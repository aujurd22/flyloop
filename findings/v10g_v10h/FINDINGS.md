# V10g′/h′ findings — M7.2 storage fixed (writes verified), but the derived candidate never answers its own probe-1: flag semantics puzzle registered as M7.3

Runs: 2026-10-02 18:47 → 20:53, composite world, 4 arms, CAP=5 (V10g′) /
CAP=2 (V10h′), 3826/3765 cycles, 0 failures, readback clean ×8.

## What is now VERIFIED working (counter-grade evidence)

- Derived writes: 95 per run, **0 write failures** (force_new=True fixed
  the silent-update drop).
- Derived lookups: 1900, **1699 hits** — the candidate reached the
  candidate list 1699 times (derived_cand_added counter).
- The derived candidate DOES win matches: 109-armed probes in the first
  V10g attempt, derived_use fires across all four families.

## What is BROKEN (the open puzzle)

**Composite NEW probe-1 rows: 12 per run, derived-armed = 0.** The
derivation is written at the derivation episode's own probe-1 (hook at
cycle-level before the read), the read appends the candidate with
ep = write-epoch = current epoch, and predict's early-return
(`if ep == epoch: return rule`) should fire on it — yet the returned
answer carries derived_use = 0 while often being CORRECT (err 0).

Meanwhile derived_use=1 leaks onto LATER probes of ever-derived rules
(e.g. fam-2 epoch-5 probes 4-15 after a mid-episode derivation) — the
flag tracks "rid was EVER derived" (derived_rids never prunes), not
"this answer came from the derived candidate".

Two candidate mechanisms, unresolved by inspection:
1. the early-return matched a REAL rule carrying ep == epoch (possible
   via REACTIVATION re-stamping rules at recall epochs — needs a trace
   of aux.rid on those probe-1s);
2. the flag membership fails at return time (set/identity issue).

## Registered M7.3 (next session, instrumented)

- Early-return trace: log aux.rid + the ep==epoch candidate list on
  composite NEW probe-1 (one run, 30 min).
- Flag semantics fix: derived_use must be per-ANSWER (set at the return
  site when the returned rid is the live derived candidate), never a
  never-pruned set membership.
- Then re-adjudicate transfer (V10c's clean-filter 40%, 4/10, stands as
  the M7 reference under the same polluted flag — may move either way).

## Lineage state after tonight

| mutation | verdict |
|---|---|
| M5 residual registry | ACCEPTED (same-seed + fresh-seed replication) |
| M7.1 evict-first derived | REFUTED (never stored + poison) |
| M7.2 separate derived slot | storage VERIFIED; transfer UNMEASURED (flag semantics broken) |
| M7.3 per-answer flag + trace | registered |

The composition-transfer question remains OPEN with the measurement
apparatus now honest: pipeline verified counter-grade, transfer metric
defined cleanly (NEW probe-1, derived flag, composite family), and the
single remaining unknown is a traceable return-site semantics bug.
