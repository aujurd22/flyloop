# DESIGN V7 — Factorial Decomposition × The Abstraction-Loss World

Status: registered 2026-09-28 late evening (post-V6 review). Nothing
implemented yet. Two phases, both short (≤ 2 h each, operator policy).

## 0. Motivation (the V6 review, accepted)

V6 established: under ε=0.25 noise the recurrence advantage of FULL over
MATCHED WIDENS with a symmetric tolerant matcher (+1.155 → +2.306) — the
matcher-artifact hypothesis is dead. But FULL and MATCHED still differ in
THREE bundled factors:

1. **support size** — a rule covers all 13 x; an archived table covers ~5;
2. **write-time verification** — rules pass consec-3 exact verification;
   archive rows are written as-observed (25% flipped);
3. **abstraction** — (a, b) vs raw pairs.

V7 takes the bundle apart. Priority per the review: the factorial before
more noise levels; the abstraction-loss world before more mod-13.

## 1. Phase A — the 2×2 factorial (same mod-13 world)

| arm | support | write |
|---|---|---|
| FULL (= V4 FULL) | full (rule → all x) | **verified** (consec-3) |
| FULL-RAW (new) | full | **unverified** — rule written from the first 2-pair fit, no consec gate |
| MATCHED-VER (new) | sparse (5 pairs) | **verified** — only archive rows whose pairs survived one confirmation probe |
| MATCHED (= V4) | sparse | raw |

All four arms share the identical schedule/probes/pairing; two extra
sandbox instances (ports 8772/8773); padding parity extended to four-way.

Registered predictions (cluster CIs, rule-lineage clusters):

- **V7-P01**: under ε=0.25, support is the DOMINANT factor —
  |F − F-RAW| < |F − M| (unverified-but-full-support keeps most of the
  advantage). If instead F − F-RAW ≈ F − M, verification dominates.
- **V7-P02**: MATCHED-VER improves over MATCHED but stays worse than
  FULL-RAW (verification helps, support caps it).
- **V7-P03**: SIR(F-RAW) > SIR(F) — unverified full-support writes are
  exactly the noise-amplifier V5's mechanism predicts (poisoned rules
  covering all x).
- V7-P04 (NC): the E arm unchanged.

The interaction term (support × verification) is the deliverable: it decides
whether the program's headline is "verify your writes" or "generalize your
storage" or both.

## 2. Phase B — the abstraction-loss world

A world where **no compact (a, b) reproduces the observations** — the
condition where P46/P51 predict instance memory wins:

- `y = (a x + b) mod 13`, then each episode's map is perturbed per-x by a
  fixed random offset drawn once per (episode, x) pair (a "wavy affine"):
  compression to (a, b) now has an irreducible error floor of ±w, while the
  raw pair table of the SAME episode reproduces its own entries exactly.
- Registered prediction: the F/M/E ordering INVERTS on long episodes
  (instance archive beats the rule) — the in-loop replication of P46's
  second-family inversion, with the wave amplitude w as the dose-response
  knob.

Implementation notes: w lives in world.py (pure function, seeded, schedule
artifact unchanged in format); the reasoner needs no changes (fit residual
n_ver simply never reaches the old ceiling; discovery criterion needs a
band-adjusted form — registered before implementation, exact bands set in
the pilot).

## 3. The probe-1 floor (from the V6 review, resolved with data)

Post-hoc decomposition on the three finished runs (world recomputed
offline; unexplained = 0 in all three):

| run | recovered | flipped reveal | no candidate | unexplained |
|---|---|---|---|---|
| V4 ε=0 | 32 | 0 | 19 | 0 |
| V5B ε=0.25 exact | 25 | 17 | 16 | 0 |
| V6T ε=0.25 tolerant | 19 | 15 | 15 | 0 |

Correction to the V4-era arithmetic: the probe-1 ceiling was never
62.7% × 0.75 — there is a **~35% no-candidate floor** (BOOK_CAP=5 recency
eviction + late discoveries) present even without noise. V7 therefore also
sweeps BOOK_CAP ∈ {5, 13} as a covariate: if the floor is the book's recency
policy, raising the cap should lift the whole recovery curve.

## 4. What V7 does NOT do

- No longer runs, no added noise doses (V6 closed the noise axis).
- Still no LLM in the loop; still no claim about "compression generally
  induces structure" — Phase B is precisely the test of when it does NOT.
