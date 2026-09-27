# flyloop first-run findings — `night_20260927_0143` (2026-09-27, 01:43-11:43)

## Run accounting

10.00 h / 55,173 cycles (~0.65 s per cycle), **0 failures, 0 breaker trips,
`http` mode throughout**, peak RAM well under 1 GB used. Ended gracefully:
deadline -> STOP -> worker rc=0 -> final report. No restarts.

## Final lane states

| Lane | Final rolling error | Key fact |
|---|---|---|
| fact | **0.08** | 2,122 / 2,122 drift events "recovered in 0 cycles" (median 0) |
| puzzle | **0.30** | fit predictions 19,951 with error **0.000**; rule reuse 115 with error **0.000**; cold probes 7,310 with error **1.000** |
| seq | **0.81** | did not learn at all (see below) |

Reading the error rate correctly matters: the puzzle lane's error consists
*entirely* of cold probes (cycles where the observation table could not be
parsed). Every cycle that produced a prediction — fit or rule — was exactly
right. The error is a **memory read-path reliability problem, not a reasoning
problem**.

## Finding 1 (decisive engineering negative): the 80-char truncation cuts the `c=`
## field -> 31% of the tables unparseable -> 26% cold probes

Mechanism chain (verified against a DB snapshot, not inferred):

1. FlyMemory's recall output truncates each entry to 80 chars;
2. observation-table entries (persona prefix + `FLPAIRS fam=... ep=...` + 8
   pairs) have median length 84 — the trailing `c=<cycle>` lands past the cut;
3. the loop's parser required a trailing `c=(\d+)` -> unparseable after the cut;
4. DB measurement: **4,370 / 13,989 FLPAIRS entries (31.2%)** unparseable at 80
   chars; the cut points are all of the form `':10 c='`, `':11 c='`;
5. behaviour matches: cold probes 26.1%, and families with longer tables
   (8 pairs) went cold far more often; cold runs reached 67 consecutive probes;
6. **self-lock**: a cold probe triggers a table write (error-path), the table
   gets longer, it truncates more, it goes colder.

This is not a sandbox bug — it is a real lesson for long-horizon memory systems:
**writing in more detail can poison the read path**.

## Finding 2: rule entries never survived as memory nodes

DB snapshot: 110 entries containing `FLRULE` — **0 active, all tombstones**,
and 110/110 successors were `FLPAIRS` entries. Mechanism (measured): the
same-family rule text and table text embed at **0.869** similarity — inside
FlyMemory's merge zone (0.75-0.92). Write the rule -> it rewrites the family's
table in place; write the table again -> it rewrites back. Two "different
semantics of the same entity" mutually overwrote each other. Rule reuse still
worked 115 times at zero error — by timing coincidence (the rule text happened
to be active in the recall window before the next table write), not by design.

Lesson: the two semantics of one entity need different anchors (or different
compartments); FlyMemory's merge semantics, designed for state updates, will
otherwise treat them as "a new version of the same state".

## Finding 3 (a genuine negative): the sequence lane learned nothing in 10 h

- Error oscillated 0.70-0.88 for the whole run; training loss 2.19 -> 2.29 flat.
- Theory (computed): uniform = 0.9375; context oracle (perfectly learned per-regime
  transitions, knowing the regime) = 0.6386; **marginal-only constant predictor
  = 0.9102**. The measured 0.75 means the model captured positional statistics
  (better than constant) but **not the transition structure** (far from oracle).

Diagnosis (three independent lines agree): the regimes switch every 500 steps
but the model has **no way to observe which regime it is in**; mixing three
transition kernels leaves the conditional expectation (= roughly the marginal)
as the optimum. The failure mode is **unidentifiability, not capacity,
not tuning**. This is the sandbox's first scientific output: learning systems
fail this way — *because the task was not identified from the input*, not
because the model was too small.

## Ledger adjudications (115 signatures: 61 CONFIRMED / 54 REFUTED; run level 3/5)

| Prediction | Verdict | Evidence |
|---|---|---|
| P1: >=70% of fact drifts spike | **REFUTED** | 0/2,122 spiked — the memory lane's 0-cycle recovery was stronger than predicted |
| P2: >= 8 rule discoveries | **CONFIRMED** | 115 |
| P3: >=60% signatures CONFIRMED | **REFUTED** | 37/115 (cold probes polluted the pre-window) |
| P4: >=70% seq shifts recover <= 200 c | **CONFIRMED** | 97/109 (the rolling window smoothed away the fact that nothing was learned) |
| P5: final size in [2000, 40000] | **CONFIRMED** | 20,977 |

**P1's refutation is the most valuable run-level result**: I predicted memory
inertia (spike-then-recover at drift); measured 2,122 drifts all recovered in
0 cycles with no spike. The system's memory inertia is *far lower than
intuition*. **P4's confirmation must be discounted**: the long rolling window
produced a "confirmation illusion". Window choice can matter more than the
result itself — a methodological lesson carried into v2 (three-window
consistency rules).

## Data assets preserved here

- `final_report.md` — 5k-cycle binned curves, drift-response tables, insight list, ledger table.
- `ledger.jsonl` — 115 prospective predictions with adjudications.
- `events_sample.jsonl` — first 2,000 cycles of the 55,173-cycle per-cycle record
  (the full record is regenerable from a rerun; it is 5.6 MB).
- `state.json` — the final checkpoint (counters, discovery table, insight state).

The run also served as a **soak test for FlyMemory itself**: 20,977 entries,
74 MB pickle, 10 h of continuous writes — no deadlocks, no corruption, mean
save 0.17 s, cycle time creeping 145 -> 180 ms as the pickle grew.

## Rerun recommendations (priority order, all implemented in v2)

1. **Fix the truncation**: table capacity 8 -> 5 pairs, `c=` moved to the front,
   pairs *first* so a cut can only remove trailing metadata; write-then-read-back
   verification. Expected: cold rate 26% -> <5%, puzzle error 0.30 -> ~0.05.
2. **De-anchor the rules**: one global `RULEBOOK` entry read via the
   non-truncating `state_lookup`, calibrated against the real emitters.
3. **Give the sequence lane identifiability**: prefix a regime-marker token
   (dual-stream A/B); otherwise the lane forever measures "optimal prediction
   under unidentifiability", and learning the transition structure is not
   expected behaviour.
