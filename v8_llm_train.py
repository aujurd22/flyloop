"""V8-LLM: Test whether flyloop findings transfer to real LLM fine-tuning.

Findings to test:
1. Moderate noise is optimal (eps=0.15 best) -> train with 15% label noise
2. Shallow beats deep (1 epoch > 3 epochs) -> train for 1 epoch only

Model: Qwen2.5-0.5B-Instruct (0.5B params, LoRA on q_proj/v_proj)
Data: GSM8K (math word problems, verifiable answers)
Eval: GSM8K test accuracy (exact match on final number)

Design rules (hard-won):
- Each config reloads FRESH base weights + fresh LoRA (never reuse a trained
  model across configs -- that turns a 2x2 factorial into a cumulative run).
- HF Dataset slicing ds[:n] yields a dict of COLUMNS, not a list of examples.
  Access columns directly: ds["question"][:n].
- Smoke mode first (V8_SMOKE=1): tiny subset, validates train->eval->save
  end-to-end before committing hours to the full run.
"""
import os, sys, json, re, gc
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                          TrainingArguments)
from peft import LoraConfig, get_peft_model

SMOKE = os.environ.get("V8_SMOKE", "0") == "1"
MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
OUT = os.path.join(r"D:\djr82\flyloop\runs", "v8_llm")
os.makedirs(OUT, exist_ok=True)

from datasets import load_dataset
ds = load_dataset("openai/gsm8k", "main")
train_ds = ds["train"]  # 7473 examples
test_ds = ds["test"]    # 1319 examples

def extract_answer(text):
    """Extract final number from GSM8K answer."""
    m = re.findall(r"-?\d[\d,]*\.?\d*", text.replace(",", ""))
    return m[-1] if m else ""

# Column access, NOT list-comprehension over a slice (slice -> dict of cols)
train_q = train_ds["question"]
train_ans = train_ds["answer"]
test_q_all = test_ds["question"]
test_a_all = [extract_answer(a) for a in test_ds["answer"]]

if SMOKE:
    train_q, train_ans = train_q[:300], train_ans[:300]
    N_TEST = 16
else:
    N_TEST = 100
test_q = test_q_all[:N_TEST]
test_a = test_a_all[:N_TEST]

# Bare-number targets (direct answer, no CoT): closest analogue to flyloop's
# memorize-label condition; label noise then attacks exactly the memorized map.
clean_ans = []
for a in train_ans:
    m = re.findall(r"-?\d[\d,]*\.?\d*", a.replace(",", ""))
    clean_ans.append(m[-1] if m else a)

def add_noise(labels, noise_rate, seed=42):
    rng = np.random.RandomState(seed)
    noisy = list(labels)
    for i in range(len(noisy)):
        if rng.random() < noise_rate:
            noisy[i] = str(rng.randint(1, 1000))
    return noisy

# ---- Tokenizer (load once) ----
print("Loading tokenizer...")
tok = AutoTokenizer.from_pretrained(MODEL)
tok.pad_token = tok.eos_token
tok.padding_side = "left"  # correct positions for batched generate

class QADataset(Dataset):
    def __init__(self, questions, answers, tok, max_len=384):
        self.data = []
        eos = tok.eos_token
        for q, a in zip(questions, answers):
            prompt = f"Question: {q}\nAnswer:"
            full = f"{prompt} {a}{eos}"
            p_ids = tok(prompt, add_special_tokens=False).input_ids
            f_ids = tok(full, add_special_tokens=False, truncation=True,
                        max_length=max_len).input_ids
            labels = list(f_ids)
            for i in range(min(len(p_ids), len(labels))):
                labels[i] = -100  # mask prompt, supervise answer + EOS
            self.data.append({"input_ids": torch.tensor(f_ids),
                              "labels": torch.tensor(labels)})
    def __len__(self):
        return len(self.data)
    def __getitem__(self, idx):
        return self.data[idx]

class SimpleCollator:
    def __call__(self, features):
        max_len = max(f["input_ids"].shape[0] for f in features)
        batch = {"input_ids": [], "labels": [], "attention_mask": []}
        for f in features:
            ids, lab = f["input_ids"], f["labels"]
            pad = max_len - ids.shape[0]
            batch["input_ids"].append(
                torch.nn.functional.pad(ids, (0, pad), value=tok.pad_token_id))
            batch["labels"].append(
                torch.nn.functional.pad(lab, (0, pad), value=-100))
            batch["attention_mask"].append(
                torch.nn.functional.pad(torch.ones_like(ids), (0, pad), value=0))
        return {k: torch.stack(v) for k, v in batch.items()}

LORA_CFG = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"],
                      lora_dropout=0.05, bias="none", task_type="CAUSAL_LM")

def fresh_model():
    """Reload base weights + fresh LoRA. NEVER share a trained model across
    configs -- config 2 would start from config 1's weights."""
    m = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.bfloat16).to("cuda")
    m = get_peft_model(m, LORA_CFG)
    m.enable_input_require_grads()
    return m

# ---- Pre-tokenize data variants ONCE (reused across configs) ----
print("Tokenizing datasets...")
split = int(0.9 * len(train_q))
tr_q, val_q = train_q[:split], train_q[split:]
tr_a_clean = clean_ans[:split]
DATA_CLEAN = QADataset(tr_q, tr_a_clean, tok)
DATA_NOISY = QADataset(tr_q, add_noise(tr_a_clean, 0.15), tok)
print(f"  clean={len(DATA_CLEAN)} noisy={len(DATA_NOISY)} examples")

if SMOKE:
    configs = [
        {"name": "smoke_noise15", "epochs": 1, "noise": 0.15},
        {"name": "smoke_shallow1ep_noise15", "epochs": 1, "noise": 0.15},
    ]
else:
    configs = [
        {"name": "standard", "epochs": 3, "noise": 0.0},
        {"name": "noise15", "epochs": 3, "noise": 0.15},
        {"name": "shallow1ep", "epochs": 1, "noise": 0.0},
        {"name": "shallow1ep_noise15", "epochs": 1, "noise": 0.15},
    ]

results = {}
for ci, cfg in enumerate(configs):
    name = cfg["name"]
    print(f"\n=== [{ci+1}/{len(configs)}] Training: {name} "
          f"(epochs={cfg['epochs']}, noise={cfg['noise']}) ===", flush=True)
    torch.manual_seed(42)
    np.random.seed(42)

    train_data = DATA_NOISY if cfg["noise"] > 0 else DATA_CLEAN
    bs = 2 if SMOKE else 4
    training_args = TrainingArguments(
        output_dir=os.path.join(OUT, name),
        num_train_epochs=cfg["epochs"],
        per_device_train_batch_size=bs,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        warmup_steps=20 if SMOKE else 50,
        logging_steps=10 if SMOKE else 20,
        save_strategy="no",
        bf16=True,
        remove_unused_columns=False,
        dataloader_pin_memory=False,
        report_to="none",
    )

    model = fresh_model()
    trainer = Trainer(model=model, args=training_args,
                      train_dataset=train_data, data_collator=SimpleCollator())
    trainer.train()

    # Evaluate
    model.eval()
    gen_answers = []
    with torch.no_grad():
        for i in range(0, len(test_q), 8):
            batch_q = test_q[i:i+8]
            prompts = [f"Question: {q}\nAnswer:" for q in batch_q]
            enc = tok(prompts, return_tensors="pt", padding=True,
                      truncation=True, max_length=256).to(model.device)
            out = model.generate(**enc, max_new_tokens=48, do_sample=False,
                                 pad_token_id=tok.pad_token_id,
                                 eos_token_id=tok.eos_token_id)
            for output in out:
                text = tok.decode(output, skip_special_tokens=True)
                gen_answers.append(text.split("Answer:")[-1].strip())

    correct = sum(1 for g, t in zip(gen_answers, test_a)
                  if extract_answer(g) == t)
    accuracy = correct / len(test_q)
    results[name] = {"accuracy": accuracy, "correct": correct,
                     "total": len(test_q)}
    print(f"  {name}: accuracy = {accuracy:.3f} ({correct}/{len(test_q)})",
          flush=True)

    # Per-config result saved IMMEDIATELY (survives a later crash)
    with open(os.path.join(OUT, f"{name}_results.json"), "w") as f:
        json.dump(results[name], f)

    del model, trainer
    gc.collect()
    torch.cuda.empty_cache()

with open(os.path.join(OUT, "all_results.json"), "w") as f:
    json.dump(results, f, indent=2)

print("\n=== All results ===")
for name, r in results.items():
    print(f"  {name}: accuracy={r['accuracy']:.3f}")
print("DONE")
