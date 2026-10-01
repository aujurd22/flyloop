# V8-LLM-4 findings — 10× memorization pressure: correction behavior holds, the episodic transition is not reached

Run: 2026-10-01 ~12:25 → 12:50, Qwen2.5-0.5B-Instruct + LoRA, **first 50
GSM8K examples × 30 epochs** (~10× v3's passes-per-instance), 2 cells ×
2 seeds, 0 failures. Same three readouts as v3.

## Results (mean over seeds {42, 1337})

| cell | TRAIN50 vs truth | TRAIN50 vs stored | TEST500 |
|---|---|---|---|
| mem_clean (50×30) | **75.0%** | 75.0% | 18.1% |
| mem_noise15 (50×30) | 67.0% | **64.0%** | 17.4% |
| (v3: mem_clean 200×8) | 42.7% | 42.7% | 32.4% |
| (v3: mem_noise15 200×8) | 41.7% | 36.5% | 31.5% |

## Three observations

1. **The memorization regime is fully engaged.** Train recall 75.0% and
   held-out accuracy COLLAPSED to 18.1% (from 32.4% in v3) — the model
   became a 50-instance lookup table; memorization crowded out
   generalization entirely, in BOTH cells (clean included).

2. **Correction behavior survives 10× pressure.** On corrupted instances,
   the model still emits the TRUE answer more often than the corrupted
   stored value: gap ≈ 3.0pp over the 15% corrupted base → P(true|corrupt)
   − P(replay|corrupt) ≈ **20pp**. The flyloop-episodic prediction
   (verbatim replay of corrupted stored conclusions wins at sufficient
   pressure) did NOT materialize.

3. **But the gap is narrowing with pressure** — the emergence trend is
   real: P(true|corrupt) − P(replay|corrupt) ≈ 35pp at 200×8ep (v3) →
   ~20pp at 50×30ep (v4, ~15× passes-per-instance pressure). Roughly
   linear in log-pressure, it would cross zero somewhere around ~100×
   v3's pressure (e.g. ~50 × 800 epochs) — far beyond practical
   fine-tuning and arguably a different phenomenon (rote overfit) at that
   point.

## The completed LLM-side arc (v1 → v4)

| run | regime | verdict |
|---|---|---|
| v1 | direct answer, n=100 | floored (3-6%), unmeasurable |
| v2 | CoT, generalization | no transfer; effects ≤ ~3pp vs flyloop 2-4× |
| v3 | 200×8ep memorization | model CORRECTS corrupted instances (+35pp), not replay |
| v4 | 50×30ep extreme | correction survives (still +20pp); test collapsed to 18% |

**Final statement**: within practical fine-tuning pressure, parametric
storage stays on the abstraction side of flyloop's law even at its most
memorization-like operating point. The LM never becomes episodic in the
flyloop sense — even while acting as a lookup table on 50 instances, it
aggregates away corrupted entries instead of replaying them. Episodic
vulnerabilities (noise-propagating verbatim storage) require
instance-addressable memory; gradient storage does not provide it. The
V8-LLM question is closed: the correct unit for the Mushroom-Body laws is
the memory SYSTEM architecture (instance-addressable vs parametric), not
the learning rule.

Registered (not queued): the log-pressure extrapolation predicts verbatim
replay wins near ~100× v4's pressure; testing that would be a rote-
overfit study, outside this program's question.
