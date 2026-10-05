# M7.7: EPUSH_EARLY -- identification-latency lever + freshness gate

**Pre-registered** (cde03de): push episode history at first identification
(book_test naming, not only verified write) + freshness gate
(derive only when newest history entry is the immediately previous episode).
Adjudication: fam-2 NEW probe-1 derived-candidate accuracy + firing count
vs M7.5 (10-12 fires, ~10% correct) and baseline (3/13).

## Verdict: REJECT

Local rerun of the cloud run lost to the instance shutdown
(same schedule as m73_retest baseline: 4 arms, composite CAP=2,
duration 2.0h, FLYLOOP_EPUSH_EARLY=1, DERIVE_EPISODES=1;
runs/m77_epush_s0b_local_20261005, diag 3/3 PASS, zero failures).

| metric | baseline (M7.3) | M7.5 (verified write) | M7.7 (EPUSH_EARLY) |
|---|---|---|---|
| fires (m73 trace lines) | -- | 10-12 | **60 total / 13 fam-2** |
| fam-2 NEW p1 derived acc | 3/13 (23%) | ~10% | **1/13 (7.7%)** |

Firing count went up ~5x; accuracy went *down*. The single fam-2 hit
(f2r5, dp=(7,5)==truth) is the one case where the shallow history
happened to be right.

## Mechanism

The freshness gate (e1 == epoch-1) blocks *stale* pairs but not *shallow*
ones. Book_test naming is a first retrieval, not a verified write: the
(a,b) it surfaces is frequently wrong, and the composite formula
R=(a2+a1, b2-b1) is exactly as wrong as its inputs. Deterministic repeats
confirm this: f2r13 fires twice with the same dp=(12,6) vs truth (5,9) --
the same wrong history pair derives the same wrong candidate.
Identify-deeper, not identify-earlier, is what feeds composition.

## Consequence for the composition arc

M7.1 (derived entries crowd the budget, net-negative) + M7.5 (~10% on
verified-write history) + M7.7 (earlier history is *worse*) close the
in-loop derivation lever set: the ceiling of inference-time composition
is set by the accumulation rate of *verified* episodes, and pushing
unverified history in earlier only poisons it. M7.8 should either raise
verified-episode throughput or accept out-of-band composition; in-loop
early-push is dead.
