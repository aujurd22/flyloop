# V7 Phase A findings — the 2×2 factorial: support dominates, verification is a minor term with a quantified trade-off

Run: 2026-09-29 02:42 → 04:42, stopped by operator policy at the 2 h cap
(9528 cycles, 0 failures, full http/http, ~3.5-3.8k entries per store).
Arms: FULL-RAW (rule registry, shallow verification consec-1) vs
MATCHED-VER (sparse archive, verified gate) — paired cross-run with V5B
(FULL verified / MATCHED raw) as the other two cells of the 2×2.

**First run of the pair was invalidated by a harness bug** (memory-read arm
conditions still gated on old arm names — both new arms wrote memory but
never read it back, collapsing into identical fit-only arms, E20 identical
to the digit 4.759 = 4.759). The bug itself provided an unintended control:
write policy with no memory reads has zero behavioral effect.

## The clean within-tolerant-matcher factorial (ε=0.25)

| cell | E20 (RECALL, discovered+all) |
|---|---|
| FULL, deep write (consec-3, V6T) | 2.347 |
| FULL-RAW, shallow write (consec-1, V7A) | 2.633 |
| MATCHED-VER, verified-gated archive (V7A) | 4.620 |
| MATCHED, cadence archive (V5B) | 4.653 |

| factor | effect | reading |
|---|---|---|
| support (sparse − full) | **+2.2-2.3** | dominant, robust to write policy |
| write depth at full support (shallow − deep) | +0.45 (se 0.31, n.s.) | deep mildly better |
| archive gate at sparse support (verified − cadence) | −0.03 | neutral |

## Verdicts

- **V7-P01 REFUTED (as registered) — and the refutation is the result**: the
  dominance comparison as worded was confounded (cells differed in matcher
  regime too). The clean factorial says **support size dominates the
  write-verification factor ~5:1** (2.2-2.3 vs 0.45 n.s.).
- V7-P02 PARTIAL: verified-gated archiving at sparse support ≈ neutral
  (−0.03 within tolerant).
- V7-P03 CONFIRMED: epi_test 44→60, book_test 151→174 — both paths live.
- **V7-P04 CONFIRMED — the trade-off quantified**: shallow writes triple
  stale intrusions (first-20 window: **150 vs 53**) while lifting probe-1
  recovery (51.3% vs 38.8%). Availability and poisoning move together.
- V7-P05 CONFIRMED: shallow-write probe-1 recovery 51.3% ≥ 40% band.

## The refined law

V5's "write-time verification is the noise filter" survives in weakened,
precise form: deep verification is mildly better than shallow at full
support (+0.29-0.45, n.s. at this n) — but it is NOT the dominant term.
**Coverage/generalization is.** The three-run arc (V5 exact / V6 tolerant /
V7 factorial) converges on:

> Under measurement noise, the recurrence advantage of rule memory over
> instance memory is driven primarily by full-input-space coverage of the
> abstraction; write-time verification is a secondary term with a
> quantified availability (probe-1 +12pp) / poisoning (intrusions ×2.8)
> trade-off.

## Registered next steps

- Phase B (wavy affine world, launched this night): the P46
  instance-friendly axis — instances of the SAME rule accumulate its
  per-rule stable wave across visits while the prototype cannot express
  the wave. Order-inversion test lands ~06:47.
- BOOK_CAP sweep (the ~35% no-candidate probe-1 floor) — independent
  covariate run.
