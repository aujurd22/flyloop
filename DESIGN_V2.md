# flyloop v2 design — aligned with LOOP.md / v4-RFC / the three-level mechanization map

(Redesign after the first run, 2026-09-27. Sources: flymemory `research/LOOP.md`,
`v4-rfc.md`, README (v3.5/L4/L5); intuition-mechanism PAPER / RESEARCH_PLAN /
OVERNIGHT_20260927.)

## 0. Positioning: from a self-built sandbox to LOOP.md's executable trunk

LOOP.md defines the three repos as organs — intuition-mechanism = WORLD/VERIFIER,
flymemory = MEMORY/STATE, flypoet = PROPOSER — and the cycle
`PROPOSE -> REGISTER -> RUN -> VERIFY -> RECORD -> REMEMBER -> PUSH`, noting the
next step is wrapping steps 1-7 into an orchestrator (propose stays human/LLM;
everything else mechanical).

flyloop v1 was already that orchestrator's skeleton (a computable world, a
mechanical seven-step cycle, a ledger). v2's job is to **complete the LOOP.md
contract set (REGISTER / VERIFY / RECORD / REMEMBER)** and to turn "a world"
into "a class of worlds". Two tiers:

- **Tier 1 (near, tonight)**: synthetic world v2 — more instruments, the three
  first-run fixes, two new lanes.
- **Tier 2 (far)**: research-world mode — the world *is* the open edges of the
  research registry (e.g. the P15-d scheme-selection question, the P30 estimator
  question), the verifier is the repos' existing gates (50-digit validator,
  registered bands), and `propose` stays at the session boundary. flyloop
  becomes the mechanical runner of registered experiment batteries.

## 1. Every update -> concrete change

| Update (source) | v2 change |
|---|---|
| **v4 entity-state shipped** (state_key/state_value/valid_from, I1 active-unique, I8 atomicity) | fact lane gets **dual-path A/B**: arm A semantic recall (v1 status quo), arm B `state_lookup` structural read. Same world, same budget — measures "retrieval form vs query type" (the L5 doctrine) |
| **L4 failure law** (small-edit states silently swallowed; lineage must backstop) | **State-fidelity read-back** on writes: after every sampled write, read it back (state_lookup/recall), count the "swallow rate"; the first-run 80-char truncation is a new member of this family, now caught by instrumentation |
| **L5 aggregation law** (single-shot top-k structurally insufficient) | **Aggregation lane**: cross-station counting / latest-change questions every 10 cycles, two arms (single-shot recall vs multi-round decomposition up to 4 rounds); plus an **evidence-rank diagnostic** (5 hard questions every 500 cycles at top_k=100, recording the correct entry's rank — the 85-miss 1708-11867 attribution method, ported) |
| **v4 §9 dreaming** (idle overlay consolidation + faithfulness audit gate) | **Dream channel**: every 2000 cycles, overlay-consolidate aggregation/stale slots (strict L1 discipline: overlay, never replace), then run a 10-question audit with known ground truth. Registered experiment: aggregation error drops >=30% and the fact lane does not regress (P3-style safety condition) |
| **Invariants I1/I3/I4 shipped** | **Invariant patrol**: every 500 cycles sample 20 state_keys and verify I1 (exactly one active), I3 (no cycles), I4 (tombstones present). Turns the sandbox into a long-run soak test for flymemory |
| **insights / find_conflicts shipped** | Call them every 1000 cycles and score P/R against the ground-truth drift history — these tools currently only have synthetic tests; the sandbox gives them their first truth-labeled evaluation |
| **P16 meta-lesson** (bands must be set against achievable precision, or they test the band instead of the hypothesis) | All bands restated in units of the **measured control-window sigma**: start-of-run steady window measures rolling sigma per metric, bands are sigma multiples with the floor recorded; signature ratios get a floor (the first run's 3.6e8 ratio was exactly this disease); REVISION records formalized |
| **P7 meta-lesson** (audit the implementation before a negative verdict; a null triggers a bug hunt) | **Oracle anchors**: at start and every 5k cycles, run perfect-input anchors of all three lanes (write-then-read fact anchor, short-table parse anchor, deterministic-pattern learning anchor); a failed anchor means audit code before adjudicating a hypothesis |
| **P24** (an ill-posed experiment ending in HALT is a valid verdict) | Ledger gains HALTED; three consecutive INCONCLUSIVE runs write a "blocked — needs human" note and stop that lane (no thrashing) |
| **P15-f regime theorem / P30 information limit** (internal criteria all failed; remaining openings = external information or structural priors) | seq lane becomes **dual-stream A/B**: stream A hides the regime (v1 replication), stream B prefixes a regime marker token to the context. Same model, same budget, parallel. This directly measures the external-information lever the P15-f/P30 openings point at |
| **P17** (a 27B model was at chance on this kind of discrimination in both arms) | Loop stays **LLM-free**; LLMs are allowed only at the session-boundary propose step |
| **LOOP.md data contract** | Ledger upgraded to the LOOP.md record: `{id, registered_cycle, registered_hash, band{metric, confirm, partial, negative}, artifact, verdict, supersedes, lessons}`; the final report generates the registry table; adjudication requires an artifact file plus hash |
| **LOOP.md must-not list** | Every lane pre-registered (no unregistered experiments); memory writes check supersede state; no verdict without an artifact |

## 2. The three first-run fixes (mechanisms confirmed)

1. **80-char truncation** (31.2% of observation tables unparseable -> 26% cold):
   table capacity 8 -> 6 pairs (later 5); `c=` moved to the front; pairs moved
   *first* so a cut can only remove trailing metadata (a cut could otherwise
   turn `12:10` into `12:1` — a fabricated observation); write-then-read-back
   verification. Registered: cold rate <= 5%.
2. **RULE/table mutual overwrite** (same-family sim 0.869 in the merge zone;
   all 110 rule entries tombstoned): rules moved into a single global
   **RULEBOOK** entry (`state_key=flyloop/rulebook`, read via the
   non-truncating `state_lookup`, ASCII-headed), calibrated against the real
   emitters; per-family personae greedy-optimised. Registered: rule survival
   >= 90%.
3. **seq unidentifiability** (an as-designed negative, not a tuning problem):
   dual-stream A/B (see above). Registered: stream B error < 0.68 (oracle
   0.639 + margin), stream A replicates 0.70-0.88.

## 3. Adjudication governance upgrades (fixing two first-run measurement illusions)

- **Three-window consistency**: every drift-response metric is computed in
  short/long/micro windows; disagreement auto-downgrades the verdict to PARTIAL
  (the first run's FL-P004 "confirmation illusion": the long window smoothed
  away the fact that nothing was learned).
- **NEGATIVE triggers an audit**: any negative lane verdict runs the oracle
  anchors first; only a healthy anchor lets the verdict stand.
- **Sigma-stated bands**: expectations and falsification bands both expressed
  in measured control-window sigmas (P16's meta-lesson implemented).
- **REVISION records**: band changes only via recorded entries (as in P16
  REVISION 1), with the reason surfaced in the final report.

## 4. v2 pre-registered predictions (draft, ~14; written to the ledger at launch)

| ID | Prediction | Falsification band |
|---|---|---|
| V2-P01 | cold rate <= 5% after the truncation fix | >15% => NEGATIVE (audit implementation first) |
| V2-P02 | rule survival >= 90% (state_history verified) | <70% NEGATIVE |
| V2-P03 | arm B (state_lookup) error <= half of arm A (recall) | no difference => NEGATIVE (form does not matter) |
| V2-P04 | write-readback swallow rate <= 2% (L4 direct measure) | >10% -> file a flymemory bug |
| V2-P05 | invariant violations = 0 (I1/I3/I4) | any violation FAILS with a repro artifact |
| V2-P06 | aggregation: multi-round <= single-shot x 0.7 | no advantage = a synthetic-domain counterexample to L5 |
| V2-P07 | dream channel: aggregation error drops >= 30% and fact lane regresses <= +0.01 | unsafe or ineffective => NEGATIVE |
| V2-P08 | seq B < 0.68; seq A stays >= 0.70-0.88 | B fails => identifiability is not sufficient |
| V2-P09 | rank diagnostic: median rank of the correct entry for hard aggregation questions > 34 | <= 6 => aggregation failures have another cause |
| V2-P10 | conflict detection P >= 0.8 / R >= 0.7 | report false-positive samples |
| V2-P11 | three-window consistency >= 90% | otherwise window choice is the main variable (methodological finding) |
| V2-P12 | signature CONFIRMED ratio in [0.4, 0.9] (no overflow) | out of range => instrument still sick |
| V2-P13 | >= 40k cycles, 0 breaker trips, 0 restarts | any violation is an engineering incident (write a post-mortem) |
| V2-P14 | `http` mode throughout (no degraded stretch) | a `local` stretch = service-stability issue |

## 5. Budget and engineering

- Keep the wall-clock ceiling at the operator's window (5 h tonight, 10 h
  possible); cycle time 0.3-0.6 s with the new instruments; target >= 40k
  cycles.
- Tombstone growth (run 1: 20k entries / 74 MB per 10 h; save mean 0.17 s,
  cycle time creeping 145 -> 180 ms) is acceptable at this scale. Beyond 24 h a
  cold archive / compression pass is required — recorded as a flymemory-side
  recommendation, not changed inside the sandbox.
- The run-1 DB is archived as the v1 baseline; v2 starts from an empty library.

## 6. Write-back (the LOOP.md RECORD+REMEMBER steps, implemented)

1. `runs/<run>/`: final report + FINDINGS + `registry.jsonl` (LOOP.md contract);
2. flymemory memory: findings remembered, superseded states superseded,
   >=3 related entries consolidated;
3. flymemory repo `research/`: a LOOP.md-style note for the session (local
   file; pushing is the operator's call);
4. intuition-mechanism repo: methodological lessons only (bands/windows/audits);
   mathematical conclusions are the propose leg's business.

## 7. Tier 2 sketch: research-world mode (next phase)

- The world = the registry's open edges (e.g. P15-d unsupervised scheme
  selection; new structure for the P30 blind estimator);
- The verifier = the repos' existing gates (the 50-digit validator, the band
  adjudication scripts);
- One night = one "experiment battery": every experiment independently
  registered, independently artifacted, independently adjudicated;
- `propose` stays at the session boundary; RUN/VERIFY/RECORD/REMEMBER are
  fully mechanical;
- Relation to the current manual overnight runs: it takes over the mechanical
  middle, never replaces propose. First goal: turn the four manual steps
  (script -> JSON -> registry row -> memory) into one command.

## 8. Run-duration policy (derived from measured event rates, 2026-09-27)

Run 1 measured 55,173 cycles / 10 h ~= 5,500 cycles/h. Lanes and the sample
sizes the v2 predictions need:

| Event | Measured rate | Sample needed | Time to reach | Accelerator |
|---|---|---|---|---|
| fact rotations | ~210/h | 1000+ | <1 h | — |
| fact shocks | 3.7/h | >= 24 | **6.5 h** | shock period 1500 -> 750 cycles => 3.3 h |
| puzzle rotations (all families) | 20.6/h | >= 20 per family | ~4 h | — |
| seq regime shifts | 11/h | >= 30 | 2.7 h | — |
| rule discoveries | 11.5/h | >= 50 | 4.4 h | — |
| dream audits (v2) | 2.76/h | >= 10 passed | 3.6 h | interval 2000 -> 1000 cycles => 1.8 h |
| seq-B convergence | — | **updates, not hours** | 4 steps/cycle => 22k updates/h; 2-4 h to see converge-or-not | steps per cycle 1 -> 4 |

**Conclusions**: 2-3 h covers engineering verification (fixes, anchors, A/B
reads, invariant patrols); 5-6 h is the sweet spot for the full v2 prediction
set; 10 h buys the long-stability claim plus thicker shock samples. When more
samples are wanted, accelerate the world clock (shorter periods, more steps per
cycle) rather than extending wall time. Beyond 10 h is on hold until the
tombstone cold-archive exists (24 h would reach ~200 MB pickles and ~0.4 s
saves).

**Stop rules (instead of a fixed duration)**: end gracefully when any of
(a) event quotas are met (shocks, discoveries, dream audits), (b) the time
ceiling is reached, (c) the learning curves have been flat for 5000 cycles.
Quota-based stopping is more honest than "run N hours": it buys samples by
statistical need, not by the clock. (This run: quotas disabled — the operator
booked the full 5 h window.)

**Iteration speed beats single-run duration**: two 5 h runs with a design
change in between beat one 10 h run. The three first-run fixes were each
independently verifiable, which is what made fast iteration possible.
