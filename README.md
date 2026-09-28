# flyloop

**A closed-loop sandbox wiring three research projects into one learning cycle:**
`experience -> memory -> prediction -> error -> update -> new experience -> insight`

flyloop is the mechanical orchestrator for the **Mushroom-Body Program** — the
research line that asks *when does compression induce structure?* It connects
three organs that were previously studied only in isolation:

| Organ | Repo | Role in the loop |
|---|---|---|
| **Memory** | [aujurd22/flymemory](https://github.com/aujurd22/flymemory) | storage, recall, dedup, supersede, consolidation — *all* prediction knowledge comes from here |
| **Proposer** | [aujurd22/flypoet](https://github.com/aujurd22/flypoet) | k-WTA sparse-competition networks, trained online (few updates x partitioned parameters) |
| **Verifier** | [aujurd22/intuition-mechanism](https://github.com/aujurd22/intuition-mechanism) | registered-prediction ledger culture; restructuring-signature measurement |

There is **no LLM in the loop** — every step is mechanical, the world is a
pure function of the cycle index, and every error signal has recoverable ground
truth. The point is to measure the *dynamics* of memory-driven prediction under
drift: the phase-transition laws (L3), failure laws (L4/L5), and the
`PROPOSE -> REGISTER -> RUN -> VERIFY -> RECORD -> REMEMBER` cycle described in
flymemory's [research/LOOP.md](https://github.com/aujurd22/flymemory/blob/main/research/LOOP.md)
— with `propose` left to the human/LLM session boundary, everything else automated.

## The loop

One iteration per cycle (~0.09 s per arm pass; the V3 run sustains ~4,800
cycles/hour with both arms and their poets):

```
1 EXPERIENCE  the world emits events: a station's channel query,
              a hidden-rule puzzle probe, the next symbol of a stream
2 MEMORY      recall the relevant compartment from FlyMemory
              (or a direct state_lookup in the V4 arm)
3 PREDICT     mechanical reasoner (vote / mod-13 fit / recorded rule)
              or the k-WTA net's next-symbol argmax
4 ERROR       score against the world's ground truth
5 UPDATE      correction writes / table fold-in / rule abstraction /
              one sparse gradient step (25% partition, k-WTA 0.25)
6 NEW EXPERIENCE  the world has drifted under our feet (rotations, shocks,
              regime shifts) — the next lap starts on new ground
7 INSIGHT     rule-abstraction events and drift-response statistics are
              written to the registered ledger and back into memory
```

### Lanes

- **fact** — 24 stations whose channel state rotates on staggered periods,
  plus shocks. Tests state tracking under drift; A/B arm compares semantic
  `recall` (arm A) against V4 `state_lookup` structural read (arm B).
- **puzzle** — 4 families of `y = (a x + b) mod 13` with epoch rotations.
  The loop must *abstract* a rule from observed exemplars into memory
  (a "discovery"), then reuse it. Discoveries are insight events.
- **seq** — a 3-regime Markov stream, predicted online by a 494K-parameter
  k-WTA GPT (dual streams: A hides the regime = unidentifiable task;
  B prefixes a regime marker = identifiability arm).
- **noise** — unique distractor entries every 20 cycles, exercising
  dedup/decay under write load.

### Registered predictions

Every run pre-registers its claims *before the first cycle* (git timestamps
are the proof, LOOP.md style): run-level predictions (`V2-P01`..`V2-P10`) plus
per-discovery signature entries. The final report adjudicates each to
`CONFIRMED / REFUTED / PARTIAL` with evidence — never post-hoc thresholds.

## Results so far

### Run 1 — `night_20260927_0143` (10 h, 55,173 cycles, 0 failures)

Three findings, all unplanned ([full report](findings/night_20260927_0143/FINDINGS.md)):

1. **The 80-char truncation self-lock.** FlyMemory's recall truncates entry
   text to 80 chars; 31.2% of the observation-table entries were cut inside
   their trailing `c=` field, making them unparseable -> 26% "cold" probes,
   which write *longer* tables, which truncate *more*. A long-horizon memory
   system reality: **writing in more detail can poison the read path**.
2. **Rules never survived as nodes.** Per-family rule entries measured 0.869
   similarity against their own observation table — inside FlyMemory's merge
   zone (0.75-0.92), where rewriting is *in-place regardless of compartment or
   state_key*. All 110 rule entries became tombstones.
3. **The sequence lane's null result was identifiability, not capacity.**
   With three regimes mixed and no observable marker, the optimal predictor is
   the marginal one (theory: uniform 0.9375 / marginal 0.9102 / oracle 0.6386;
   measured 0.75-0.87 flat). A clean negative result: *this failure mode is
   unidentifiability, not underfitting.*

The run also served as a **soak test** for FlyMemory itself: 20,977 entries,
74 MB pickle, 10 h of continuous writes, zero corruption, mean save 0.17 s.

### Run 2 — `night_20260927_1228` (5 h, v2 fixes)

| Metric | v1 | v2 |
|---|---|---|
| cold-probe rate | 26.1% | **4.0%** |
| rules surviving as parseable memory | 0 / 110 | **4/4 families in one RULEBOOK entry, 0 read-back failures** |
| fact arm B (state_lookup) error | n/a | **0.18 vs arm A 0.28** |

Verdicts `V2-P01..P10`: 7 CONFIRMED / 2 PARTIAL / 1 REFUTED. The seq null
result *survived* the identifiability repair (marked stream B ≈ unmarked A),
which upgraded it: the bottleneck is the small poets' aggregate learning, not
information availability ([full report](findings/night_20260927_1228/FINDINGS.md)).

### Run 3 — `v3_20260928_0252` (10 h, V3: recurrent drift × memory consolidation)

The first controlled mechanism experiment: two memory arms through the
**identical** precomputed episode schedule (NEW 50% / VARIANT 25% / RECALL
25%, gaps 2–5 epochs), FULL with a per-family rule registry, EPISODIC with
tables only, byte-exact padding-write parity. Each arm has its own sandbox
FlyMemory instance (ports 8769/8770).

| Verdict | Claim | Result |
|---|---|---|
| **P01 ✓** | FULL lower error on RECALL (primary) | dE20 = **+0.641**, cluster-bootstrap CI [0.521, 0.776], n=78, perm_p<1e-4, 4/4 families positive |
| **P02 ✓** | FULL faster recovery (primary) | latency **+0.551** probe, cluster CI [0.426, 0.693] |
| **P03 ✓** | advantage at every gap 2/3/4/5 | +0.47 … +0.75, all positive |
| **P04 ✓** (NC1) | advantage absent on VARIANT/NEW | \|dE\| 0.014 / 0.02 vs 0.641 — **pure reuse signature** |
| **P05 ✓** | stale intrusion within band | SIR ratio **1.42** ≤ 1.5 — memory benefit and memory interference are the same mechanism's two faces |
| P06 ✗ | useful-insight rate above null | **REFUTED after correction** (external review found no temporal check / REACTIVATION conflation; corrected statistic equals its null; the decisive discovered-vs-undiscovered contrast is untestable — FULL abstracted 100% of rules) |
| P07 / P08 — | noise-phase / fact-lane controls | INCONCLUSIVE (phase C beyond the reachable 48.3k cycles; design mis-calibration registered) |

Mechanism, resolved from the data: recovery is a **one-observation story** —
FULL adopts a returning rule from a single live pair (`book_test`, unique
match required) at probe 2, while EPISODIC needs two pairs to fit at probe 3.
Zero-observation recovery never happened (0/78). Full analysis, corrections
trail, and the V4 queue: [findings/v3_20260928_0252](findings/v3_20260928_0252/FINDINGS.md),
[V3_DESIGN.md](V3_DESIGN.md).

## Engineering discipline (read this before writing to a memory system in a loop)

Two live bugs were caught by pre-launch audits, and both generalize:

- **Calibrate with the real emitters, not approximations.** The first v2 draft
  calibrated similarity with hand-written *approximate* texts; the actual
  emitters crossed the 0.75 merge line at runtime and rules were swallowed.
  Every text form is now calibrated by `tests/calibrate_texts.py` against the
  actual embedder with hard constraints: distinct entities `< 0.75`,
  same-entity update `> 0.75`, own-entity query ranks first.
- **Make truncation unable to fabricate data.** Recall cuts at 80 chars; a cut
  can turn `12:10` into `12:1` — a malformed observation that silently poisons
  the fit. v2 puts observation pairs *first* so a cut can only remove trailing
  metadata. `tests/test_parsers.py` fuzzes every emitted form under the exact
  80-char cut.

Robustness for unattended multi-hour runs: per-cycle try/except with a
consecutive-failure circuit breaker, atomic checkpoints every 50 cycles,
heartbeat/status/report cadence, local-mirror degradation when the memory
service dies (with auto-switch-back), RAM red line, sleep guard, and a
logon-resume hook so a reboot continues from the checkpoint (the absolute
deadline lives in `deadline.json`).

## Repository layout

```
flyloop/            the loop implementation
  config.py         all knobs, thresholds, quotas, calibrated text data
  world.py          deterministic world: facts / puzzle / sequence / noise
  memclient.py      async MCP client to the sandbox FlyMemory + local mirror
  reasoner.py       mechanical predictors + strict parsers
  poetleg.py        k-WTA GPT leg (imports FlyPoet's train_v2.GPT)
  insight.py        drift-response tracking, insight detector, ledger
  cycle.py          the seven-step cycle
  worker.py         run loop: checkpoints, quotas, adjudication, reports
  supervisor.py     process supervision, keep-awake, finalize-from-disk
tests/
  test_parsers.py       truncation fuzzing of every emitted text form
  calibrate_texts.py    pre-launch similarity calibration (hard constraints)
findings/
  night_20260927_0143/  curated artifacts from run 1 (report, registry, findings)
DESIGN.md           v1 design: world semantics, seven-step mapping
DESIGN_V2.md        v2 design: fixes, A/B arms, governance upgrades, duration policy
README.md           this file
```

## Usage

Requirements: Windows (the supervision layer is PowerShell/ctypes), Python 3.13
with `mcp`, `torch`, `sentence-transformers`; a FlyMemory checkout reachable
for the sandbox instance; a FlyPoet checkout for the `train_v2` import.

Paths default to the repository layout and can be overridden with environment
variables: `FLYLOOP_PYTHON` / `FLYLOOP_PYTHONW` (interpreter with the
dependencies), `FLYLOOP_ROOT` (repo root), `FLYLOOP_FLYPOET` (FlyPoet
checkout), `FLYLOOP_PORT` (sandbox memory port, default 8767).

1. Copy the FlyMemory package into `sandbox_mem/flymemory/` (an isolated
   third instance: own pickled DB, own port — never the production instance).
2. Run the gates: `python tests/test_parsers.py` and
   `python tests/calibrate_texts.py` — both must pass before any launch.
3. Smoke: `python -m flyloop.worker --run-dir runs/smoke --max-cycles 200 --duration-h 0.5`
4. Overnight: `powershell -File run_night.ps1` (starts the sandbox service, then
   the supervisor detached; monitor `runs/<id>/STATUS.md`; stop gracefully by
   creating a `STOP` file in the run directory).

All text content written to memory is intentionally multilingual (the
embedder is multilingual and CJK prose is the realistic surface); code,
comments, and documentation are English.

## Duration policy

Time is a ceiling, not a goal — events are bought by statistics. Empirically:
2-3 h covers the engineering-verification tier; 5-6 h satisfies the full
prediction set (shock counts, discovery counts, recovery distributions);
10 h buys a long-stability claim. Prefer *accelerating the world's clock*
(shorter rotation/shock periods, more gradient steps per cycle) over longer
wall-clock runs, and prefer two 5 h runs with a design change in between over
one 10 h run. See DESIGN_V2.md section 8.

## License

MIT. The three component repos have their own licenses.
