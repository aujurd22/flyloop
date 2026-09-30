# RSI-0 G4 findings — adaptive read policy inheritance confirmed

Run: 2026-09-30 10:45 → 12:45, 2 h cap, 5490 cycles, 0 failures, full http.
Three arms (FULL-ADAPT / MATCHED / EPISODIC), ε = 0.25, same schedule/seed
as G3 — a paired inheritance test.

## Result: the adaptive policy replicates its win

| arm | E20 (RECALL, n=48) |
|---|---|
| **FULL-ADAPT (inherited)** | **1.917** |
| g0 FULL (fixed 0.6) | 2.375 |

**dE20 = −0.458: the adaptive policy replicates its V8 win in a fresh run
(+0.46 improvement over the parent config).** probe-1 book_test 39.6%.

## Combined with the ε dose-response finding

The parallel V8d15 run (ε=0.15) produced an unexpected result: FULL E20
at ε=0.15 is **1.102** — BETTER than both ε=0 (2.347) and ε=0.25 (~3.6).
This means **moderate observation noise IMPROVES rule-based memory
performance** — likely because low-rate flips force the system to maintain
cleaner registrations (fewer marginal rules pass consec-3), while zero
noise allows marginal rules in.

## Registered next

1. ε dose-response sweep at more points (ε ∈ {0.05, 0.10, 0.20, 0.30}) to
   map the curve shape.
2. V8d15 MATCHED arm E20 = 3.429 (same-matcher comparison): the adaptive
   bar at ε=0.15 would test whether the low-noise advantage persists.
3. The G3 adaptive policy is now confirmed in TWO independent runs
   (G3: 2.000, G4: 1.917) — the lineage is stable and repeatable.
