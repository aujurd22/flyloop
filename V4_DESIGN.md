# DESIGN V4 — Discovery-Failure Variation × Representation–Algorithm Disentanglement

Status: framework registered 2026-09-28 (post-V3-review). Implementation by
delegated subagents under the contracts below; every diff reviewed by the
operator before launch. V3 remains the reference run (5C/2I/1R after
corrections).

## 1. What V3 left open (the two questions V4 answers)

1. **Does the abstraction itself pay?** V3 could not ask this: FULL abstracted
   100% of recurring rules, so the discovered-vs-undiscovered contrast had zero
   variation, and the registered UIR was refuted as near-tautological once
   corrected. V4 creates **discovery-failure variation** by giving episodes
   variable lengths: short episodes end before the abstraction loop completes,
   so a calibrated fraction of rules stays unabstracted while still returning
   later as RECALL episodes.
2. **Representation or algorithm?** V3 introduced the rule registry AND the
   one-pair matcher together. V4 adds arm **MATCHED (M)**: the same
   candidate-scoring/unique-match decision rule, but over **raw episodic pair
   tables** instead of compressed rules. Only the stored representation
   differs between F and M.

## 2. Three arms, one world

| | FULL (F) | MATCHED (M) | EPISODIC (E) |
|---|---|---|---|
| live observation table (current epoch) | yes | yes | yes |
| recent-episodes archive | — | **raw pair tables, last 5/family** | — |
| rule registry (compressed a,b) | **last 5/family** | — | — |
| matcher over archive | book_test (1 live pair → unique rule match → adopt) | **epi_test** (live pairs → unique episode-table match → fit from pooled pairs) | none (fit only) |
| padding writes | book bytes charged | archive bytes charged | drains both |

All arms see the identical precomputed schedule, identical probes, paired by
(family, epoch, probe_idx). Three independent sandbox FlyMemory instances
(ports 8769 F / 8770 M / 8771 E; separate pickles — the merge zone ignores
compartments). Write parity: E's padding writes byte-match F.book + M.archive
combined.

## 3. World changes (the only two, everything else frozen from V3)

1. **Variable episode lengths.** Each episode gets a length in probes drawn
   from a calibrated mix (pilot-tuned so ~20–40% of rules end their NEW
   episode unabstracted). Short episodes (< ~6 probes) usually end before the
   fit→consec→book-write loop completes; long episodes behave like V3.
   Episode boundaries are prefix sums of lengths (pure function of SEED,
   recomputable, saved as world_schedule.json before cycle 1).
2. **Quota-gated noise phases.** Phases advance on cumulative NEW-episode
   counts (A: 0–49, B: 50–109, C: 110+), never on cycle thresholds — the
   P07/P8 lesson. Gates are calibrated so phase C is reached well inside 10 h.

Frozen from V3: y=(ax+b) mod 13 (harder families are V5, queue item 6), fact
lane with A/B sub-arms, dual seq streams as continual-learning control, noise
text, distractor cadence multipliers (20/10/5), RECALL gaps 2–5 epochs, mix
NEW 50 / VARIANT 25 / RECALL 25.

## 4. The probe-1 interface fix (applied symmetrically)

V3 artifact: the current probe's revealed pair (x1,y1) was folded into the
observation table AFTER prediction, so probe 1 was blind by construction
(0/78 instant recoveries). V4 folds the revealed pair into obs BEFORE the
prediction step, for **all three arms**. Expected: F adopts a returning rule
at probe 1 (book_test on the single revealed pair); E can fit at probe 2 (two
distinct x by then). This is an interface fix, not an arm advantage — it
applies identically to everyone.

## 5. Endpoints (registered before the first cycle)

| ID | Claim |
|---|---|
| V4-P01 (primary, the P06 fix) | Recurrences of DISCOVERED rules show larger F-vs-E benefit than recurrences of UNDISCOVERED rules (cluster bootstrap CI of the contrast excludes 0). Requires the undiscovered fraction to land in the pilot-calibrated band. |
| V4-P02 (primary, disentanglement) | On recurrences of discovered rules: F ≤ M ≤ E in E20, with both steps' point estimates positive. Reading: F−M ≈ 0 → the matcher is the mechanism; F−M > 0 → compression adds beyond the matcher. |
| V4-P03 | On recurrences of UNDISCOVERED rules, M beats F (M archived the raw pairs; F has no rule to adopt): dE20(M−F) < 0. The winning representation flips with discovery success. |
| V4-P04 | Probe-1 recovery exists: F book_test fires at probe 1 on RECALL episodes of discovered rules ≥ 40%. |
| V4-P05 | SIR(F vs E) ≤ 1.5 (band maintained in the 3-arm world). |
| V4-P06 (NC1) | VARIANT/NEW contrasts ≈ 0 for F−E and M−E. |
| V4-P07 | Phase C is reached (quota gate) and FULL degrades slower than E across phases. |
| V4-P08 (NC2) | Fact lane: no regression, all arms. |

Inference: cluster bootstrap by rule lineage is the DEFAULT (episode-iid CIs
reported only for comparison); perm_p by sign-flip on cluster means; per-family
breakdown mandatory. DISCOVERY ≠ REACTIVATION in the event schema
(insight_kind); UIR-style statistics use first-DISCOVERY cycle strictly.

## 6. Stop rules

All quotas (NEW ≥ 150, VARIANT ≥ 75, RECALL ≥ 75, shocks ≥ 100) or 10 h
deadline or engineering tripwires → ENGINEERING_INVALID discipline unchanged
(readback splits, entry caps, breaker). Phase C is quota-gated so P07 is
evaluable by construction.

## 7. Pre-launch checklist

- Pilot: short-run (≤ 30 min) to calibrate the length mix to the 20–40%
  undiscovered band and confirm phase C reachability; gates frozen before the
  registered run.
- tests/test_v4_world.py (schedule/length/phase determinism),
  tests/test_v4_analyze.py (analyzer recovers known effects from a synthetic
  fixture), existing suites (test_v3, test_parsers, calibrate_texts) green.
- smoke_v4.py: 3-arm pairing, three-way parity, epi_test fires on M and not
  on F/E, discovery-failure variation present, event schema complete.
- Real-emitter recalibration for any new text format (episodic archive
  entries) against MiniLM: cross-entry < 0.75, same-entry update > 0.75.
