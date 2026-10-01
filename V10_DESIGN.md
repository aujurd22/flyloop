# V10 DESIGN — the composite world: periodicity + anomaly + composition in one three-arm closed loop

Registered: 2026-10-01 evening (operator directive: flyloop custody; user
direction 3 — "把 Flyloop 接进来"). Status: DESIGNED, implementation next.

## What already exists (so the design only adds what's missing)

The user's proposed A/B/C closed loop is flyloop's standing architecture:

| user's label | flyloop arm | memory substrate |
|---|---|---|
| A 普通 episodic memory | EPISODIC | fit-only pads, no memory of rules |
| B FlyMemory | MATCHED | episodic pair-table archive (FlyMemory instances) |
| C 规则压缩 memory | FULL | compressed rule registry (the RULEBOOK) |

What V3-V9 measured on it: RECALL E20, discovery counts, stale intrusions —
in a world where every rule is ONE affine map (a, b) mod 13. What the
user's direction asks for and V10 adds: **a world whose hidden structure
mixes three regularity TYPES**, and metrics that measure discovery as a
process (speed, compression ratio, hallucination boundary), not just
accuracy.

## The three regularity types (new world layer, env `FLYLOOP_COMPOSITE=1`)

1. **Periodic rules (periodicity)**: a rule whose offset drifts
   deterministically with visit count: b_k = b_0 + δ·k mod 13 at its k-th
   episode. Prediction requires remembering the VISIT HISTORY — the
   compact form (a, b) is now INSUFFICIENT (it must be (a, b_0, δ, k)):
   instance memory gains a native advantage for the first time in the
   program.
2. **Anomaly probes (anomaly)**: with probability p_anom = 3%, a probe's
   truth is drawn from an outlier generator unrelated to any rule. The
   correct behavior is REFUSAL (or one-off fit), NOT memorization.
   Storing the anomaly as a rule is the in-loop definition of
   hallucinated structure.
3. **Composite rules (composition)**: a rule whose parameters are a
   deterministic function of two other rules: R3 = (a1 + a2, b1 − b2).
   R3's episodes appear only AFTER R1 and R2 are discoverable. A registry
   that holds R1, R2 can infer R3's parameters WITHOUT observing it; an
   archive must store R3's instances from scratch. Discovery-from-
   composition is the process under test.

## Pre-registered metrics (the user's three, made mechanical)

- **Discovery speed**: first-DISCOVERY cycle per rule type, per arm
  (already logged as insight events; V10 reports it as the endpoint).
- **ICR (Insight Compression Ratio)**: total raw observation bytes the arm
  consumed / bytes of its stored memory. Registered expectation: ICR is
  not the goal itself — the V9 result predicts the useful statement is
  ICR **conditional on E20**: registry achieves high ICR at low error in
  lossless regimes and collapses in residual-bearing ones; V10 measures
  the same curve per regularity TYPE (periodic rules should bend the
  curve toward the archive — the first predicted EPISODIC win on a
  memory metric).
- **Hallucination boundary**: (i) stale intrusion rate (existing counter),
  (ii) NEW anomaly-memorization rate: fraction of anomaly probes that
  trigger a book write or an archive entry. Registered prediction: the
  registry's verification gate refuses anomalies better than the archive
  (write-time consec filter), both beat EPISODIC's fit-only baseline.

## Predictions

- P1 (periodicity flips the ordering): on periodic rules, MATCHED ≥ FULL
  on E20 — the first registered episodic win in program history; the
  compact form provably cannot carry (δ, k).
- P2 (composition shows the registry's inference advantage): FULL
  discovers composite rules faster than MATCHED discovers them from
  instances — and can answer composite probes it has NEVER observed
  (composition transfer), measured as composite-rule probe-1 hits before
  any R3 episode completes.
- P3 (anomaly separates verification from memory): anomaly-memorization
  rate FULL < MATCHED, and arms with read-time exactness (the W9B/W9C
  lesson: refit-on-confirmed-instances) refuse best of all.
- P4 (ICR law): per regularity type, the E20-vs-ICR curve crosses —
  lossless type favors the registry, periodic type favors the archive.
  This is the quantified "abstraction advantage radius" (W9A's cliff,
  now per-structure-type).

## Design discipline

- World shift, not a system mutation (M3 class): three standard arms, no
  new capability — EXCEPT the read path needs no change at all; the
  registry's periodic handicap is honest (it can store (a, b_0, δ, k) in
  its entries — the question is whether its discovery machinery finds δ).
- Seeds: default run seed; composite world keys read RUN_SEED for
  realizations (post-G4 split discipline).
- 2 h per run, three arms, paired per-(family, epoch) contrasts.
- Failure mode watched: if the registry simply cannot represent periodic
  rules, P1 is trivially confirmed by storage mismatch, not discovery
  failure — the analysis must separate "cannot store" from "cannot
  discover" (registry entries for periodic rules carry δ if discovered;
  log whether δ ever enters the book).

## Relation to the user's five directions

| direction | flyloop custody status |
|---|---|
| 1 ICR | defined above, computable from existing runs (baseline first) |
| 2 benchmark (compression/transfer/surprise) | V10 = the in-loop benchmark; transfer = composition probes |
| 3 closed loop with flyloop | THIS document |
| 4 insight vs hallucination | anomaly-memorization rate + stale intrusions (in-loop, mechanical) |
| 5 active exploration / curiosity loop | out of flyloop custody for now (needs a proposal lane; registered as the V11 candidate) |
