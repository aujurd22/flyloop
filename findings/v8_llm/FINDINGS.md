# V8-LLM findings — pipeline validated, adjudication UNDERPOWERED (no transfer claim)

Run: 2026-09-30 22:33 → 23:20, RTX 4070 SUPER, Qwen2.5-0.5B-Instruct + LoRA
(r=16, q_proj/v_proj), GSM8K direct-answer targets, 6748 train examples,
4 configs × fresh base weights, eval n=100 test questions each.

## Results (test accuracy, exact match on final number)

| config | epochs | label noise | acc | correct/100 |
|---|---|---|---|---|
| standard | 3 | 0 | **6%** | 6 |
| noise15 | 3 | 0.15 | 3% | 3 |
| shallow1ep | 1 | 0 | 3% | 3 |
| shallow1ep_noise15 | 1 | 0.15 | 3% | 3 |

**No contrast is significant at n=100** (6/100 vs 3/100: binomial p ≈ 0.31;
three of four cells sit at the 3% floor). The honest verdict: this run
CANNOT adjudicate whether flyloop's noise/write-depth findings transfer to
LLM fine-tuning — neither CONFIRMED nor REFUTED.

## Why the readout is floor-compressed

Direct-answer training (target = the bare number, no chain-of-thought) is
the closest analogue to flyloop's memorize-a-label condition, but it caps a
0.5B model near single digits on GSM8K: multi-step arithmetic in one forward
pass. With all cells between 3-6%, effect compression + n=100 makes the 2×2
uninformative. The untrained base model under the same protocol extracts
numbers from truncated CoT rambles at a comparable rate — training lifted
the ceiling by only a few points.

## What this run DID establish (engineering, all reusable)

1. **Fresh-weights-per-config discipline**: the first draft shared one LoRA
   model across all 4 configs — config 2 would have started from config 1's
   weights, silently destroying the factorial. Fixed: each config reloads
   base + fresh LoRA (verified: identical loss curves for identical
   smoke configs).
2. **Smoke gate**: V8_SMOKE=1 (300 examples, 1 epoch, 16-question eval)
   validates train → eval → save → reload end-to-end in ~2 min before any
   multi-hour commitment.
3. **HF Dataset access**: `ds[:n]` yields a dict of COLUMNS, not a list of
   examples — column access (`ds["question"][:n]`) is the only safe form.
   (The original crash: `for x in test_ds[:100]` iterated column NAMES.)
4. EOS-supervised targets make greedy eval terminate (max_new_tokens=48
   instead of 256); per-config results written immediately (crunch-survivable).

## Registered follow-up (V8-LLM-2, NOT launched — needs operator call)

For a decisive transfer test the design must move the readout off the floor:

1. **CoT targets** (strip `<<..>>` annotations, keep reasoning + `#### N`):
   lifts 0.5B GSM8K to the 20-35% band where contrasts are visible.
2. **Full test eval** (n=1319, SE ≈ 1.3-2 pp) and **save checkpoints** so
   eval can be re-run/enlarged post hoc.
3. **≥2 seeds per cell** (run-level seed varies data order + noise draws)
   with a cluster bootstrap on the 2×2 contrasts.
4. Same four cells; predictions unchanged from the flyloop analogy:
   deep+noise worst; shallow+noise ≥ deep+noise (fewer updates = less
   noise memorization); moderate noise on CLEAN data ≥ 0 noise (the ε=0.15
   dose-response bump is the boldest transfer target).

Cost estimate: CoT targets ~3× tokens → 3-epoch configs ≈ 30-40 min each on
the 4070 SUPER; full run ≈ 2.5-3 h including eval.
