# V8-LLM-2 findings — the transfer test at generalization regime: flyloop effects do NOT transfer (decisively bounded)

Run: 2026-10-01 00:20 → 04:35, RTX 4070 SUPER, Qwen2.5-0.5B-Instruct + LoRA
(r=16, q/v_proj), GSM8K **CoT targets** (annotations stripped, "#### N" kept),
6748 train examples, 4 cells × 2 seeds, fresh base+LoRA per run, eval n=500
test questions (extraction prefers the "#### N" slot). 8/8 runs, 0 failures.
Adapters + per-run loss curves saved (runs/v8_llm_v2/).

## Results (test accuracy, mean over seeds {42, 1337})

| cell | epochs | label noise | s42 | s1337 | mean |
|---|---|---|---|---|---|
| standard | 3 | 0 | 34.0% | 34.2% | **34.1%** |
| noise15 | 3 | 0.15 | 32.2% | 34.6% | 33.4% |
| shallow1ep | 1 | 0 | 33.8% | 34.8% | **34.3%** |
| shallow1ep_noise15 | 1 | 0.15 | 32.6% | 32.0% | 32.3% |

(For scale: run 1's direct-answer training floored at 3-6%; CoT targets
lifted the readout into a range where effects are measurable.)

## Verdict: no flyloop effect survives the transfer, at any detectable magnitude

All four cells sit in a 2-point band (32.3-34.3%) and **within-cell seed
spread (up to 2.4pp) is the same size as every cell difference**. The
specific flyloop analogues:

- **Moderate-noise benefit** (flyloop: ε=0.05-0.15 is 4× BETTER than ε=0):
  absent. 15% corrupted stored conclusions move test accuracy by −0.7pp at
  3 epochs, −2.0pp at 1 epoch — noise is if anything mildly harmful, never
  helpful.
- **Shallow-beats-deep under noise** (flyloop: −0.655, CI excl. 0): absent;
  the noisy 1-epoch cell is nominally the WORST (32.3%), opposite sign.
- **Any depth effect at all**: 1 epoch ≈ 3 epochs (34.3 vs 34.1) — the
  model extracts everything GSM8K offers in one pass.

Power: flyloop effects are 2-4× RELATIVE (E20 doubling or halving; the
equivalent here would be 34% → 17% or 68%). We can bound any true effect at
≤ ~3pp (~9% relative) — an order of magnitude below the flyloop scale.
**The null is decisive, not underpowered** (unlike run 1).

## Registered reading: the flyloop condition law locates the boundary

flyloop's three-condition law (support × write-depth × observation noise)
was derived in a regime where specific observations must be STORED and
RETRIEVED (small memory, instance identity matters, exact-match read).
A 0.5B LM fine-tune on 6.7k instances GENERALIZES: parameter sharing
absorbs 15% corrupted targets, test questions are novel, and there is no
instance retrieval at test time for noise to corrupt. The transfer
prediction this generates is registered and TESTED in V8-LLM-3
(v8_llm_train_v3.py, running): under memorization pressure (200 examples ×
8 epochs, eval on the training instances themselves) the flyloop laws
should REAPPEAR — corrupted stored conclusions should be reproduced
verbatim if parametric storage behaves like episodic memory. If they do,
the boundary is located between storage-dominated and generalization-
dominated regimes; if they do not, parametric storage is noise-robust in a
way episodic memory is not — either outcome is a clean statement.

## Engineering deposits

Fresh-weights-per-config + smoke gate carried over from run 1 and reused
unchanged; 8 runs × (~12 min train + ~8 min eval) with zero intervention.
Per-run loss curves saved with results. One launch footgun: the nohup log
redirect requires the output directory to exist BEFORE the shell redirect
(silent death otherwise).
