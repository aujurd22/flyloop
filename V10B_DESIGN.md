# V10b DESIGN — evidence-chain budget, the Polanyi gap, and the in-loop Arena profile

Registered: 2026-10-02 01:20 (operator directive: "仔细看兄弟仓库，设计下一个测试").
Status: E2/E3 analysis immediate (existing data), E1 launched.

## What the sibling-repo sweep yielded (the usable pieces)

1. **flymemory P-COMBO (PARTIAL, clean mechanism)**: two-hop compositional
   QA — unfiltered triple extraction hits 100% ceiling; standard
   question-relevance extraction DELETES the hop-2 entry (75% < RRF 87.5%)
   because "the hop-2 entry has no lexical overlap with the question".
   Their verdict explicitly bridges here: composition transfer holds
   through the memory path only if the predecessor evidence survives the
   filter.
2. **intuition-mechanism P156 (the verbalization gap, quantified)**: all
   three judges' STATED rules score ~50% (below the all-normal prior)
   while their OPERATIVE judgments run 79-94% — Polanyi's paradox,
   measured. Design law: score probe agreement, never rule statements.
3. **flymemory P-DISCOVERY**: consolidation entries profile as
   C 1.10 / N 0.13 / T 0.00 on the Arena metrics — "value-carrying
   compression, NOT insight". A production baseline to compare flyloop's
   own discoveries against.
4. **flymemory M5T-2 (SUPPORTED)**: residual entries work as declarative
   third-person memories (100%/89.7%) — independently validates the M5
   residual-entry FORMAT chosen in W9C.
5. **SDB metrics module** (sdb/metrics.py): bits_of/mdl_ratio/transfer/
   surprise — adopted verbatim as V10b's measurement convention.

## E1 (run, 2h): evidence-chain budget — BOOK_CAP eviction vs composition

P-COMBO's law, in-loop. In the composite world, R_i derives from EPISODES
i-2, i-1; the registry's book keeps the BOOK_CAP most recent rules per
family. At CAP=5 (V10) the predecessors survive; **at CAP=2 the eviction
victims are exactly R_{i-2} when R_i arrives** — recency filtering is a
precision-targeted hop-2 deleter (recency keeps i-1 and i, drops i-2).

| run | BOOK_CAP | prediction |
|---|---|---|
| V10 (baseline, same seed) | 5 | composite probe-1 56%, composite E20 1.33 |
| **V10b** | **2** | FULL composition transfer collapses toward chance; composite E20 → MATCHED band; MATCHED unchanged (its read cap is independent) |

Arms FULL/MATCHED/EPISODIC, ε=0.25, FLYLOOP_COMPOSITE=1, 2h. The paired
contrast is V10 vs V10b FULL on composite-family metrics (same schedule
seed, one knob) — with the G4 caveat that V10b is a WORLD/config change,
so the pairing is per-(family,epoch) cross-run, not bit-level.

## E2 (analysis, existing data): the Polanyi gap in the registry

P156's verbalization gap, mechanized: a registry entry's STATED (a, b)
(the compressed fit at discovery) vs its OPERATIVE rule (the exhaustive
refit from confirmed raw pairs, W9C machinery). In the wave world the
stated fit is polluted by construction; the refit recovers the operative
rule. Measure: fraction of entries where stated ≠ operative (beyond
tolerance) YET operative predictions hit — "the registry knows more than
its entries say". Prediction: gap > 0 at W=4, ~0 in lossless worlds.

## E3 (analysis, existing data): the Arena profile of flyloop discoveries

P-DISCOVERY scored flymemory consolidations C 1.10 / N 0.13 / T 0.00 —
"not insight". The same profile for flyloop rule discoveries (FULL arm,
V10 run), SDB conventions:

- C = mdl_ratio: bits(pre-discovery observation pairs of that rule) /
  bits(rule entry)
- V = 1 by construction (consec-3 verification gate) — reported as
  gate-passed
- T = RECALL E20 delta vs EPISODIC on the same episodes
- N = 1 for first DISCOVERY (fresh rid; REACTIVATION excluded)

Registered expectation: flyloop discoveries profile as INSIGHT-class
(C ≫ 1, N = 1, T > 0, V = 1) — the loop's discovery events are insight-
grade under the Arena's own definition, unlike consolidation. This is the
umbrella question ("does the loop produce insight?") answered with the
Arena's own yardstick, mechanically.

## Discipline

- E1 is a config change (M3-class world/budget shift), never counted as
  self-improvement; the interesting claim is the P-COMBO replication
  boundary (CAP=2 destroys, CAP=5 holds).
- E2/E3 are read-only analyses of existing runs.
- ICR (V10 P4 debt): computed here from the now-verified counters
  (book_bytes / epireg_bytes / pad_bytes), SDB bit convention.
