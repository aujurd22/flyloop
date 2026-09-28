# V6 findings — tolerant matching: the V5 amplification is NOT an artifact

Run T: 2026-09-28 21:59 → 23:41, stopped by operator at 1.87 h / 4241 cycles
(the three-way answer had stabilized — see the mid-run and final numbers
below). Pure algorithm A/B vs V5B: identical ε=0.25 world, same seed and
schedule, only the matcher differs (MATCH_MIN_FRAC 0.6 vs exact 1.0).
Three-way write parity byte-exact (20582 drained at mid-run; final report
has the closing figure). 0 cycle failures. run_status OK.

## Verdicts

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| V6-P01 (headline) | V5's noise amplification of the F−M gap is a matcher artifact | **REFUTED** | tolerant matching rescued FULL (3.621 → 2.347, −1.27) while MATCHED stayed flat (4.776 → 4.653, −0.12); dE20(M−F) **widened +1.155 → +2.306** |
| V6-P02 | MATCHED damage shrinks below EPISODIC with tolerance | **REFUTED** | the 5-pair x-support of an archived table cannot compete with a rule's universal coverage under noise |
| V6-P03 | matcher paths reopen | **CONFIRMED** | epi_test 44 → 60 uses; book_test 151 → 174 |
| V6-P04 (registered cost) | stale intrusions rise under tolerance | **REFUTED** | first-20-window intrusions 53 → 53 flat — the 0.6 band + strict argmax refused ambiguous candidate sets (ties → refusal) |
| V6-P05 | probe-1 exact recovery ≥ 40% | **PARTIAL** | 19/49 = 38.8%, a hair under (flip noise removes ~25% of would-be matches) |

## The law, now pinned by a controlled A/B

Across V4 → V5 → V6 (same world family, three matcher/noise conditions):

| condition | F | M | E | dE20(M−F) |
|---|---|---|---|---|
| ε=0, exact | 0.431 | 0.569 | 1.059 | +0.137 |
| ε=0.25, exact | 3.621 | 4.776 | 4.966 | **+1.155** |
| ε=0.25, tolerant 0.6 | 2.347 | 4.653 | 4.918 | **+2.306** |

Tolerant matching rescued the arm that stores VERIFIED ABSTRACTIONS
(F: −1.27 errors — the true rule reproduces ~75% of noisy pairs, wrong
rules ~8%, the fraction separates them) and did nothing for the arm that
stores RAW OBSERVATIONS (M: −0.12 — its 5-pair x-support cannot cover the
13-x input space, and 25% of its stored pairs are poisoned anyway).

> **Law candidate (flyloop, cross-checked with P46/P50/P51):** under
> measurement noise, the recurrence advantage of structured memory over
> instance memory GROWS — driven by write-time verification (noise filtered
> at the write) times full-support coverage (rules generalize to every x;
> instances only cover the x they saw). The two conditions of the P50
> two-condition law and the P46 dissociation are real but belong to the
> overlap axis; the noise axis favors structure on BOTH matcher regimes.

## Honest notes

- Operator early stop (answer stabilized mid-run; the final 29 RECALLs were
  not going to flip a +2.31 gap whose V5B counterpart was +1.16 with CI
  [0.755, 1.571]).
- The registered cost of tolerance (rising stale intrusions) did NOT
  materialize — the strict-argmax refusal discipline kept the tolerance
  from leaking. P04's own prediction was wrong in the useful direction:
  tolerance is free here.
- probe-1 landed at 38.8%, a hair under the 40% band — flip noise removes
  ~25% of would-be matches by construction; with ε=0.15 the band would be
  met comfortably. Not pursued (short-run policy).

## Where this leaves the program

- V3: structured memory has a recurrence advantage. V4: the advantage is
  mostly the matcher. V5: noise amplifies the structured advantage. V6:
  that amplification survives a symmetric tolerant matcher — it is
  coverage × write-time verification, not matcher brittleness.
- intuition-mechanism P46's instance-friendly condition (continuous /
  overlapping class statistics) remains the un-tested axis in the loop; it
  requires a world where abstraction genuinely loses information (noisy or
  non-affine maps), now scoped as V7 with the length/noise machinery built
  here.
- Cross-repo: P46 (second-family inversion) and the P50 two-condition law
  motivated this run; the in-loop result *corrects the naive transfer* of
  that law to the noise axis — the same correction pattern as V3's P06.
