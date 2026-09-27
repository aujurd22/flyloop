# flyloop — detailed design (v1, 2026-09-27)

## 0. Goal and principles

Wire FlyMemory (memory), FlyPoet (sparse-update learning) and
intuition-mechanism (prospective ledger + insight signatures) into one
self-driving cycle: **experience -> memory -> prediction -> error -> update ->
new experience -> insight**. The thing you "throw in" is a deterministic,
drifting world with recoverable ground truth; the loop must run for hours
without crashing, leave a trace on a schedule, survive crashes, and be
auditable.

Principles: no LLM inside the loop (fast, stable, zero API cost); the
prediction leg's *entire* knowledge comes from memory contents — the
memory/prediction coupling is the thing being measured; the world is a pure
function of the cycle index, so error signals are honest and crash-resume is
free.

## 1. World semantics (world.py — everything is a pure function of cycle+SEED)

| Lane | Structure | Drift schedule (deterministic) |
|---|---|---|
| fact | 24 stations (NATO word + city persona), channel in {A..E} | station i rotates every `350+30i` cycles; a shock every 1500 cycles jumps a random station 1-4 steps |
| puzzle | 4 families (red/blue/gold/silver), rule `y=(ax+b) mod 13` | family f switches (a,b) every `800+200f` cycles; epoch = cycle // period |
| seq | 16-symbol Markov stream in independent 512-symbol blocks | regime = (pos//500) % 3, three fixed transition matrices |
| noise | one unique hashed distractor entry every 20 cycles | none |

All drift is deterministic and computable ahead -> resume only needs to
restore the learners; the world jumps to the cycle index directly. That same
property lets the ledger **pre-register** predictions about drift responses.

## 2. Seven-step mapping (cycle.py)

1. **Experience** — odd cycles: a fact query (random station); even cycles: a
   puzzle probe (rotating family; one labeled exemplar plus an x whose y is
   hidden until scoring); every cycle: one stream symbol arrives. Periodic
   full-state refresh (every 600 cycles) and noise writes.
2. **Memory** — recall by compartment (`flyloop-fact` / `flyloop-puzzle`,
   top-k); v2 adds `state_lookup` for the structural arm.
3. **Prediction** (reasoner.py / poetleg.py):
   - fact: parse the latest `FLFACT` payload for the station from recall;
   - puzzle: use the family's recorded rule if present, else fit the mod-13
     linear form from the observation table (<=5 pairs) with cross-validation,
     else fall back to the most recent observation;
   - seq: a 494K-parameter k-WTA GPT (d=128, L=3, k_frac=0.25, GPU) next-symbol
     argmax.
4. **Error** — scored against world truth, one line per cycle in events.jsonl.
5. **Update** — fact corrections by state_key (in-place rewrite); puzzle
   table fold-in; discovery writes the abstracted rule and consolidates it
   with its evidence; seq gets one sparse update every 2 cycles (fixed random
   25% of every tensor trains; the rest of the gradient is zeroed — the
   "few updates x parameter partition" surviving claim, translated directly).
6. **New experience** — the world has already drifted by the next lap.
7. **Insight** (insight.py) — rule abstraction is an insight event (signature
   prediction into the ledger + memory write); drift-response tracking
   (60-cycle pre-baseline, post-window peak, recovery time); signature
   adjudication = rolling error over [d+10,d+70] <= 0.6x rolling error over
   [d-70,d].

### Ledger (prospective registration culture, after intuition-mechanism)

Five run-level predictions registered before the first cycle, adjudicated at
the end from the data:
- `P1` >=70% of fact drift events spike (post_max >= max(pre+0.10, 0.25))
- `P2` >= 8 distinct rule discoveries
- `P3` >=60% of signature entries CONFIRMED
- `P4` >=70% of seq regime shifts recover within 200 cycles
- `P5` final memory size in [2000, 40000]

Status vocabulary matches the parent repos: `REGISTERED / CONFIRMED / REFUTED /
PARTIAL` (with `RETRACTED` reserved).

## 3. Text protocol (coexisting with FlyMemory's merge semantics, measured)

- FlyMemory's merge zone (0.75 < sim <= 0.92) rewrites in place (state-fidelity
  design); a pure strengthen (>0.92, no new tokens) does not update text.
  Therefore every entity gets one state entry with a unique persona first,
  payload last; all machine-readable fields sit inside the first 80 chars.
- Puzzle: one observation table per family (`FLPAIRS`, <=5 pairs) plus the
  rule abstraction (`FLRULE`, v1) — later restructured into one global
  `RULEBOOK` entry (v2) because per-family rules collided with their tables.
- All parseable payloads live inside the 80-char recall cut; the parser is
  tolerant of the `[#id | ...] text` wrapper.

## 4. Robustness engineering (hard requirements for unattended hours)

- **Process model**: run_night.ps1 -> supervisor (detached) -> worker (child).
  The supervisor restarts crashed workers with exponential backoff (<=30),
  probes the sandbox service every 20 s and respawns it idempotently, writes
  STOP at the deadline and kills after a 240 s grace, and rebuilds the final
  report from disk (`worker --finalize`) if it is missing.
- **Worker**: per-cycle try/except; 25 consecutive failures -> checkpoint,
  exit(3) for the supervisor to restart; checkpoints every 50 cycles / 120 s;
  heartbeat 15 s; STATUS 60 s; periodic reports.
- **Service degradation**: MCP call failure -> one reconnect -> local keyword
  mirror with a background probe to switch back; the mode is recorded per
  cycle (`mode` field).
- **RAM discipline**: whole pipeline resident < 1 GB; the supervisor refuses
  restarts below 2.5 GB free; torch threads capped.
- **Resume semantics**: the world is a pure function of the cycle index, so a
  checkpoint only carries (cycle, learner weights, counters, ledger, insight
  state); events.jsonl is append-only so the error series rebuilds losslessly.
- **Isolation**: the sandbox is a third FlyMemory instance (own directory =
  own pickled DB, own port); production instances are untouched, library code
  unmodified (copied only).

## 5. Budget and pacing

Roughly 0.3-0.6 s per cycle (two HTTP round trips plus one torch step) ->
55k cycles in 10 h, ~5.5k cycles/h. Writes run ~0.4/cycle (error-driven plus
sampling), so the library reaches several thousand entries per long run; the
pickle save grows with it, which naturally slows the cycle and self-balances.

## 6. What to inspect in the morning

1. `final_report.md` — binned error curves for all lanes (expectation: fact
   and puzzle drop sharply as rules are acquired, with a spike-then-recovery
   at each drift; seq falls from the random line as training proceeds),
   ledger adjudications, insight list.
2. `reports/report_NN.md` — finer-grained drift-response tables.
3. The `mode` field in `events.jsonl` — should be `http` throughout; a `local`
   stretch means the service dropped and the supervisor reopened it.
4. `sandbox_mem/flymemory/server.log` — sandbox service log.
