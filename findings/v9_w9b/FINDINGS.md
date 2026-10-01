# W9B findings — the plateau is the prediction floor, not the matcher (M5 is the only remaining lever)

Run: 2026-10-01 16:37 → 18:37, W=4, ε=0.15, arms FULL / **MATCHED-EXACT**
(the W9B mutation: archive matcher tol=0) / EPISODIC, 6201 cycles,
0 failures. World bit-identical to the W9A W=4 run (default run seed).

## Controls

**FULL reproduced W9A's W=4 FULL bit-for-bit**: 2567/2567 puzzle events
identical. The determinism harness is now a working asset — a same-world
rerun is a free randomized-free control, and its bit-identity certifies
the comparison.

## Verdict: tolerance decoupling does NOT rescue the archive

| arm (W=4) | E20 | CI | n_ep |
|---|---|---|---|
| W9A FULL | 10.581 | [8.98, 12.30] | 43 |
| W9A MATCHED | 10.419 | [8.87, 12.08] | 43 |
| W9B FULL (control) | 10.920 | [9.39, 12.49] | 50 |
| **W9B MATCHED-EXACT** | **10.620** | [9.14, 12.13] | 50 |

MATCHED-EXACT ≈ MATCHED ≈ FULL — the "plateau is matcher self-inflicted"
hypothesis is **REFUTED**. Exact identification of the right archived
episode changes nothing, because identification was never the binding
constraint at W≥2.

## Where the plateau actually lives: the prediction layer

Both reasoner paths (book and archive) end in the same compression step:
`fit_from(pairs)` produces a compact (a, b), and the prediction is
`(a·xp + b) mod p`. The wave never enters the prediction. The arithmetic
matches the observation exactly: for W=4, P(wave(x) ≠ 0) = 1 −
4·arcsin(0.125)/2π ≈ **0.92**, and the runs' rolling err100 sits at
0.86–0.94. Every arm eats the same irreducible prediction floor: identify
the rule perfectly, then throw the residual away at the last step.

Rolling err100 in W9B: FULL 0.94, MATCHED-EXACT 0.86.

## Consequence: M5 (residual registry) is the only remaining lever

The W9A/W9B pair localizes the entire W≥2 plateau to one design choice:
prediction compresses the residual away. The registered recovery (M5,
V9_DESIGN) attacks exactly that — store per-rule wave residuals alongside
the compact rule and add a wave estimate at prediction time. Registered
predictions for W9C (M5 vs same-world controls):

- P1: FULL-RES beats the ~10.5 plateau at W=4 by a wide margin
  (the residual table carries what the compact form discards).
- P2: the advantage grows with visits to the same rule (residual table
  fills across episodes) — a learning-to-predict-the-residual curve, not
  a constant offset.
- P3: flip noise poisons at most a minority of stored residuals
  (|res| ≤ W filter keeps true wave samples, drops most flips).
- Control: FULL must bit-replicate again (third consecutive harness pass).

## Falsification ledger update

| hypothesis | verdict |
|---|---|
| W9A "plateau is matcher self-inflicted" | **REFUTED** (W9B) |
| "identification is the binding constraint at W≥2" | REFUTED |
| "prediction-layer compression carries the plateau" | **SUPPORTED** (err100 ≈ P(wave≠0) arithmetic) |
