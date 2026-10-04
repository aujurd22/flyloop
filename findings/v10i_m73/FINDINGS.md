# M7.3 re-adjudication (v10i): the rid fix made the derived candidate answer
# its own probe-1 perfectly — and the answer is almost always WRONG.

Runs: 2026-10-04 20:43 → 22:43, composite world, 4 arms, CAP=2, 2.0h,
cycle 4314, 0 fails. Code: per-answer flag (96f3a9f) + rid double-prefix
fix (969aeee) + m73 trace notes.

## 1. Mechanism: FIXED (counter-grade)

- Pre-fix (v10g'/h' + the 0.5h trace run): the derived candidate entered
  cands under a mangled rid (f3r+f3r2="f3rf3r2"); it sometimes answered,
  but the flag's dp[0]==aux comparison could never fire. NEW probe-1
  derived_use was 0%.
- Post-fix: m73 trace shows clean forms end to end
  (`m73:aux=f3r2,m=rule,dp=f3r2,11,0,2,cands=...|f3r2@e2,flag=1`).
- **59/59 NEW probe-1s with a live derived candidate → the candidate was
  retrieved, selected (first ep==epoch candidate → method "rule"), and
  answered under its own rid. flag=1 rate 100%, zero misses.**
- Semantics note: "rule" in predict_puzzle_v4 = first candidate stamped at
  the current epoch — the derived candidate is the ONLY such candidate on a
  NEW probe-1, so derived_use measures candidate-use and is trivially 100%
  once it exists. The informative metric is accuracy.

## 2. Composition quality: AT FLOOR (the claim moves DOWN)

Derived-candidate answer correctness at NEW probe-1, by family:

| family | correct | composite in world law? |
|--------|---------|------------------------|
| 0      | 1/15    | no                     |
| 1      | 1/15    | no (periodic/drift)    |
| 2      | 3/13    | **YES (index>=2 composition)** |
| 3      | 1/16    | no                     |

Overall 6/59 (10%). The composite family (3/13 = 23%) is statistically
indistinguishable from the non-composite families (3/46 = 6.5%). The world's
composition law is NOT being recovered by R_new = (a1+a2, b2-b1) over the
two most-recent-by-epoch book rules.

Candidate causes (distinguishable next session):

1. **Predecessor selection mismatch**: the world composes by rule INDEX
   (rule i from i-1, i-2); the derivation takes the two most recent by
   epoch. If the book's write order diverges from index order (drift,
   revisits), the wrong pair is composed.
2. **Anchor/wave semantics**: stored-pair replay uses y_s + a*(xp-x_s)
   (anchored, wave-inclusive); the derived candidate predicts raw
   a*xp+b with no anchor. Even a slope-correct derivation fails if a
   per-episode offset exists. Test: re-score the 59 with the anchored
   form y1 + a_derived*(xp-x1) — needs only the slope to be right.
3. fam-2's actual composition law differs from the formula.

## 3. Reference points

- V10c "clean-filter 40% (4/10)" was measured under the polluted
  ever-derived flag with a different denominator — not comparable to the
  per-answer numbers above; retire it as the M7 reference.
- Blind-derivation poison cost is now measurable directly: 53 wrong
  candidate-adoptions at NEW probe-1 (90% of firings).

## 4. Registered next (M7.4)

1. Re-score the 59 trace events with the anchored predictor. The probe
   values are not in the note; reconstruct them via world.puz_probe(fam, c)
   under the run's SEED and verify against the recorded truth before
   trusting the reconstruction.
2. If anchored scoring still floors fam-2, log the family's book
   write-order vs index-order at derivation time (test cause 1).
3. Only then consider constraining derivation to the composite family.

## 5. M7.4 resolution (same night, offline)

**M7.4-1 anchored re-score (m74_anchored_rescore.py):** probes reconstructed
via world.puz_probe — 59/59 truth match. Anchored predictor y1+a_d(xp-x1):
7/59 vs raw 6/59 (WAVE_AMP=0 in this config, so anchored ≡ slope test).
dp slope == true slope only 6/59; full (a,b) 1/59. Cause 2 (anchor/wave)
REFUTED — the slope itself is wrong.

**M7.4-2 predecessor audit (source-level):** world.py composes fam
COMPOSITE_FAM ONLY, from the two immediate predecessor EPISODES:
`R_i = (ep[i-2].a + ep[i-1].a, ep[i-2].b - ep[i-1].b)` — RECALL episodes
OCCUPY slots in that sequence. The cycle.py derivation instead composes the
two most-recent-by-epoch DISTINCT book rules. Whenever a RECALL interleaves
(world composed ep[i-2]=r_k, ep[i-1]=r_k; book holds {r_j, r_k}, j≠k), the
derived pair is wrong. This is the mechanism behind fam-2's 2/13 slope
accuracy; fams 0/1/3 are random-rule families where blind derivation is
wrong by design.

## 6. Registered M7.5

Derivation input := the family's last TWO EPISODES (multiset semantics,
repeats included), not the deduplicated freshest book rules. Implemented as
FLYLOOP_DERIVE_EPISODES=1 (per-family deque of the last two episode rule
params as identified at their episodes); adjudicate vs baseline in parallel
on the 208-core cloud node (baseline + variant, 4 arms each, 1h).
