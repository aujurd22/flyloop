# DESIGN V6 — Tolerant Matching: was V5's noise finding an algorithm artifact?

Status: registered 2026-09-28 evening. Short run (2 h cap) per operator
policy. The arc this closes: V5 found that observation noise (ε=0.25)
AMPLIFIES the compression advantage (dE20(M−F) 0.137 → 1.155) and that the
MATCHED arm suffered the worst noise damage (+4.14, worst of three arms).
But V5's matchers were EXACT: one flipped observation kills any candidate
match, and the episodic archive absorbs flipped pairs into its rows. The
damage ranking may therefore be a property of the matcher's brittleness,
not of the representation. V6 changes exactly one thing.

## 1. The manipulation

`MATCH_MIN_FRAC` (env `FLYLOOP_MATCH_MIN_FRAC`, default 1.0 = exact, V4/V5
behavior). At 0.6, a memory candidate (rule for FULL, archived table for
MATCHED) matches the live observations when it reproduces **≥ 60% of the
live pairs exactly**, adopting the strictly-best candidate (ties broken by
recency — the V4 candidate order; note the final implementation refuses
top-rank ties outright instead of breaking them by recency — reviewer
option A, ambiguous identification is refused). Rationale: under ε=0.25 flip noise the
TRUE rule reproduces unflipped pairs exactly (~75% of pairs) — above the
band; wrong rules sit at ~1/13 ≈ 8% — far below. The fraction criterion
separates them where the all-pairs criterion could not.

Matcher composition (both memory arms, same decision rule):
1. exact unique match (kept first: probe-1 shortcut survives when the live
   pair is unflipped — 75% of pairs);
2. fraction-best match (≥ MATCH_MIN_FRAC, strict argmax; a top-rank tie is
   a refusal, not a recency tiebreak)
   — the noise antidote, live from probe 2 (needs ≥ 2 live pairs for the
   fraction to mean anything);
3. live fit → stale fit → guess/cold (unchanged).

Scoring stays EXACT (prediction == truth); only candidate identification
becomes tolerant. The tradeoff is registered, not hidden: tolerant matching
also lets a WRONG near-candidate pass on an all-flipped pair set — stale
intrusions may rise. That is V6-P04.

## 2. Comparison structure

- **Run T (this run)**: ε = 0.25, MATCH_MIN_FRAC = 0.6, same seed/schedule
  as V5B (paired episodes).
- Comparisons: vs **V5B** (ε = 0.25, exact matching — only the matcher
  differs: pure algorithm A/B) and vs **V4 run** (ε = 0 baseline).

## 3. Endpoints

| ID | Claim |
|---|---|
| V6-P01 (headline) | The V5 noise amplification of the F−M gap is a matcher artifact: with tolerant matching, dE20(M−F) under ε=0.25 is smaller than V5B's +1.155 (between-run cluster CI of the difference). |
| V6-P02 | MATCHED's noise damage shrinks below EPISODIC's (V5B: M +4.14 > E +3.86) — tolerant matching lets the archive's stored pairs vote, recovering instance memory under noise. |
| V6-P03 | epi_test and book_test usage recover vs V5B (matcher path reopens). |
| V6-P04 (registered tradeoff) | FULL's stale intrusions rise vs V5B (tolerance admits wrong candidates) — pre-registered as the cost side; SIR read with the absolute-count floor. |
| V6-P05 | probe-1 exact-unique recovery maintained ≥ 40% of discovered-rule RECALL episodes (the composite keeps the exact path first). |

Inference unchanged: cluster bootstrap by rule lineage; DISCOVERY ≠
REACTIVATION; verdicts applied by the compare script, never in-flight.

## 4. What V6 does NOT claim

Tolerant matching is an ALGORITHM change applied to both memory arms — a
positive P01/P02 refines V5's finding (matcher brittleness, not
representation) without vindicating "compression" per se. The P46 overlap
condition (approximate recurrence) still needs its own world change and
stays queued behind this.

## 5. Stop rules

RECALL ≥ 45 or 2 h deadline; engineering tripwires unchanged
(readback splits, entry caps, breaker, ENGINEERING_INVALID discipline).
