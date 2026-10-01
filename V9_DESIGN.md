# V9 DESIGN — the abstraction-loss axis: when does compact representation LOSE to instance storage?

Registered: 2026-10-01 ~05:40, operator standing order "都开始" (start all
registered next steps). Status: **launched**.

## Why this axis (program logic)

Two results define the fork this experiment addresses:

1. flyloop's core law: under observation noise, structured/abstract memory
   (rule registry) beats episodic instance memory (MATCHED) by 2-4×.
2. V8-LLM (10-01): fine-tuned parametric LMs sit firmly on the abstract
   side — they refuse to replay corrupted stored instances even under
   memorization pressure.

So the abstract side always wins… in worlds where the compact form is
LOSSLESS. flyloop's affine world is exactly that: every rule IS a compact
(a, b). The registered question (from the G4′/marathon review): **when the
world makes abstraction lossy, does the ordering reverse?** The wave
machinery from V7B already implements a lossy world: observations carry a
rule-stable sinusoid `wave(x) = round(W·sin(2π(x+φ)/13))`. A compact
(a, b) prototype can never reproduce it (irreducible ±W floor), while
stored raw pairs of the SAME rule remain exactly valid across visits —
the abstraction loss is surgical: it removes exactly the information that
only instances carry.

## W9A: wave-amplitude sweep (this phase)

Four 2h runs, arms FULL / MATCHED / EPISODIC (fixed policy — adaptive is
dead per G4′ + marathon), ε = 0.15 (the J-curve optimum, cleanest filter),
same schedule/seed family as V5B-V8 runs. Two lines concurrently
(W = 0, 6), then (W = 2, 4).

| run | WAVE_AMP | role |
|---|---|---|
| w9w0 | 0 | lossless control (compare v8d15 FULL E20 1.102) |
| w9w6 | 6 | extreme lossy (mean abs wave ≈ 2.5 on p=13) |
| w9w2 | 2 | mild lossy |
| w9w4 | 4 | strong lossy |

Observations pair exactly across W values (wave does not consume probe RNG
draws; flip sequence unchanged), so paired per-(family, epoch) contrasts
and cluster bootstrap apply unchanged.

## Pre-registered predictions

- **P1 (loss floor)**: FULL RECALL E20 increases monotonically with W, and
  mechanistically: FULL's probe errors concentrate where |wave(x_p)| is
  large (post-hoc correlation; the error IS the wave — this proves the
  loss is abstraction-caused, not noise or matcher artifact).
- **P2 (crossover)**: MATCHED degrades more slowly with W than FULL
  (stored pairs stay exactly valid; the prototype never does), producing a
  crossover W* where episodic instance storage beats the registry.
  If no crossover by W = 6, register the bound and treat "abstraction
  wins everywhere" as confirmed for this world family.
- **P3 (discovery survives)**: FULL's discovery machinery still works
  under wave (WAVE_TOL = W band-gating), so the loss must show up as
  probe-time error on KNOWN rules, not as discovery failure. Watch
  discoveries/cycle ≈ flat across W as the guard.
- **Control discipline**: world shift (M3 class) — never counted as a
  self-improvement; it maps the condition surface for the NEXT system-side
  mutation (registered candidate: a registry+residual arm that stores
  per-rule wave residuals — the "abstraction compensation" mutation M5,
  only designed if P2 shows a crossover worth compensating).

## Stop / adjudication

2 h wall per run, cluster bootstrap by rule lineage, primary endpoint
RECALL E20 per arm per W; paired FULL-vs-MATCHED delta as the crossover
statistic. Adjudication script: `experiments/compare_v7.py` loaders
(arm-agnostic) + new W-pairing wrapper if needed.
