# V5 findings — the condition law, run B (eps=0.25) vs run A (eps=0)

Run B: 2026-09-28 18:49 → 20:49, 2 h deadline, three arms, fresh stores.
Run A: the V4 early-stop run (same seed, same schedule, eps=0) — reused as
baseline, no rerun. Run B quotas: RECALL 58 (near the 75 full-quota mark).
Write parity byte-exact (23390 + 23663 = 47053 drained). 0 readback failures.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| V5-P01 | eps=0 replication: F edge on discovered recurrences | **PARTIAL** | dE20(M−F)=+0.137 CI[−0.043, 0.310], n=51 — direction replicates V4's marginal edge, CI crosses |
| V5-P02 | condition law (headline) | **CONFIRMED** (operationally) / **narrative REFUTED** | dE20(M−F) at eps=0.25: **+1.155 CI[0.755, 1.571]**, n=58; between-run contrast **+1.018 CI[0.584, 1.472]** |
| V5-P03 | discovery rate drops under noise | **CONFIRMED** | 0.894 → 0.744 discoveries per NEW/VARIANT episode |
| V5-P04 | book_test collapses under noise | **PARTIAL** | success 0.986 → 0.939: only −5pp, NOT the registered collapse |
| V5-P05 | EPISODIC degrades slowest | **REFUTED** | damage B−A: MATCHED **+4.14** > EPISODIC +3.86 > FULL +3.08 (CIs exclude 0 pairwise for F/M) |

## The finding: noise AMPLIFIES the compression advantage

V5_DESIGN §1 predicted the opposite ("the F−M gap should shrink toward zero
as ε rises" — the naive transfer of P46's condition law to the noise axis).
The data say the reverse: under 25% observation noise the compression
advantage **triples** (0.137 → 1.155 errors per RECALL episode), with the
between-run contrast at +1.018 (CI excludes 0). The mechanism is not the
registered one either — book_test did not collapse (−5pp only), because a
rule that survives consec-3 exact verification is *noise-filtered at write
time*, while the episodic archive absorbs flipped pairs indiscriminately and
its exact-match matcher then poisons itself on them (damage ranking: MATCHED
worst, EPISODIC middle, FULL best).

Registered law candidate (flyloop L-candidate, cross-repo with P46/P50/P51):

> **Write-time verification is the noise filter.** Representations whose
> writes are gated by verification against the stream (abstracted rules)
> are noise-filtering; representations that store observations as-is
> (episodic pairs) are noise-accumulating. Under measurement noise the gap
> between them GROWS — the advantage of structure is conditional on noise
> in the opposite direction of the overlap condition.

This does NOT contradict P46: overlap (approximate recurrence) and noise
(measurement corruption) are different manipulations. P46's in-loop test
still requires the tolerance matcher (V6, registered in V3_DESIGN §8). What
V5 adds is the second axis of the condition law and a correction to its
naive reading: it is not "messier worlds favor instance memory" — it is
"worlds that let you VERIFY writes favor structural memory; worlds whose
classes overlap favor instance memory". Noise is the former kind of mess.

## Also settled

- **P03 (C1 degradation)**: discovery rate 0.894 → 0.744 under noise — the
  extraction-quality axis of the P50 law shows up in-loop exactly as the
  two-condition law predicts.
- **P04 (mechanism correction)**: the registered collapse mechanism failed;
  verification, not luck, is why book rules stay clean.

## Method notes

- compare_v5.py: between-run cluster contrasts (rule lineage) + per-arm
  damage CIs; ledger verdicts applied to run B. Initial run of the script
  had a claim-prefix mismatch (verdicts not landing) and a double-dash id —
  both fixed in the same commit as these findings; verdicts were applied
  from the corrected script output.
- V4's run A was reused as the eps=0 baseline (same seed/schedule) — no
  rerun spent on the baseline.
- Early-stop operator policy: total added wall clock 2 h, as directed.
