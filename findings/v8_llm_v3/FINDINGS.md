# V8-LLM-3 findings — memorization-pressure regime: parametric storage actively resists verbatim noise (the transfer boundary is located)

Run: 2026-10-01 04:45 → 05:20, Qwen2.5-0.5B-Instruct + LoRA, **first 200
GSM8K train examples × 8 epochs** (memorization pressure), 2 cells ×
2 seeds, 0 failures. Three readouts per run: recall of training instances
scored against TRUTH, against the STORED targets (corruptions included),
and held-out TEST500.

## Results (mean over seeds {42, 1337})

| cell | TRAIN200 vs truth | TRAIN200 vs stored | TEST500 |
|---|---|---|---|
| mem_clean | 42.7% | 42.7% | 32.4% |
| mem_noise15 | 41.7% | **36.5%** | 31.5% |

The regime is engaged: training-instance recall sits ~10pp above held-out
(42.7 vs 32.4). Now the decisive quantity.

## The finding: on corrupted instances the model emits the TRUTH, not the stored value

Decomposing the noise cell: stored-vs-truth differ only on the 30 corrupted
instances. The gap between the two TRAIN readouts (41.7 − 36.5 = 5.2pp over
a 15% corrupted base) means on a corrupted instance the fine-tuned model is
**~35pp more likely to produce the true answer than to reproduce the
corrupted conclusion it was actually trained on**. flyloop's episodic-side
prediction was the opposite: the MATCHED archive stores corrupted
observations and retrieves them verbatim (that is precisely why observation
noise hurts there and why read-time exactness filtering is load-bearing).

Parametric storage is not episodic storage. Gradient descent on 85%
consistent CoT patterns outvotes the 15% corrupted targets per-instance —
the LM behaves like flyloop's FULL arm endowed with a built-in
write-verification filter (the fit), i.e. **it already sits on the winning
side of the program's core law (abstraction beats episodic under noise)**.
The v2 "transfer failure" was therefore mis-framed: the laws did not fail
to transfer — the LM implements the side of the law that the laws say
should win. Episodic-side vulnerabilities (noise-propagating storage,
verbatim retrieval of corrupted entries) have no parametric counterpart at
this scale.

Caveat registered: 200 instances × 8 epochs at 0.5B tests moderate
memorization pressure; known LLM literature shows verbatim memorization
does appear at sufficient pressure (more data passes/params, fewer
instances). The claim is scoped to the regime tested; a higher-pressure
run (e.g. 50 × 30 epochs) is the registered follow-up if verbatim-storage
emergence itself becomes the question.

## The completed V8-LLM arc

| run | regime | question | verdict |
|---|---|---|---|
| 1 | direct-answer, n=100 | does anything transfer? | unmeasurable (floored at 3-6%) |
| 2 | CoT, generalization, 2 seeds | does the noise/depth law transfer? | no; any effect ≤ ~3pp vs flyloop's 2-4× relative |
| 3 | memorization pressure | does the law reappear when instances must be stored? | no — parametric storage actively corrects corrupted instances instead of replaying them |

Bottom line for the Mushroom-Body program: the toy-world condition laws
bind to **episodic/instance-addressable memory systems** (flyloop's
MATCHED/EPI arms and the registry's write/read filtering). Fine-tuned
parametric models are not that kind of system — they are the abstraction
side. Any attempt to improve LLM fine-tuning by importing episodic-memory
findings must first ask whether the target behavior is instance-addressable
at all; for benchmark-style generalization it is not.
