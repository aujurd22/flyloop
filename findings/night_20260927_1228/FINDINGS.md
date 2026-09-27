# Night run night_20260927_1228 — findings (v2, 5h, 46134 cycles)

2026-09-27 12:26 → 17:26, deadline reached, 0 cycle failures, 0 breaker trips.
FlyMemory third sandbox instance (port 8767, zero library changes), FlyPoet legs
on CUDA, pre-registered V2-P01..P10 adjudicated from run data (see ledger.jsonl).

## Verdicts (registered before/during run, applied offline from state+events)

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| V2-P01 | puzzle cold rate <= 5% after truncation fix | **CONFIRMED** | 186/23067 = 0.81% (all first-episode, no truncation-induced cold) |
| V2-P02 | rule entries survive active in own compartment >= 90% | **CONFIRMED** | readback_fail = 0/177 discoveries |
| V2-P03 | fact B arm (state_lookup) error <= half of A arm (recall) | **PARTIAL** | errA 0.0706 vs errB 0.0689 — both ~99.9% hit; the truncation fix erased the v1-era gap |
| V2-P04 | write-readback failures <= 2% | **CONFIRMED** | 0 failures |
| V2-P05 | no I1 active-unique violations | **CONFIRMED** | 0 violations across 29 state_keys; see NOTE-1 (superseded_by=0 falsy trap) |
| V2-P06 | seq B (regime marker) err < 0.68 (oracle 0.639) | **PARTIAL** | last-10-bin mean 0.707 — marker identifiable but transitions not learned |
| V2-P07 | seq A replicates v1 stall (err >= 0.70 in >= 90% bins) | **CONFIRMED** | 97.9% of 47 bins |
| V2-P08 | signature CONFIRMED ratio in [0.4, 0.9] | **REFUTED** | 62/66 = 0.94 — puzzle leg so good that pre/post drift ratios degenerate to 0/0 (PARTIAL), inflating the confirmed share |
| V2-P09 | >= 40000 cycles in 5h, 0 breaker trips | **CONFIRMED** | 46134 cycles |
| V2-P10 | memory entries <= 40000 at end | **CONFIRMED** | 9140 entries (dedup + merge kept growth linear-ish) |

Signature ledger: 62 CONFIRMED / 110 PARTIAL / 4 REFUTED (177 discoveries).

## The three findings

**F1 (positive): the v1 failure modes are fixed and the loop closes.**
v1's cold-start lock (26%) → 0.81%; v1's 110 rule-discoveries-all-tombstones →
177 discoveries, 100% readable, and the RULEBOOK is load-bearing: 5483
predictions served by `book` lookups with zero error (fit path 17069 also zero).
The puzzle leg is *solved*, not merely improved: after a family's rule is
written once, drift rotations are absorbed at median 0 recovery cycles.

**F2 (informative negative): identifiability was not the seq bottleneck.**
Stream B prefixes a regime marker token (vocab 19) specifically so the poet can
attribute transitions to regimes — P15-f/P30 style identifiability, granted for
free. Result: seqB 0.73-0.76 vs seqA 0.74-0.79 across 46k cycles; both far from
oracle 0.639 and barely below v1's unmarked 0.81. The 494K poets' own loss also
rises mid-run (1.03 → 1.49) on *their own* stream. Reading: the bottleneck is
not observability of the regime but the aggregate-learning capacity of a small
poet under continual rotation — the v1 conclusion "seq did not learn" survives
the identifiability repair, which strengthens it.

**F3 (measurement artifact worth registering): a leg that saturates breaks
ratio-based signature probes.**
The drift-signature probe (post-drift err <= 0.6 × pre-drift err) degenerates
when the leg sits at ~0 error both sides: 110/176 signatures scored PARTIAL on
0/0. Registered as V2-P08 and REFUTED by design — future signatures need an
absolute-floor guard (e.g. skip if pre-window err < 0.02) instead of ratios.

## Hard knowledge (do not re-learn these)

- `superseded_by=0` is falsy: any audit counting actives with
  `not entry.superseded_by` miscounts "superseded by id 0" as active
  (194 tombstones at st-0). Always `is None`. Recorded as NOTE-1.
- `_adjudicate` at runtime read counter names that no longer exist
  (`trunc_fail`, `discoveries` vs actual `cold`, `book_writes`), so the
  worker never applied verdicts in-flight; they were applied offline from
  state.json + events.jsonl (this document). Fixed in reports.py for next run.
- station 0's persona text is degenerate (`FACT_FEAT1[0] == FACT_FEAT2[0]`,
  self-repeat) — harmless here (dedup handled it) but a calibration hazard:
  fix the data, not the thresholds.

## v1 → v2 comparison

| Metric | v1 (10h) | v2 (5h) |
|---|---|---|
| puzzle cold rate | 26% self-lock | 0.81% |
| rule discoveries readable | 0% (all tombstoned) | 100% (177/177) |
| fact recall hit | degraded by truncation | 99.9% both arms |
| puzzle served-by-rule error | n/a | 0.0000 over 5483 book lookups |
| drift recovery (fact/seq/puzzle) | partial | 1801/1801, 90/91, 172/172, median 0 cycles |
| seq learning | none (0.81) | none (0.73-0.76 with marker) — negative result replicated |
