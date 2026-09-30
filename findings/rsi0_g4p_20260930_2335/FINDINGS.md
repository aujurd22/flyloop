# RSI-0 G4′ findings — the TRUE replication: adaptive-policy gain does NOT survive; structured-memory advantage does

Run: 2026-09-30 23:35 → 10-01 01:38, 2 h cap, 5258 cycles, **0 failures**.
Config: identical to G3 (FULL-ADAPT / MATCHED / EPISODIC, ε = 0.25, adaptive
min_frac on 0.6 base), **FLYLOOP_RUNSEED = 20260930** — same schedule, fresh
realizations. Independence: diverges from G3 at event 9 of 5000
(`tests/check_run_independent.py` PASS; 61.4% trivial coincidence from shared
schedule positions is expected).

## Headline: the G3 improvement is within realization noise

| comparison | paired ΔE20 | cluster CI | verdict |
|---|---|---|---|
| G3 − g0 parent (original) | −0.347 | excl. 0 | the basis of G3's acceptance |
| **G4′ − g0 parent (replication)** | **+0.163** | **[−0.976, +1.380]** | **n.s., sign undetermined** |
| G4′ − G3 | +0.628 | [−0.512, +1.841] | n.s. |

Per-run E20 (discovered-rule RECALL episodes, cluster bootstrap):
g0 2.347 · G3 2.000 · **G4′ 2.581** CI[1.528, 3.804] (n_ep=43).

Mean effect across the two realizations ≈ −0.09 — consistent with zero.
**G3's acceptance is downgraded to single-realization evidence.** The
lineage must not treat "adaptive read policy" as an established
improvement; it is a registered hypothesis whose effect, if real, is
smaller than run-to-run realization noise in this world.

## What DID replicate, strongly

The original program-level finding — structured rule memory beats episodic
archive beats nothing — is robust across independent realizations:

| arm | E20 (G4′) |
|---|---|
| FULL-ADAPT (rule registry) | **2.581** |
| MATCHED (episodic archive) | 5.186 |
| EPISODIC (no memory) | 5.372 |

Rolling err100 tells the same story: 0.24 vs 0.46 vs 0.46; discoveries 121
vs 0 vs 0. The ~2.5-3× structured-memory advantage survives a full change
of realization (new probe draws, new noise flips, new poet init). The
effect that built this program is not a seed artifact — precisely the thing
the retracted G4 could never have shown.

## Method note: why this run exists at all

The original G4 was retracted (bit-identical prefix of G3 — the world is a
pure function of C.SEED and there was no run-level seed). G4′ is the first
run under the seed split: schedule keys stay on C.SEED (episodes pair
across runs, making the paired contrasts above possible), realization keys
read C.RUN_SEED. Standing rule, now load-bearing: **paired contrasts want
the same seed; replications want a fresh one.**

## Consequences for the RSI-0 loop

1. G3's mutation stays IN the lineage config (it is not harmful), but its
   "accepted" flag carries the annotation: single-realization, not
   replicated.
2. The improvement menu was already exhausted (M1 struck on merit; M2/M4
   absorbed into the parent config; M3 control-only). G4′ adds the sharper
   conclusion: the remaining knob-space within this world/matcher regime is
   inside realization noise. The next accepted mutation must come from a
   NEW AXIS (registered: abstraction-loss world / V9 design), not from
   re-tuning these knobs.
3. Positive selection evidence in RSI-0 now reads: one accepted mutation
   whose gain failed independent replication + two merit rejections. The
   loop's negative selection (rejecting M1/M2) remains its most reliable
   faculty — consistent with the program-wide theme that rejection/
   filtering, not generation, is where the leverage is.

## Engineering

0 failures across the run; write parity drained (FULL 1654 / MATCHED 1975 /
EPI 2110 writes incl. pads); readback fails 0 across all lanes; RAM stayed
≥ 7.4 GB despite co-running with the 3-line marathon (15 services) — the
0.0 GB reading earlier was a transient store-snapshot serialization spike.
