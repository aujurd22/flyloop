# DESIGN V5 — The Condition Law: representation advantage under observation noise

Status: registered 2026-09-28 evening. Short runs by operator decision
(V4 proved headline effects visible inside 2 h). Design motivated by sibling
results landed the same day:

- intuition-mechanism **P46 second-family inversion**: EPI 65.5% > STR 55.7% —
  "structural memory wins on compact discrete families, instance memory wins
  on continuous-overlapping families" (prototype–exemplar dissociation,
  mechanistically replicated across four families; P51 synthesis).
- flymemory/intuition **P50 two-condition law**: recognition is decided by C1
  (extraction quality) alone; novelty requires C1 AND C2 (hull visibility).
  Engineering prescription (flymemory side): rewrite novelty-type judgments
  into anchored comparisons against recalled candidates.

## 1. The question

V4 established the ordering F ≤ M ≤ E on discovered-rule recurrences, with
the matcher contributing most of the advantage (E−M = +0.49) and compression
adding marginally (M−F = +0.14, CI crossing 0). Both V4 and the sibling
results point at the same law: **a memory representation's advantage is
conditional on the world's observation structure**. V5 tests the flyloop
version:

> Does the compression's (small) extra advantage survive observation noise?

Prediction under the condition law: no. A stored prototype (a, b) abstracted
from a few pairs is noise-brittle — one flipped observation poisons a
consec-verified fit and kills exact book_test matches — while the matcher
arms already rely on multi-pair fitting that degrades gracefully. So the
F−M gap should shrink toward zero as ε rises, and the discovery rate
(C1 extraction) should drop.

## 2. Manipulation

`NOISE_EPS` (env `FLYLOOP_NOISE_EPS`, default 0): the REVEALED pair's y1 is
flipped to a different value with probability ε. Truth stays exact (the
world's ground truth is untouched — this is measurement noise, not world
drift). The flip is a pure function of (fam, cycle, seed), so all three arms
see IDENTICAL corrupted observations — pairing is unchanged.

- **Run A = V4's run** `v4_20260928_1636` (ε = 0, same seed, same schedule,
  51 RECALL episodes) — the ε=0 baseline, no rerun needed.
- **Run B** = new short run at ε = 0.25, target RECALL ≥ 45 or 90 min.

Everything else frozen from V4 (three arms, schedule, quotas, parity).

## 3. Endpoints

| ID | Claim |
|---|---|
| V5-P01 (replication) | At ε=0 (run A), the F−M advantage is positive on discovered recurrences (V4-P02 continuity check). |
| V5-P02 (headline, condition law) | dE20(M−F) at ε=0.25 is LARGER than at ε=0 (noise shrinks the compression advantage); cluster-bootstrap CI of the between-run contrast excludes 0. |
| V5-P03 | Discovery rate drops under noise: discoveries per NEW episode, ε=0.25 < ε=0 (C1 extraction degraded). |
| V5-P04 (mechanism) | FULL's book_test success rate collapses under noise (its one-pair exact match is noise-brittle) — the mechanism behind P02. |
| V5-P05 | EPISODIC degrades slowest in absolute error under noise (multi-pair fitting is the noise-robust path) — E20(E, ε=0.25) − E20(E, ε=0) < corresponding F and M deltas. |

Inference: cluster bootstrap by rule lineage within each run; between-run
contrasts via independent cluster resampling. SIR carries the V4 absolute
count floor. DISCOVERY/REACTIVATION split; temporal UIR rules inherited.

## 4. Stop rules

Per run: RECALL ≥ 45 or 90 min deadline, engineering tripwires unchanged.
Total added wall clock ≤ 2 h.

## 5. What V5 is NOT

- Not the P46 "overlap" manipulation proper — exact-match matching is brittle
  to ANY perturbation, so approximate recurrence (b±1 returns) would need a
  tolerance matcher first; that matcher redesign is registered as V6 (it
  changes the algorithm for all arms equally and deserves its own run).
- Not a novelty/hull experiment (P48/P49's C2) — flyloop's stale-intrusion
  metric is the in-loop novelty analog and stays on the books at full-quota
  length where intrusion counts are readable.
