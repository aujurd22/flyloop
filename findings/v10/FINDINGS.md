# V10 findings — the composite world: composition transfer real, periodicity refutes the episodic-win prediction (drift punishes both architectures)

Run: 2026-10-01 21:17 → 23:18, FLYLOOP_COMPOSITE=1, ε=0.25, arms FULL /
MATCHED / EPISODIC (the user's A/B/C), 5418 cycles, 0 failures.
SDB-aligned (P148): COMPRESSION=ICR, TRANSFER=composition probes,
SURPRISE=anomaly class. Adjudication data: `v10_adjudication.txt`.

## Headline results (RECALL E20 by rule type)

| type | FULL (registry) | MATCHED (archive) | EPISODIC |
|---|---|---|---|
| standard (fam 0,3) | **3.864** | 5.773 | 5.864 |
| **composite (fam 2)** | **1.333** | 5.222 | 5.333 |
| **periodic (fam 1)** | 6.154 | 6.846 | 6.846 |

## P2 CONFIRMED (composition transfer is real)

- Composite RECALL E20: **FULL 1.333 vs MATCHED 5.222 / EPISODIC 5.333** —
  the registry's largest per-type win in program history (4× better than
  the archive).
- FULL's composite RECALL **probe-1 hit rate: 5/9 = 56%** vs 7.7% random —
  hits on the FIRST probe of a rule whose parameters are derivable from
  its two predecessor rules. n=9 (wide CI), but 7× random is hard to
  dismiss: the registry answers unobserved structure from stored
  composition. SDB TRANSFER, mechanical, in-loop.

## P1 REFUTED — and the refutation is the finding

The prediction "periodicity favors the archive" is wrong: on periodic
rules FULL 6.154 ≈ MATCHED 6.846 ≈ EPISODIC 6.846 — **both memory
architectures lose ~2.3 E20 to their standard-family performance**.
The mechanism prediction missed: I assumed the archive's exact replay
would carry the drift. It cannot — a stored pair from visit k carries
b_k, and visit k+1 presents b_{k+1}; **drift breaks the archive's
temporal-invariance assumption exactly as it breaks the registry's
compact form**. Registered law sharpened: *drift (temporal
non-invariance) is the abstraction-loss type that punishes BOTH
architecture families; neither (a,b) nor instance replay carries
(b0, δ, k) — the missing representation is the delta itself.*
Registered V10b: give the registry a δ field (one mutation, M6) — can it
LEARN to store drift when the slot exists?

## P3 (anomaly/hallucination) — error side measured, memorization side pending

All arms err ~89-90% on the 97 anomaly probes each (the outlier is
unpredictable by design — correct behavior). The registered metric
(anomaly-episode memorization: book/archive writes charged at anomaly
episodes) needs an events-side join not yet implemented; queued for
V10b. No arm collapsed on anomaly handling.

## P4 (ICR) — plumbing broken, deferred

The coarse ICR read failed (counts key mismatch: per-arm stored-bytes
tracking is incomplete in state.json). Registered: add per-arm
observation-byte accounting to the worker (one counter), recompute ICR
for W9*/V10 runs retroactively — events.jsonl has everything needed.

## For the program

1. The user's direction-3 closed loop works: the A/B/C arms separate
   cleanly by regularity TYPE in a single run — composition is the
   registry's killer feature (1.33), standard is its normal win (3.86 vs
   5.8), periodicity is nobody's friend (6.2/6.8/6.8).
2. With P148's SDB (three domains, LLM-judged) and V10 (in-loop,
   mechanical), the benchmark layer of the Mushroom-Body program exists
   in both flavors and agrees on the metric vocabulary.
3. Registered next: V10b (δ-field mutation M6, anomaly-memorization
   join, ICR counters) and W9D replication adjudication (M5's
   "accepted" decision).
