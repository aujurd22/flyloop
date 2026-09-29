
## G1 verdict: M1 REJECTED, revert to g0 (BOOK_CAP=5)

FULL E20 on discovered-rule RECALL episodes: 4.078 (n=51) vs parent 2.347 —
far worse. Root cause chain: 13-rule book entries reached ~190 chars,
exceeding the split_chunks 120-char threshold; the state_key atomicity guard
then rejected the write outright; 92/133 book writes were dead
(rulebook_readback_fail 69%); the book froze at stale rules and book_test
hit rate collapsed to 15.7% (parent 38.8%).

## What this means for the RSI-0 loop

The loop functioned exactly as designed: evidence → mechanical selector →
run → evaluator → REJECT + revert. The selector's proposal was faithful to
its evidence (no-candidate was the largest failure bucket) but infeasible
under the storage engine's encoding constraint — a constraint the lineage
now knows about and has registered. G2 candidate: per-rule entry encoding
(one short state entry per rule), which needs a small implementation task
(book read path + a MATCHED-style archive alternative), then the same 2 h
harness.

This is the first generation where the RSI-0 loop said NO to its own
mutation — the reject-and-revert path is the part that makes the lineage
trustworthy.

## RSI-0 G2 + V7C first launches: both ENGINEERING_INVALID (2026-09-29 evening)

Two harness bugs, both fixed in code, both runs voided and registered for
rerun:

1. **G2 (per-rule encoding)**: BOOK_CAP=13 eviction pruned the book MIRROR
   without pruning the perrule INDEX — the read path's sort key then hit the
   evicted rule (KeyError 'f3r1', 450 cycle failures, circuit breaker). Fix:
   lockstep prune + a desync guard before the sort.
2. **V7C (write-depth n-extension)**: the worker's arm→service mapping gave
   FULL and FULL-RAW the SAME port — one store, the two arms I1-superseded
   each other's book entries, and the write-depth contrast collapsed to
   0.000 on every episode. Fix: FLYLOOP_PORTS env, one port per arm.

The RSI-0 lineage records both as engineering-invalid (not hypothesis
negatives); the corrected designs are the registered next runs.
