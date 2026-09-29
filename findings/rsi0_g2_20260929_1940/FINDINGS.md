# RSI-0 G2 findings — per-rule encoding: mechanically sound, REJECTED on merit

Run: 2026-09-29 19:40 → 22:10, 2.5 h cap, three arms (FULL per-rule registry
cap-13 / MATCHED sparse archive / EPISODIC), ε = 0.25, tolerant matcher 0.6.
0 failures, readback fails 0 (G1's 69% dead-write failure eliminated by the
force_new per-rule encoding).

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| RSI0-G2-P01 | per-rule cap-13 beats g0's cap-5 (FULL E20 < 2.347) | **REFUTED** | FULL E20 = 3.660 (n=53 discovered recurrences) vs g0 2.347 — the larger registry does NOT help |
| RSI0-G2-P02 | readback fails < 5% of book writes | **CONFIRMED** | 0 failures across the run (force_new per-rule encoding mechanically sound) |
| RSI0-G2-P03 | probe-1 book_test hits ≥ 38.8% (g0 level) | **CONFIRMED** | 22/53 = 41.5% |

## Interpretation

M1's intent was: "the no-candidate floor (15-19 probe-1 failures) comes from
recency eviction at cap 5; raising the cap puts more candidates in the
window". The mechanically feasible version (per-rule entries, no 120-char
trap) was tested and the floor did NOT shrink the advantage — **the
no-candidate probe-1 failures are mostly NOISE failures (the revealed pair
was flipped), not missing-candidate failures**. More stored candidates do
not recover flipped observations; they only add false-match risk at read
time.

This is the RSI-0 loop's second merit-rejection: the first (G1) was
mechanically infeasible; this one was mechanically sound and failed on
merit. Both rejections sharpen the constraint map: (1) entries must stay
< 120 chars (G1), (2) registry size does not buy recovery from flipped
observations (G2).

## Lineage

G1: M1 (naive cap raise) — REJECTED (mechanically infeasible).
G2: M1 (feasible re-encoding) — REJECTED (no E20 improvement; the floor is
noise-bound, not candidate-bound).
Next candidate: none from the current menu — the menu needs a new mutation
class (e.g., tolerance-matched retrieval of flipped pairs, or reveal-pair
noise estimation) before the next generation runs.
