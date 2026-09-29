# V7C findings — the write-depth sign resolves: shallow write beats deep write under noise

Run: 2026-09-29 19:40 → 22:10, 2.5 h cap, two arms (FULL deep-write consec-3
vs FULL-RAW shallow-write consec-1), exact matcher, ε = 0.25, same
seed/schedule as V7A — a PURE write-depth A/B with zero confounds (unlike
V7A, whose F-RAW cell had been compared against V6T's different-matcher run).

## Result: shallow write SIGNIFICANTLY beats deep write

| arm | E20 (RECALL, n=58) |
|---|---|
| FULL-RAW (shallow, consec-1) | **2.931** |
| FULL (deep, consec-3) | 3.586 |
| EPISODIC reference (live fit) | 4.914 |

Paired difference (shallow − deep): **−0.655, cluster CI [−1.102, −0.169] —
excludes zero.** Probe-1 correct: FULL 44.8%, FULL-RAW 50.0%, EPISODIC 8.6%.

Two independent runs agree: V7A (−0.99, CI crossed at n=49-58), V7C (−0.66,
CI excludes at n=58). Pooled direction is unambiguous.

## Verdicts

- **V7C-P01 CONFIRMED**: the write-depth sign resolves — SHALLOW wins. This
  REFUTES V5's mechanism claim ("write-time verification is the noise
  filter") in its write-depth form: deeper write-time verification is a net
  COST under noise, not a benefit. The filter is at READ time (exact
  reproduction of live pairs by the matcher — wrong stored rules fail live
  reproduction and fall through to fitting); write-time verification only
  DELAYS availability.
- The V5-era reading ("verification filters noise at the write") is
  corrected to: **read-time exactness is the filter; write-time depth is an
  availability delay.**

## Law status after this run

1. **Support/coverage is the dominant term** (+2.14 significant at raw
   write; V7A/V7C agree) — retained.
2. **Write-depth: shallow ≥ deep under noise** (significant in V7C) —
   V5's "verification filters noise at write" is REFUTED in direction.
3. **Registry size has an optimum**: G2's cap-13 per-rule book (3.660) was
   WORSE than cap-5 single-entry (2.347) — more stored candidates under
   noise = more wrong-candidate false matches at read time. The availability
   /poisoning trade-off is registry-size dependent.

## Registered next

- The verified/shallow × support-size interaction (Phase A's n.s. +1.00 vs
  significant +2.14) needs one more n-doubling before any claim about the
  interaction sign.
- The truth-noise variant (wave on TRUTH, no exact rule exists) remains the
  strongest un-tested instance-friendly condition (V8).
