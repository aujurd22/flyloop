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

### Run 4 — `v4_20260928_1636` (1.9 h, V4: discovery-failure × disentanglement, early stop)

Three arms: FULL / **MATCHED** (episodic pair-table archive + the SAME
unique-match decision rule — pure algorithm control) / EPISODIC; variable
episode lengths create rules that never get abstracted.

| Verdict | Claim | Result |
|---|---|---|
| **P02 ✓** (disentanglement) | F ≤ M ≤ E on discovered recurrences | E20 = 0.43 / 0.57 / 1.06 — the matcher adds +0.49 (CI excludes 0), compression only +0.14 (CI crosses 0) |
| **P04 ✓** | probe-1 recovery exists | 62.7% (pre-folded interface; V3's 0/78 was a folding-order artifact) |
| **P06 ✓** (NC1) | VARIANT/NEW contrasts ≈ 0 | the advantage stays recurrence-specific |

[findings/v4_20260928_1636](findings/v4_20260928_1636/FINDINGS.md)

### Run 5 — `v5b_20260928_1848` (2 h, V5: the condition law, ε=0.25)

| Verdict | Claim | Result |
|---|---|---|
| P01 PARTIAL | ε=0 replication | dE20(M−F) = +0.137 CI[−0.043, 0.310] |
| **P02 ✓** (headline, operational) | dE20(M−F) larger at ε=0.25 | **+1.155** CI[0.755, 1.571]; between-run contrast +1.018 CI[0.584, 1.472] |
| P03 ✓ | discovery rate drops under noise | 0.894 → 0.744 |
| P05 ✗ | EPISODIC degrades slowest | REFUTED — MATCHED damaged most (+4.14) |

**Headline with the correction**: the design narrative predicted noise would
shrink the compression advantage; the data show it TRIPLES. The registered
operational claim (larger at ε=0.25) is confirmed; the narrative interpretation
is refuted and the mechanism took another run to pin (V6).
[findings/v5b_20260928_1848](findings/v5b_20260928_1848/FINDINGS.md)

### Run 6 — `v6t_20260928_2159` (1.9 h, V6: tolerant matching, algorithm A/B)

Only the matcher changed (fraction-best ≥ 0.6 with ties→refusal, vs exact),
same ε=0.25 world — was V5's amplification a matcher artifact?

| Verdict | Claim | Result |
|---|---|---|
| **P01 ✗** (headline) | the amplification is a matcher artifact | **REFUTED** — the gap WIDENED +1.155 → +2.306: tolerance rescued FULL (−1.27) and left MATCHED flat (−0.12) |
| P03 ✓ | matcher paths reopen | epi_test 44 → 60, book_test 151 → 174 |
| P04 ✗ | registered cost (rising stale intrusions) | did NOT materialize (53 → 53 flat) — the 0.6 band + strict-argmax refusal kept tolerance from leaking |

**The law as it now stands**: under observation noise the recurrence advantage
of structured memory over instance memory GROWS —
**write-time verification (noise filtered at the write) × full-support
coverage (a rule generalizes to every x; an instance covers only the x it
saw)**. The P46 instance-friendly condition (continuous/overlapping families)
is a different axis and remains untested in the loop (V7).
[findings/v6t_20260928_2159](findings/v6t_20260928_2159/FINDINGS.md),
[V6_DESIGN.md](V6_DESIGN.md)

### Runs 7-8 — V7 (factorial + wavy world) and V8 (adaptive read policy)

**V7A** (factorial 2×2, exact matcher): support effect **+2.14 CI[0.82, 3.44]**
is the only significant contrast; write-depth effect −0.99 CI[−2.29, +0.31],
sign unconclusive. **V7B** (wavy world): no order inversion — coverage is the
binding constraint. **V7C** (write-depth A/B): **shallow write significantly
beats deep write** (−0.655 CI[−1.10, −0.17]) — V5's write-time-filter claim
REFUTED in direction.

**V8** (ε=0.40, 4 arms including FULL-ADAPT): the adaptive read policy
(rolling flip estimate adjusts min_frac) **beats fixed policy by 0.41 errors**
(3.741 vs 4.155). The full ε dose-response reveals a **non-monotonic curve**
— ε=0.15 gives the BEST FULL E20 (1.102), lower than ε=0 (2.347): moderate
observation noise improves rule-based memory by forcing cleaner registrations.

| ε | FULL E20 | reading |
|---|---|---|
| 0 | 2.347 | baseline; marginal rules pass verification |
| **0.15** | **1.102** | **optimal**: low-rate flips filter marginal rules |
| 0.25 | ~3.6 | noise starts overwhelming the filter |
| 0.40 | ~4.2 | noise dominates; adaptive policy partially compensates |

RSI-0 lineage after four generations: g0 (2.347) → G1 ✗ → G2 ✗ →
**G3 ✓ (adaptive, 2.000)** → G4 ✗ (retracted: bit-identical duplicate of G3 —
same-config re-runs replay the parent bit-for-bit without a run seed; the
replication is requeued as G4′ with `FLYLOOP_RUNSEED`). One acceptance, one
retraction — and the retraction bought the program a seed split
(`FLYLOOP_RUNSEED`: schedule stays paired, realizations go independent), a
preflight guard, and a mechanical independence check. Standing rule: paired
contrasts want the same seed; replications want a fresh one.

Full data, corrections, and next-step registrations:
[V7A](findings/v7a_20260929_0242/FINDINGS.md),
[V7B](findings/v7b_20260929_0447/FINDINGS.md),
[V7C](findings/v7c_20260929_1940/FINDINGS.md),
[V8](findings/v8_20260930_0310/FINDINGS.md),
[G4](findings/rsi0_g4_20260930_1045/FINDINGS.md),
[V8_DESIGN.md](V8_DESIGN.md)

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

Three more from V6-V8:

- **force_new is load-bearing for multi-entry designs.** Same-family entries
  (book rules, archive rows) share enough text to exceed the 0.92 duplicate
  threshold — without `force_new`, the merge zone rewrites earlier entries
  in place, silently destroying history. This killed G1 (single 190-char
  entry) and would have killed the per-rule archive.
- **Entries must stay < 120 chars.** The engine's `split_chunks` cuts texts
  longer than 120 chars into multiple chunks; the state_key atomicity guard
  then rejects state_key writes that produce more than one chunk — silently.
- **Every arm needs its own FlyMemory instance.** The merge zone ignores
  compartments, so same-persona texts from different arms would collide in
  one store. Ports are disjoint per arm (V7C: 8769/8770/8771).

Robustness for unattended multi-hour runs: per-cycle try/except with a
consecutive-failure circuit breaker, atomic checkpoints every 50 cycles,
heartbeat/status/report cadence, local-mirror degradation when the memory
service dies (with auto-switch-back), RAM red line, sleep guard, and a
logon-resume hook so a reboot continues from the checkpoint (the absolute
deadline lives in `deadline.json`).

## Repository layout
