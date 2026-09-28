# V7 Phase B findings — the wavy world: no inversion, uniform collapse

Run: 2026-09-29 04:47 → 06:47, 2 h cap, three arms, ε = 0, WAVE_AMP = 2
(50 RECALL episodes, 5720 cycles, 0 failures, full http×3). The world: each
rule carries a SMOOTH per-rule sinusoid wav(x) = round(2·sin(2π(x+φ)/13))
with rule-seeded phase, stable across episodes — prototypes always miss it,
instances of the same rule accumulate it exactly.

## Result: the registered order-inversion did NOT materialize

| arm | E20 (RECALL) | methods |
|---|---|---|
| FULL | 9.620 | rule 1163 / book_test 55 / fit 1493 / guess 153 |
| MATCHED | 9.720 | epi_test 109 / fit 2630 / guess 125 |
| EPISODIC | 9.840 | fit 2664 |

F ≤ M ≤ E preserved (differences 0.10-0.22, marginal); overall FULL error
rate 75.7%. By episode length: short episodes (≤8 probes) F 3.88 / M 3.94 /
E 3.94; mid (9-20) ~11.6; long (21+) ~15.5-16.3 — all arms degrade with
episode length under the wave, roughly equally.

## Why no inversion (mechanism, from the numbers)

1. **The prototype's wave-blindness is bounded** (|wav| ≤ 2, typical ~1.2),
   while **the instance archive's x-support is 5 of 13** — the coverage
   asymmetry found in V7A still dominates: a stored instance only helps when
   the probe x coincides with a previously-seen x (~38%), and the sinusoid
   is smooth, so a 2-point live fit already interpolates the wave partially.
   Neither memory makes the wave difference decisive.
2. **epi_test fired 109 times without moving E20** — exact wave-match
   requires the probe x to be one of the ~5 archived x's; at that rate the
   instance information arrives too sparsely to beat the prototype's
   full-support +1.2-typical error.

## The V5→V6→V7B line, corrected and closed for this world family

- V5: noise amplifies the structured advantage (+1.16). V6: not a matcher
  artifact (+2.31 with symmetric tolerance). V7A: the amplification
  decomposes into support dominance (~5:1 over write-verification depth).
- **V7B: the wave axis does not invert the ordering at amplitude 2 with
  sparse 5-pair instances.** The instance-friendly condition from P46
  (continuous/overlapping statistics) is NOT reproduced by "prototype misses
  a smooth wave + sparse instances" — because the prototype's loss is
  bounded and the instances' coverage is the binding constraint. A world
  where instances win needs the instance information to be dense (many
  stored points, or queries concentrated on seen x's) or the prototype loss
  to be unbounded (per-x independent noise ON THE TRUTH — the truth-noise
  variant, where NO affine rule exists and instances of neighbors are the
  only signal).

## Honest notes

- WAVE_AMP = 2 was chosen conservatively for the first pass; the dose is
  arguably too low (all-arm collapse to ~48% error suggests the wave
  dominates EVERYTHING, yet the arms stay within 0.2 of each other — the
  wave adds a common error floor that does not discriminate arms).
- The e20-by-length gradient (short 3.9 → long 15.5-16.3) is a real signal:
  under the wave, longer episodes accumulate wave-mismatched stored rules
  and tables — memory contents made of earlier-episode structure actively
  hurt later probes within long episodes. Registered for V8: separate
  "stale-within-episode" from "wave residual".
- Registered V7B predictions were phrased for the wave-stable design; they
  are evaluated as above (no inversion → the registered inversion claim is
  REFUTED for this implementation).
