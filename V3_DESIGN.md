# DESIGN V3 — Recurrent Drift × Memory Consolidation

Status: pre-registered before launch. Code landed first (commit history is the
pre-registration), run dir carries `world_schedule.json` and a `ledger.jsonl`
with V3-P01..P08 registered before cycle 1. Verdicts are applied by
`experiments/analyze_v3.py` after the run, never in-flight.

## 1. The question

Not "can it run long" (v2 answered that: 46134 cycles, 0 failures) but:

> Does structured memory change future behavior — and does remembering more
> risk confusing the past with the present?

Measured over repeated rule recurrence under escalating noise pressure, with a
clean paired control.

## 2. Two memory arms, one world

| | FULL (F) | EPISODIC (E) |
|---|---|---|
| observation tables | yes | yes |
| RULEBOOK (per-family rule registry) | yes | **never** |
| state/history | yes | yes |
| padding writes | book writes | byte/count-matched pads (`PadSync`) |

Both arms run in ONE worker process, back-to-back per cycle, each talking to
its OWN sandbox FlyMemory instance (separate process + pickle: FULL on
`MEM_PORT`, EPI on `MEM_PORT_EPI`). Separate stores are mandatory — the merge
zone ignores compartments, so same-persona texts from the two arms would
collide in one store. Cross-arm recall is impossible by construction.

The recurrence shortcut under test: at an episode start the FULL arm may test
recent book candidates against live observations — ONE confirming pair adopts
an old rule (`book_test`, unique-match required); the EPI arm must re-fit from
TWO fresh pairs. `rule` = a book rule already re-activated at this epoch.

## 3. World: recurrent episodes

Each family walks a precomputed schedule (pure function of SEED, identical for
both arms, saved as `world_schedule.json` before cycle 1):

- **NEW (50%)** — fresh (a,b), never used in this family; first-learning cost
- **VARIANT (25%)** — fresh params drawn NEAR the previous rule; the
  stale-memory trap and NC1 negative control
- **RECALL (25%)** — the exact rule from k ∈ {2,3,4,5} epochs ago; THE
  statistic unit. `rule_age` = k.

Distractor pressure in three phases fixed before launch (`config.NOISE_PHASES`):
cycles 0–30k `NOISE_EVERY=20`, 30k–60k `=10`, 60k+ `=5`.

## 4. Fairness constraints

Same world schedule, same probes (paired by family/epoch/probe_idx), same
observations, same table-write policy; separate stores; identical SEED. The
FULL arm's book writes are mirrored by the EPI arm with byte-exact padding
writes (`PadSync` charges bytes, EPI drains one pad per cycle; smoke test
asserts pads == books and pad_bytes == book_bytes exactly). Padding text uses
its own head and a single shared state key so it merges in place like the
book does.

## 5. Endpoints

Each RECALL episode is one statistical unit; FULL and EPI probes are paired by
(family, epoch, probe_idx). `E20` = errors in the first 20 probes; `latency` =
first correct probe (capped at 21). Paired bootstrap CIs + sign-flip
permutation tests; effect size, 95% CI, raw counts.

- **V3-P01 (primary)**: E20 on RECALL lower for FULL; paired CI excludes 0.
- **V3-P02 (primary)**: latency on RECALL shorter for FULL; paired CI excludes 0.
- **V3-P03**: the advantage holds in every gap bucket 2/3/4/5.
- **V3-P04 (NC1)**: |dE| on VARIANT clearly smaller than on RECALL — the
  advantage is recurrence reuse, not generic smartness.
- **V3-P05**: SIR(FULL) <= 1.5 x SIR(EPI), where SIR = stale-intrusion
  errors / first-20 probes after episode starts. Remembering more must not
  mean mistaking the past for the present.
- **V3-P06**: useful-insight rate (discoveries whose rule later pays off on a
  recurrence) above a permutation null — "discovery" only counts as insight
  when future prediction improves (the FlyLoop-side analog of P32-h/P34-d:
  recognition is not novelty; an event is not insight).
- **V3-P07**: FULL degrades slower than EPI from noise phase A to C.
- **V3-P08 (NC2)**: fact lane (recall vs state_lookup) shows no regression
  under the v3 policy.

The seq lanes (A/B streams) run identically in both arms as a
CONTINUAL-LEARNING CONTROL (V3 §10: the v2 result settled the observability
question; seq does not carry verdicts this round). **FlyMemory Dream is NOT
part of this run** — dream-v2 (window → relation → prediction → verifiable
delta) is an unimplemented RFC; claiming it would be fraud. V3 tests
structured memory / recurrence / stale control, nothing else.

## 6. Stop rules

All quotas met (NEW >= 150, VARIANT >= 75, RECALL >= 75, shocks >= 100), or
the 10 h deadline, or: 25 consecutive failures / invariant violation / memory
corruption / poet checkpoint failure -> the run is marked
**ENGINEERING_INVALID** (state.json `run_status`), which voids it as a
hypothesis test WITHOUT scoring it as a hypothesis negative. analyze_v3.py
refuses to adjudicate endpoints on an invalid run.

## 7. Hard knowledge baked in (do not regress)

1. **split_chunks x state_key atomicity**: the engine splits texts > 120 chars
   into multiple chunks and then REJECTS state_key writes that produce more
   than one chunk. An unbounded registry silently stopped updating at ~120
   chars in smoke_v3_1790532091 (14/27 book writes dead, tool layer reported
   it as a bare "too similar"). Hence: per-family book entries, capped at
   BOOK_CAP=5 most recent rules, < 120 chars forever. RECALL gaps are 2-5, so
   the cap loses no recurrence coverage.
2. **Cross-family book similarity**: family books share the numeric payload
   format, and ASCII family words (red/blue/...) do not separate embeddings —
   cross-family book sim measured 0.90-0.93, deep inside the merge zone (the
   v1 "rule swallowed by table" failure mode reborn). Fix: distinct CJK head +
   a CJK family tag on every rule line (红家/蓝家/金家/银家); measured 0.655
   cross-family, 0.98 same-family update, 0.73 book-vs-table. See
   tests/calibrate_texts.py.
3. **superseded_by=0 is falsy** — active-entry audits must use `is None`.
4. **table dict keys are str** after a JSON state round-trip; the reasoner
   needs int pairs (obs built with int(k)).
5. Everything from v2: payload-first formats (80-char recall truncation),
   real-emitter calibration before launch, state_lookup reads untruncated.
