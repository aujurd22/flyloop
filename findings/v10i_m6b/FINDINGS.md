# M6b PRE-REGISTER: dense-PERIODIC world (window fix for M6)

**Registered 2026-10-06 00:15, before any M6b run.** M6 (v10i_m6) was
adjudicated INCONCLUSIVE by its own opening condition: the 8h world
gives PERIODIC rules at most 7 RECALL visits (world_schedule.json,
runs/m6_m5_base), while the delta-recurrence requires k >= 13
(gcd(delta,13)=1 => b recurs at visit k+13). The gate stack, noise,
and hypothesis are UNCHANGED from v10i_m6; only the world tempo
changes so the recurrence is actually reachable.

## Manipulation (world tempo only)

- PUZ_PROBE_CADENCE 8 -> 2 (episode cycle span x1/4)
- EPISODE_PROBE_WEIGHTS shifted short: [0.30, 0.30, 0.20, 0.15, 0.05]
  (mean probe count ~9 vs ~19; episode span x~1/2)

Expected joint effect: >=3x more episodes per wall-hour with shorter
ones => PERIODIC visit k reaches 13+ within 8h (density estimate from
seed-1 schedule: 300 episodes/8h -> ~900+ shorter episodes; PERIODIC
share 1/4 => ~225 PERIODIC episodes over a smaller rule pool =>
visit counts well past 13).

## Hypothesis & adjudication (unchanged from v10i_m6)

Error-triggered delta retrieval recovers the historical b at
recurrence (k >= 13) instead of re-learning. PRIMARY: PERIODIC
err100 on visits k >= 13, paired M6b-delta minus M6b-base.
Opening conditions unchanged: CI excludes 0 with M6b better =>
delta earns retrieval rights; otherwise RETRACTED (structural
rights only). Numbers read from run counters/events JSONL.

## Runs

Two realizations (G4' rule): seed1 local (RUNSEED default) and seed2
cloud (RUNSEED=20261006), 4 arms are NOT needed -- only FULL-RES
base vs FULL-RES+delta (2 runs per realization). 8h cap, same as M6.
