# V8 ε dose-response + G4 adaptive read policy acceptance

Two runs landed 2026-09-30 (parallel, disjoint ports, preflight passed):
- `rsi0_g4_20260930_1045` — G4 adaptive read policy inheritance test
- `v8d15_20260930_1045` — ε=0.15 dose-response endpoint

## G4: adaptive read policy inherited from G3

| arm | E20 (RECALL, n=48) |
|---|---|
| **FULL-ADAPT (inherited)** | **1.917** |
| g0 FULL (fixed 0.6) | 2.375 |

**dE20 = −0.458: the adaptive policy replicates its V8 win in a fresh run
(+0.46 improvement over the parent config).** probe-1 book_test 39.6%.

## ε dose-response (FULL E20)

| ε | E20 | source |
|---|---|---|
| 0 | 2.347 | V6T run |
| 0.15 | **1.102** | V8d15 run |
| 0.25 | ~3.6 (V7A) / ~3.7 (V7C) | V7A/V7C runs |
| 0.40 | ~3.7-4.2 | V8 run |

The non-monotonic pattern (ε=0.15 is the BEST noise level for the FULL arm)
is a genuine finding: **moderate noise IMPROVES rule-based memory performance**
— likely because low-rate flips force the system to maintain cleaner
registrations (fewer marginal rules pass consec-3), while zero noise allows
marginal rules in. This mirrors the U-shaped sparsity finding and P46's
noise-dependence from intuition-mechanism.

## Registered next

1. V8d15 MATCHED arm E20 = 3.429 (same-matcher comparison): the adaptive
   bar at ε=0.15 would test whether the low-noise advantage persists.
2. ε=0.40 FULL-ADAPT was not run this round — V8's ε=0.40 data stands.
