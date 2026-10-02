# V10c/d findings — M7 split verdict: composition transfer REAL (48%, P-COMBO replicated), naive budget-blind entries net-negative (M7.1 fix registered)

Runs: 2026-10-02 11:26 → 13:27, composite world, 4 arms
(FULL-COMP / FULL / MATCHED / EPISODIC), CAP=5 (V10c) and CAP=2 (V10d)
concurrently, 3758/3765 cycles, 0 failures, 4 per-arm stores live.

## P1 CONFIRMED — true composition transfer exists now

Derived-entry NEW-episode probe-1 hits on the composite family:
**10/21 = 48%** (CAP=5) vs 7.7% random. The registry answered UNOBSERVED
composite structure from stored predecessors — the capability V10's P2
wrongly claimed and V10b exposed as missing. With M7 it exists and fires.

## P3 CONFIRMED — the P-COMBO evidence-chain law now replicates in-loop

Under CAP=2, transfer drops to **5/21 = 24%** — predecessor eviction cuts
it in half. In V10b (no inference-time chain) the same budget knob moved
nothing; with M7 the chain exists and recency eviction cuts it, exactly
as flymemory's P-COMBO predicts for two-hop evidence. The cross-repo law
(relevance/recency filtering destroys multi-hop evidence) now replicates
on a mechanical substrate.

## P2 REFUTED — naive preemptive entries cost more than they earn

| composite RECALL E20 | FULL-COMP | FULL | paired FULL−FULL-COMP |
|---|---|---|---|
| CAP=5 | 4.286 | 1.429 | −2.857 [−9.667, +0.000] n.s. |
| CAP=2 | 7.571 | 2.000 | **−5.571 [−15.000, −0.333] SIG** |

The mechanism is budget crowding: a derived entry carries ep=epoch
(current), so it sorts as the family's most recent rule and EVICTS
observed rules from the BOOK_CAP window — at CAP=2 the displacement is
guaranteed and the paired damage is significant. First-contact transfer
gains are paid back with interest on later RECALL matches against
spurious candidates. Poison on standard/periodic families is bounded
(derived_use probes err 78% vs ~85% baseline — no collapse), the damage
concentrates in budget displacement.

## Registered: M7.1 — budget-free derived entries

Derived entries must not consume book budget: evict-first (lowest
priority in book_text_v3's recency sort), max 1 per family, and dropped
immediately when a real rule needs the slot. Prediction: with M7.1 the
transfer gain (P1) survives while the E20 damage (P2) disappears — the
composition capability becomes net-positive. The P-COMBO retest then
re-runs on M7.1 (the eviction pressure lands on REAL rules, which is the
interesting regime).

## Engineering notes

Supervisor fixed en route: ensure_services + mid-run respawn iterate
FLYLOOP_PORTS × FLYLOOP_ARMS (the 4th arm had no service — the worker
connect-timed out at start), and worker stderr now lands in worker.log
(the invalid-handle black hole had been silently eating crash tracebacks).

## Ledger

| hypothesis | verdict |
|---|---|
| M7 P1: unobserved composite answers from derived entries | **CONFIRMED** (48% vs 7.7%) |
| M7 P2: net E20 benefit | **REFUTED** (budget crowding, −2.9/−5.6) |
| M7 P3: P-COMBO eviction cuts the chain | **CONFIRMED** (48% → 24%) |
| M7 P4: poison self-corrects | HELD (no standard/periodic collapse) |
