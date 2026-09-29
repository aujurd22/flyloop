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

## The factorial (ε=0.25; all four cells ran the SAME exact matcher --
MATCH_MIN_FRAC was 1.0 in the V7A launcher and V5B predates tolerance; a
post-review pass corrected an earlier draft that mislabeled one comparison
as "within-tolerant" by pairing V7A cells with V6T's different-matcher run)

| cell | E20 (RECALL, discovered+all) |
|---|---|
| FULL, deep write (consec-3, V5B) | 3.621 |
| FULL-RAW, shallow write (consec-1, V7A) | 2.633 |
| MATCHED-VER, verified-gated archive (V7A) | 4.620 |
| MATCHED, cadence archive (V5B) | 4.776 |

| factor | effect | reading |
|---|---|---|
| support at raw write (sparse − full) | **+2.14** CI[+0.82, +3.44] | the only SIGNIFICANT contrast |
| support at verified write (sparse − full) | +1.00 CI[−0.26, +2.26] n.s. | same direction, n.s. |
| write depth at full support (shallow − deep) | −0.99 CI[−2.29, +0.31] n.s. | sign unconclusive at this n |
| archive gate at sparse support (verified − cadence) | −0.16 | neutral |

## Verdicts

- **V7-P01 REFUTED (as registered)**: the dominance comparison as worded
  (|F−F-RAW| < |M−M-VER| = 0.99 < 0.16) is false. The honest factorial
  statement: the only SIGNIFICANT contrast is the support effect at raw
  write (+2.14 CI[+0.82, +3.44]); the write-depth effect's sign is
  unconclusive at this n (CI crosses 0), and a post-review pass corrected
  an earlier draft's mislabeled "within-tolerant" comparison (V7A cells had
  been paired with V6T's different-matcher run) and its "~5:1" ratio.
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
support (−0.45, n.s. at this n) — but it is NOT the dominant term.
**Coverage/generalization is** — and the earlier draft's "~5:1" ratio is
withdrawn: the support effect is the only significant contrast (+2.14 at
raw write), while the write-depth effect's sign is itself unconclusive
(−0.99, CI crosses 0). The V4→V7A arc converges on:

> Under measurement noise, the recurrence advantage of rule memory over
> instance memory is driven primarily by full-input-space coverage of the
> abstraction; write-time verification is a secondary term whose sign is
> not yet resolvable at n≈50-79, with a quantified availability (probe-1
> +12pp) / poisoning (intrusions ×2.8) trade-off.

## Registered next steps

- Phase B (wavy affine world, launched this night): the P46
  instance-friendly axis — instances of the SAME rule accumulate its
  per-rule stable wave across visits while the prototype cannot express
  the wave. Order-inversion test lands ~06:47.
- BOOK_CAP sweep (the ~35% no-candidate probe-1 floor) — independent
  covariate run.
