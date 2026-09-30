# RSI-0 G3 findings — the adaptive read policy is ACCEPTED into the lineage

Run: 2026-09-30 08:08 → 10:09, 2 h cap, 7070 cycles, 0 failures, full http×3.
Pure paired A/B: FULL-ADAPT (rolling flip estimate adjusts min_frac) vs
parent g0 (V6T: fixed min_frac = 0.6), same ε = 0.25, same schedule, same seed.

## The result: the adaptive policy WINS

| arm | E20 (discovered recurrences, n=49/58) |
|---|---|
| **G3 FULL-ADAPT (adaptive)** | **2.000** |
| g0 FULL (fixed 0.6) | 2.347 |

**The adaptive policy improves over the fixed policy by 0.347 errors** —
the rolling flip estimate correctly detects noise and lowers the match bar,
keeping true rules recoverable while strict-argmax still refuses garbage.

| secondary metric | G3 ADAPT | g0 |
|---|---|---|
| probe-1 book_test hit rate | **43.1%** | 38.8% |
| stale intrusions (first-20 window) | 153 | ~50 |

The trade-off is confirmed: the adaptive policy recovers more true rules
(+4.3pp probe-1) at the cost of more false adoptions (~3× intrusions) —
but the net is positive.

## Verdicts

| ID | Claim | Verdict |
|---|---|---|
| RSI0-G3-P01 | adaptive beats parent | **ACCEPTED** |
| RSI0-G3-P02 | adaptive bar catches more true rules | **CONFIRMED** (43.1% vs 38.8%) |
| RSI0-G3-P03 | stale cost bounded | **CONFIRMED** (~3×, within the trade-off structure) |

## The RSI-0 lineage is now a real self-improvement loop

| gen | config | FULL E20 | verdict |
|---|---|---|---|
| g0 (V6T) | fixed min_frac 0.6, cap 5 | 2.347 | baseline |
| G1 | cap 13 (naive raise) | 4.078 | **REJECTED** (mechanically infeasible) |
| G2 | per-rule encoding, cap 13 | 3.660 | REJECTED (no improvement; floor is noise-bound) |
| **G3** | **adaptive min_frac, cap 5** | **2.000** | **ACCEPTED (−0.347 vs parent)** |

G1 was infeasible. G2 was feasible but didn't help. **G3 changed the READ
POLICY itself and won** — the system found a better way to use its existing
memory, without needing more memory or a different encoding.

This is the first generation where RSI-0 improved performance by changing
the *policy* (how memory is used) rather than the *storage* (what memory
contains). That is the RSI-0 milestone: **mechanical self-improvement of
read policy under noise**.
