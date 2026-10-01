# V10 DESIGN — the composite world: periodicity + anomaly + composition in one three-arm closed loop

Registered: 2026-10-01 evening (operator directive: flyloop custody; user
direction 3 — "把 Flyloop 接进来"). Status: IMPLEMENTING.

## Alignment with SDB (intuition-mechanism P148/P148-b/P149)

P148's own NEXT directive names this experiment ("the Flyloop A/B/C memory
experiment ... would close the Mushroom-Body loop"), and its metric
vocabulary is adopted here so the two repos measure the same thing:

| SDB metric (P148) | V10 in-loop operationalization |
|---|---|
| COMPRESSION (mdl_ratio = bits(obs)/bits(rule)) | ICR: observation bytes consumed / memory bytes stored, per arm |
| TRANSFER (accuracy on structurally-identical different-carrier probes) | composition probes: answer composite R3 = (a1+a2, b1−b2) before ANY R3 episode is observed — transfer across carrier |
| SURPRISE (detect the structure class the charter omits) | anomaly probes (3%, outlier generator, never named): detection = refusal without memorization |

V10 adds what SDB cannot have: the mechanism under test is a MEMORY
ARCHITECTURE (three arms), running mechanically in-loop — no LLM judge,
unlimited n, and the discovery process is observable per cycle.

## What already exists (so the design only adds what's missing)

The user's proposed A/B/C closed loop is flyloop's standing architecture:

| user's label | flyloop arm | memory substrate |
|---|---|---|
| A 普通 episodic memory | EPISODIC | fit-only pads, no memory of rules |
| B FlyMemory | MATCHED | episodic pair-table archive (FlyMemory instances) |
| C 规则压缩 memory | FULL | compressed rule registry (the RULEBOOK) |

## The three regularity types (new world layer, env `FLYLOOP_COMPOSITE=1`)

1. **Periodic rules (periodicity)**: family-1 rules drift deterministically
   with visit count: b_k = b_0 + δ·k mod 13 (δ ∈ {1,2,3} from the schedule
   seed) at their k-th episode. The compact form (a, b) is insufficient —
   it must be (a, b_0, δ, k). Registered honestly: the registry cannot
   store δ today, so P1 tests the STORAGE mismatch, not discovery failure;
   the analysis separates the two.
2. **Anomaly probes (anomaly)**: p_anom = 3% of probes (all families) draw
   both the revealed pair and the truth from an outlier generator. Logged
   per-probe (`anomaly` flag in events); the memory-side question is
   whether the arm MEMORIZES the anomaly (book/archive writes at anomaly
   episodes = hallucinated structure).
3. **Composite rules (composition)**: family-2 rules with index ≥2 derive
   deterministically from the family's own earlier rules:
   R_i = (a_{i-2} + a_{i-1}, b_{i-2} − b_{i-1}). Registry-side inference:
   hold R1, R2 → derive R3 without observing it. Probe-1 hits on composite
   rules before any R3 episode completes = mechanical transfer.

## Pre-registered predictions (SDB-aligned)

- P1 (periodicity — the first predicted episodic win): on periodic-rule
  RECALL probes, MATCHED ≤ FULL error — the archive's instance memory
  carries the drift the registry's compact form cannot.
- P2 (composition — the registry's inference advantage): FULL answers
  composite probe-1s before any R3 episode completes (composition
  transfer); MATCHED cannot (must observe R3's instances).
- P3 (surprise/hallucination boundary): anomaly-memorization rate
  FULL < MATCHED; anomaly-probe error is high for ALL arms (the outlier
  is unpredictable) — the metric is what gets STORED, not what gets
  answered.
- P4 (compression-accuracy law per type): standard/composite types favor
  the registry (V9's lossless regime); the periodic type bends the
  E20-vs-ICR curve toward the archive — the "abstraction advantage
  radius" made type-specific.

## Concurrency (2026-10-01)

V10 implementation proceeds while W9C runs — Python modules are imported
at worker start, so edits do not touch the running process; the only
hazard is a W9C worker crash-respawn loading a half-edited file, managed
by import-checking after every edit. Launch concurrent with W9C if RAM
≥ 8 GB free, else queued behind the W9C watchdog.

## Design discipline

- World shift, not a system mutation (M3 class): three standard arms, no
  new capability.
- Seeds: schedule keys (rule params, δ, derivation) stay on C.SEED so
  episodes pair across arms/runs; anomaly draws and probe realizations
  read C.RUN_SEED (post-G4 split discipline).
- 2 h per run, three arms, paired per-(family, epoch) contrasts; fam 0
  stays fully standard as the within-run control.

## Relation to the user's five directions

| direction | flyloop custody status |
|---|---|
| 1 ICR | defined above, computable from existing runs (baseline first) |
| 2 benchmark (compression/transfer/surprise) | covered by SDB (P148/P148-b/P149); V10 adopts its metric vocabulary in-loop |
| 3 closed loop with flyloop | THIS document |
| 4 insight vs hallucination | anomaly-memorization rate + stale intrusions (in-loop, mechanical) |
| 5 active exploration / curiosity loop | out of flyloop custody for now (needs a proposal lane; registered as the V11 candidate) |
