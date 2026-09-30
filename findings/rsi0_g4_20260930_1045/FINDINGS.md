# RSI-0 G4 findings — **RETRACTED as a replication** (deterministic duplicate)

Run: 2026-09-30 10:45 → 12:45, 2 h wall cap (hit the cap at cycle 5490),
0 failures. Config: identical to G3 (FULL-ADAPT / MATCHED / EPISODIC,
ε = 0.25, min_frac 0.6 + adaptive adjust).

> **RETRACTION (2026-09-30 evening).** The original version of this file
> claimed "the adaptive policy replicates its win in a fresh run
> (1.917 vs parent 2.375)" and "confirmed in TWO independent runs". Both
> claims are **withdrawn**. Verification with
> `tests/check_run_independent.py` shows G4's puzzle-lane event stream is
> **bit-identical to G3 on the entire common prefix** — 6000/6000 events,
> no divergence point. G4 is G3's deterministic trajectory truncated earlier
> by the 2 h wall; its E20 differs (1.917 vs 2.000) only because the wall cut
> off 10 late-run episodes (n_ep 48 vs 58). The paired contrast vs the g0
> parent (−0.458, CI [−0.644, −0.262]) is real but is **G3's effect
> re-measured**, not independent evidence.

## Root cause

Every stochastic quantity in flyloop was a pure function of
`("flyloop", C.SEED, *key)`: episode schedule, probe draws, noise flips,
wave phases, poet init. A same-config re-run replays the parent
bit-for-bit — with no run-level seed, "run it again" is indistinguishable
from "keep the old logs". G5 (launched 15:06 as a second replication attempt)
had the same defect and was killed at 0.6 h when the marathon launched.

## Fix (landed with this retraction)

1. **`FLYLOOP_RUNSEED`** (`config.py C.RUN_SEED`): realization seed for probe
   draws, noise flips, wave phases, poet init. Structure keys
   `("puz","sched",…)` stay on `C.SEED`, so the schedule (and thus the
   episode pairing keys) is bit-identical across runs — verified: 300/300
   schedule episodes identical, probe realizations fully independent.
2. **Preflight check #5**: a launch declaring `FLYLOOP_REPLICATE_OF=<parent>`
   without a fresh `FLYLOOP_RUNSEED` FAILS the gate.
3. **`tests/check_run_independent.py`**: post-launch mechanical check that a
   replication is not a bit-prefix of its parent (exit 1 on identity).

## What survives

- **G3's acceptance stands.** Its evidence is the paired contrast against the
  g0 parent (different system config, same world) — a legitimate paired
  design that *wants* the shared world. The −0.347 improvement, probe-1 hit
  rate +4.3 pp, and the stale-intrusion trade-off are untouched.
- **The ε dose-response result in this file's earlier version is REAL** (it
  came from `v8d15_20260930_1045`, a different-config run, and the follow-up
  sweep — J-shaped curve, ε ≈ 0.05–0.15 optimal). It lives in
  `findings/v8_dose_response/` and is unaffected by this retraction.

## What was lost

Independent replication of the adaptive-policy effect. **G4'** (same config,
`FLYLOOP_RUNSEED=20260930`) is queued as the true replication; it must PASS
`check_run_independent` against G3 before "replicated" language is used.

## Prevention (the general lesson)

Run the independence check BEFORE claiming replication anywhere in the
program, and treat "paired contrast" and "independent replication" as
different evidence classes with opposite seed policy: contrasts want the
same seed; replications want a fresh one.

---

**RESOLUTION (10-01 01:40).** The queued G4′ ran to completion as the true
replication (`findings/rsi0_g4p_20260930_2335/FINDINGS.md`): independent
realizations PASS the check, and the G3 gain did **not** replicate
(+0.163 vs parent, CI [−0.976, +1.380], n.s.). The structured-memory
advantage replicated strongly. See the G4′ findings for the full
adjudication and lineage consequences.
