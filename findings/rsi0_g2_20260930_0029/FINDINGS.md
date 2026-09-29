# RSI-0 G2 findings — per-rule encoding: mechanically sound, REJECTED on merit

Run: 2026-09-30 00:29 → 03:00, 2.5 h cap, three arms (FULL per-rule registry
cap-13 / MATCHED sparse archive / EPISODIC), ε = 0.25, tolerant matcher 0.6.
0 failures, readback fails 0 (G1's 69% dead-write failure eliminated by
force_new per-rule encoding + index lockstep prune).

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| RSI0-G2-P01 | per-rule cap-13 beats g0's cap-5 (FULL E20 < 2.347) | **REFUTED** | FULL E20 = 3.692 (n=52 discovered recurrences) vs g0 2.347 — the larger registry does NOT help |
| RSI0-G2-P02 | readback fails < 5% | **CONFIRMED** | 0 failures across 146 book writes (force_new per-rule encoding mechanically sound) |
| RSI0-G2-P03 | probe-1 book_test hits ≥ 38.8% | **CONFIRMED** | 22/53 = 41.5% ≥ 38.8% |

## Interpretation

The mechanically feasible version of M1 (per-rule entries immune to the
120-char trap) was tested and the full-support arm still underperformed the
parent. The no-candidate probe-1 failures are mostly NOISE failures (the
revealed pair was flipped), not missing-candidate failures — adding more
candidates does not recover flipped observations.

Combined with V7C's finding that shallow write beats deep write
significantly (−0.655 CI [−1.10, −0.17]), the constraint map is now:

1. Entries must stay < 120 chars (G1 constraint);
2. Registry size does not buy recovery from flipped observations (G2);
3. Shallow write beats deep write under noise (V7C — availability beats
   delayed correctness; read-time exactness is the real filter);
4. Stale intrusions triple with shallow writes (V7A/V7C consistent —
   the availability/poisoning trade-off is real and quantified).

## Lineage

G1: M1 naive cap raise — REJECTED (mechanically infeasible).
G2: M1 feasible re-encoding — REJECTED (no E20 improvement; the floor is
noise-bound, not candidate-bound).
Menu: M1 struck; M2 (tolerance) already at optimum; M3 is a control.
Next candidate: requires a new mutation class registered before the next
generation runs.
