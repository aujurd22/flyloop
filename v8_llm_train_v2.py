"""V8-LLM-2: the powered transfer test (follow-up to the underpowered run 1).

Changes vs v1 (registered in findings/v8_llm/FINDINGS.md):
1. CoT targets (strip <<..>> calculator annotations, keep reasoning + "#### N")
   -- moves the readout off the 3-6% direct-answer floor.
2. Eval n=500 test questions, extraction prefers the "#### N" slot.
3. 2 seeds per cell (noise draw + data order + LoRA init), 8 runs total.
4. Adapters saved per run (post-hoc re-eval possible); per-run loss curves kept.

Theory frame (sharper than v1): flyloop's noise law says the noise filter
lives at READ time (strict argmax / exact-reproduction fallback), not write
time. A plain LM fine-tune has NO read-time filter, so the flyloop prediction
is that the moderate-noise benefit does NOT transfer: label noise should be
monotonically harmful here. The 2x2 (epochs x noise) tests exactly that.

Cells: standard(3ep,clean) / noise15(3ep,eps=.15) / shallow1ep(1ep,clean)
       / shallow1ep_noise15(1ep,eps=.15), seeds {42,1337}.
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
OUT = os.path.join(r"D:\djr82\flyloop\runs", "v8_llm_v2")
os.makedirs(OUT, exist_ok=True)
SEEDS = [42, 1337] if not SMOKE else [42]

from datasets import load_dataset
ds = load_dataset("openai/gsm8k", "main")
train_ds, test_ds = ds["train"], ds["test"]

def cot_target(ans):
    """GSM8K answer -> clean CoT target: drop <<..>> calculators, keep
    reasoning + the '#### N' final line."""
    return re.sub(r"<<[^>]*>>", "", ans).strip()

def extract_answer(text):
    """Prefer the '#### N' slot; fallback to the last number in the text."""
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")
    m = re.findall(r"-?\d[\d,]*\.?\d*", text.replace(",", ""))
    return m[-1] if m else ""

train_q = train_ds["question"]
train_ans = [cot_target(a) for a in train_ds["answer"]]
N_EVAL = 16 if SMOKE else 500
test_q = test_ds["question"][:N_EVAL]
test_a = [extract_answer(a) for a in test_ds["answer"][:N_EVAL]]

if SMOKE:
    train_q, train_ans = train_q[:300], train_ans[:300]

def flip_final_answer(cot, noise_rate, rng):
    """Label noise: with prob noise_rate replace the #### number (the stored
    conclusion) with a random one, leaving the reasoning intact -- the
    analogue of flyloop's corrupted revealed observation."""
    if noise_rate <= 0:
        return cot
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)\s*$", cot)
    if not m or rng.random() >= noise_rate:
        return cot
    return cot[:m.start()] + f"#### {rng.randint(1, 1000)}"

print("Loading tokenizer...")
tok = AutoTokenizer.from_pretrained(MODEL)
tok.pad_token = tok.eos_token
tok.padding_side = "left"

class QADataset(Dataset):
    """Tokenized once per (seed, noise) variant; drops over-length examples
    (truncation would cut the '#### N' line off the supervision)."""
    def __init__(self, questions, answers, tok, seed, noise_rate, max_len=512):
        rng = np.random.RandomState(seed)
        self.data = []
        dropped = 0
        eos = tok.eos_token
        for q, a in zip(questions, answers):
            a = flip_final_answer(a, noise_rate, rng)
            prompt = f"Question: {q}\nAnswer:"
            full = f"{prompt} {a}{eos}"
            p_ids = tok(prompt, add_special_tokens=False).input_ids
            f_ids = tok(full, add_special_tokens=False,
                        truncation=True, max_length=max_len).input_ids
            if len(f_ids) >= max_len and len(tok(full, add_special_tokens=False).input_ids) > max_len:
                dropped += 1
                continue
            labels = list(f_ids)
            for i in range(min(len(p_ids), len(labels))):
                labels[i] = -100
            self.data.append({"input_ids": torch.tensor(f_ids),
                              "labels": torch.tensor(labels)})
        self.dropped = dropped

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

def fresh_model(seed):
    torch.manual_seed(seed)
    m = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.bfloat16).to("cuda")
    m = get_peft_model(m, LORA_CFG)
    m.enable_input_require_grads()
    return m

# cache datasets per variant: (seed, noise) -> QADataset
_cache = {}
def get_dataset(seed, noise):
    key = (seed, noise)
    if key not in _cache:
        _cache[key] = QADataset(train_q, train_ans, tok, seed, noise)
        print(f"  dataset seed={seed} noise={noise}: "
              f"{len(_cache[key])} kept, {_cache[key].dropped} dropped(>512)",
              flush=True)
    return _cache[key]

configs = [
    {"name": "standard", "epochs": 3, "noise": 0.0},
    {"name": "noise15", "epochs": 3, "noise": 0.15},
    {"name": "shallow1ep", "epochs": 1, "noise": 0.0},
    {"name": "shallow1ep_noise15", "epochs": 1, "noise": 0.15},
] if not SMOKE else [
    {"name": "smoke_noise15", "epochs": 1, "noise": 0.15},
]

results = {}
for cfg in configs:
    for seed in SEEDS:
        name = f"{cfg['name']}_s{seed}"
        print(f"\n=== Training: {name} (epochs={cfg['epochs']}, "
              f"noise={cfg['noise']}, seed={seed}) ===", flush=True)
        train_data = get_dataset(seed, cfg["noise"])
        bs = 2 if SMOKE else 4
        targs = TrainingArguments(
            output_dir=os.path.join(OUT, name),
            num_train_epochs=cfg["epochs"],
            per_device_train_batch_size=bs,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            warmup_steps=20 if SMOKE else 50,
            logging_steps=10 if SMOKE else 40,
            save_strategy="no",
            bf16=True,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
            report_to="none",
            seed=seed,
        )
        model = fresh_model(seed)
        trainer = Trainer(model=model, args=targs, train_dataset=train_data,
                          data_collator=SimpleCollator())
        trainer.train()

        model.eval()
        gen_answers = []
        with torch.no_grad():
            for i in range(0, len(test_q), 16):
                prompts = [f"Question: {q}\nAnswer:" for q in test_q[i:i+16]]
                enc = tok(prompts, return_tensors="pt", padding=True,
                          truncation=True, max_length=384).to(model.device)
                out = model.generate(**enc, max_new_tokens=288,
                                     do_sample=False,
                                     pad_token_id=tok.pad_token_id,
                                     eos_token_id=tok.eos_token_id)
                for output in out:
                    text = tok.decode(output, skip_special_tokens=True)
                    gen_answers.append(text.split("Answer:")[-1].strip())

        correct = sum(1 for g, t in zip(gen_answers, test_a)
                      if extract_answer(g) == t)
        acc = correct / len(test_q)
        results[name] = {"accuracy": acc, "correct": correct,
                         "total": len(test_q),
                         "loss_history": [h.get("loss") for h in trainer.state.log_history
                                          if "loss" in h]}
        print(f"  {name}: accuracy = {acc:.3f} ({correct}/{len(test_q)})",
              flush=True)
        with open(os.path.join(OUT, f"{name}_results.json"), "w") as f:
            json.dump(results[name], f)
        model.save_pretrained(os.path.join(OUT, f"{name}_adapter"))

        del model, trainer
        gc.collect()
        torch.cuda.empty_cache()

with open(os.path.join(OUT, "all_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print("\n=== All results ===")
for name, r in sorted(results.items()):
    print(f"  {name}: accuracy={r['accuracy']:.3f}")
print("DONE")
