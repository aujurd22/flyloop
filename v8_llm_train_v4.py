"""V8-LLM-4: verbatim-storage emergence at extreme memorization pressure.

v3 (200 x 8ep): the model CORRECTS corrupted instances instead of replaying
them (+35pp toward truth) -- parametric storage resisted episodic behavior.
v4 pushes the pressure 10x in passes-per-instance (50 examples x 30 epochs,
concentrated corrupted answers get ~30 gradient passes each): does verbatim
episodic-like storage EMERGE when pressure is high enough?

Cells: mem_clean / mem_noise15 x seeds {42,1337}. Readouts: TRAIN50 vs
truth / vs stored / TEST500. Flyloop-episodic prediction: at sufficient
pressure verbatim replay of corrupted stored conclusions wins; v3's
correction behavior should flip. Either outcome maps the emergence
boundary of episodic behavior in parametric storage.
"""
import os, json, re, gc
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import numpy as np
import torch
from torch.utils.data import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, Trainer,
                          TrainingArguments)
from peft import LoraConfig, get_peft_model

MODEL = "Qwen/Qwen2.5-0.5B-Instruct"
OUT = os.path.join(r"D:\djr82\flyloop\runs", "v8_llm_v4")
os.makedirs(OUT, exist_ok=True)
N_TRAIN = 50
EPOCHS = 30
SEEDS = [42, 1337]

from datasets import load_dataset
ds = load_dataset("openai/gsm8k", "main")

def cot_target(ans):
    return re.sub(r"<<[^>]*>>", "", ans).strip()

def extract_answer(text):
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)", text)
    if m:
        return m.group(1).replace(",", "")
    m = re.findall(r"-?\d[\d,]*\.?\d*", text.replace(",", ""))
    return m[-1] if m else ""

train_q = ds["train"]["question"][:N_TRAIN]
train_ans = [cot_target(a) for a in ds["train"]["answer"][:N_TRAIN]]
train_truth = [extract_answer(a) for a in ds["train"]["answer"][:N_TRAIN]]
test_q = ds["test"]["question"][:500]
test_a = [extract_answer(a) for a in ds["test"]["answer"][:500]]

print("Loading tokenizer...")
tok = AutoTokenizer.from_pretrained(MODEL)
tok.pad_token = tok.eos_token
tok.padding_side = "left"

class QADataset(Dataset):
    def __init__(self, questions, answers, tok):
        self.data = []
        eos = tok.eos_token
        for q, a in zip(questions, answers):
            prompt = f"Question: {q}\nAnswer:"
            full = f"{prompt} {a}{eos}"
            p_ids = tok(prompt, add_special_tokens=False).input_ids
            f_ids = tok(full, add_special_tokens=False,
                        truncation=True, max_length=512).input_ids
            labels = list(f_ids)
            for i in range(min(len(p_ids), len(labels))):
                labels[i] = -100
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

def flip_final(cot, noise_rate, rng):
    if noise_rate <= 0:
        return cot
    m = re.search(r"####\s*(-?[\d,]+(?:\.\d+)?)\s*$", cot)
    if not m or rng.random() >= noise_rate:
        return cot
    return cot[:m.start()] + f"#### {rng.randint(1, 1000)}"

def evaluate(model, questions, truths, tag):
    model.eval()
    answers = []
    with torch.no_grad():
        for i in range(0, len(questions), 16):
            prompts = [f"Question: {q}\nAnswer:" for q in questions[i:i+16]]
            enc = tok(prompts, return_tensors="pt", padding=True,
                      truncation=True, max_length=384).to(model.device)
            out = model.generate(**enc, max_new_tokens=288, do_sample=False,
                                 pad_token_id=tok.pad_token_id,
                                 eos_token_id=tok.eos_token_id)
            for output in out:
                text = tok.decode(output, skip_special_tokens=True)
                answers.append(text.split("Answer:")[-1].strip())
    acc = sum(1 for g, t in zip(answers, truths)
              if extract_answer(g) == t) / len(questions)
    print(f"  {tag}: {acc:.3f}", flush=True)
    return acc

results = {}
for cfg in ({"name": "mem_clean", "noise": 0.0},
            {"name": "mem_noise15", "noise": 0.15}):
    for seed in SEEDS:
        name = f"{cfg['name']}_s{seed}"
        print(f"\n=== {name} (N={N_TRAIN}, epochs={EPOCHS}, "
              f"noise={cfg['noise']}) ===", flush=True)
        rng = np.random.RandomState(seed)
        t_ans = [flip_final(a, cfg["noise"], rng) for a in train_ans]
        torch.manual_seed(seed)
        train_data = QADataset(train_q, t_ans, tok)

        model = AutoModelForCausalLM.from_pretrained(
            MODEL, torch_dtype=torch.bfloat16).to("cuda")
        model = get_peft_model(model, LORA_CFG)
        model.enable_input_require_grads()
        targs = TrainingArguments(
            output_dir=os.path.join(OUT, name),
            num_train_epochs=EPOCHS,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=4,
            learning_rate=2e-4,
            warmup_steps=10,
            logging_steps=10,
            save_strategy="no", bf16=True, remove_unused_columns=False,
            dataloader_pin_memory=False, report_to="none", seed=seed)
        trainer = Trainer(model=model, args=targs, train_dataset=train_data,
                          data_collator=SimpleCollator())
        trainer.train()

        acc_train = evaluate(model, train_q, train_truth, "TRAIN50-vs-truth")
        acc_test = evaluate(model, test_q, test_a, "TEST500")
        stored_truth = [extract_answer(a) for a in t_ans]
        acc_stored = evaluate(model, train_q, stored_truth, "TRAIN50-vs-stored")

        results[name] = {"train_vs_truth": acc_train, "test500": acc_test,
                         "train_vs_stored": acc_stored}
        with open(os.path.join(OUT, f"{name}_results.json"), "w") as f:
            json.dump(results[name], f)
        del model, trainer
        gc.collect()
        torch.cuda.empty_cache()

with open(os.path.join(OUT, "all_results.json"), "w") as f:
    json.dump(results, f, indent=2)
print("\n=== All results ===")
for name, r in sorted(results.items()):
    print(f"  {name}: train_vs_truth={r['train_vs_truth']:.3f} "
          f"test500={r['test500']:.3f} train_vs_stored={r['train_vs_stored']:.3f}")
print("DONE")
