# Marathon findings — 12.5h × 12-era world (2026-09-30 15:45 → 10-01 04:18)

Three lines launched (frozen FULL / adaptive FULL-ADAPT / "rsi" FULL-ADAPT),
35,000+ cycles each, **0 failures across all lines**, ~175k probe events,
~1.5M charged writes drained with 0 pending (write parity held for 12.5h).

**Design note first:** the "rsi" line is a bit-identical duplicate of the
adaptive line (same seed, same config, and the launcher comment's
"selector can propose mutations at era boundaries" was never implemented —
caught by `tests/check_run_independent.py`). The marathon is therefore
TWO lines: **frozen (fixed min_frac 0.6) vs adaptive**, same world, a
legitimate paired contrast. This is the determinism lesson biting a third
time; the checker now catches it in 5 seconds.

## Finding 1 — era transitions cause ~no regression: the registry absorbs world change

Primary metric (recovery time after era boundaries): essentially **zero**.
The boundary spike (first ~60 probes) is already at era-steady level in
nearly every era (e.g. era C ε=0.40: spike 0.384 vs steady ~0.35; era B:
0.142 vs 0.152), and the trailing-window recovery criterion is met at the
first checkable window (60 probes) almost everywhere. The system is NOT
told when eras change — it doesn't need to be. Because the rule registry
keeps all discovered rules and episodes on reactivated families draw rules
it already knows, a change of world character (ε and family set rotation)
produces no catastrophic forgetting and no detectable transient.

## Finding 2 — long-horizon retention: repeat eras halve RECALL error

Rules registered in an era remain recoverable when that regime returns
thousands of cycles later:

| regime | first visit | repeat visit(s) |
|---|---|---|
| B (ε=.15, fam 0-1) | errR 0.085 (era B) | **errR 0.032** (B2 era ε=.40! and B3 0.032) |
| C (ε=.40, fam 2-3) | errR 0.198 (era C) | **errR 0.090** (C2), 0.090 (C3) |
| A (ε=.25, all fam) | errR 0.140 | A2 0.126 · A3 0.147 · A4 0.140 (flat) |

B3 RECALL error 0.032 at cycle 20k+ for rules first met at cycle 2.5k —
17,500 cycles of retention with no dedicated rehearsal beyond the
scheduler's own recurrence.

## Finding 3 — frozen ≈ adaptive at marathon scale (replicates G4′)

Paired per-era deltas (same world, 12 eras): adaptive better in 5/12,
mean delta **+0.0022** — dead even. In the four high-noise eras
(ε=0.40: C, B2, D, D2) adaptive is nominally better in 3/4, consistent
with V8's direction, but the effect is ~0.005-0.017 — inside noise.
This replicates the G4′ verdict at 14× the timescale: **the adaptive read
policy is not a meaningful improvement in this regime**; the structured
registry itself (FULL err 0.04-0.36 by era vs EPISODIC 0.10-0.46 rolling)
carries all the value.

## Engineering

12.5h × 3 lines with mid-run service respawns: 0 worker failures, write
parity `pending=0` throughout, readback fails 0. Era-wise full table:
`era_analysis.txt` alongside this file.
