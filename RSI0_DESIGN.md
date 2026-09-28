# DESIGN RSI-0 — a mechanical self-improvement lineage over flyloop's own policy

Status: registered 2026-09-29 00:55, before generation G1 launches. This is
the minimal RSI experiment proposed in the program review: the system's own
run evidence selects the next generation's memory-policy configuration from
a registered mutation menu, evaluated by the same hidden evaluator every
generation (same world schedule, same seed, paired episodes). No LLM in the
selector — RSI-0 is deliberately selector-free; the proposer being mechanical
is what makes the first lineage falsifiable.

## 1. Objective (fixed before G1)

Minimize the FULL arm's E20 on discovered-rule RECALL episodes, subject to:
(a) engineering-valid run, (b) SIR absolute-count floor (>= 20 intrusions in
window before any ratio is read), (c) the mutation must be from the menu.

## 2. Lineage so far (generations already run, same evaluator)

| gen | config | FULL E20 | note |
|---|---|---|---|
| g-2 | exact matcher, cap 5, eps=0 | 0.43 | V4 run |
| g-1 | exact matcher, cap 5, eps=0.25 | 3.62 | V5B run |
| g0 | tolerant 0.6, cap 5, eps=0.25 | 2.35 | V6T run |

The g-1 → g0 step was the first EMPIRICAL strategy change: tolerance
improved FULL by 1.27 (the matcher-brittleness hypothesis was refuted along
the way — the advantage widened, and the mechanism was pinned to coverage ×
write-time verification).

## 3. Mutation menu (registered)

- **M1 BOOK_CAP 5 → 13.** Targets the measured no-candidate floor: the
  probe-1 failure decomposition (unexplained = 0 across three runs) showed
  15–19 of 49–58 probe-1 failures were "no candidate in window" — the
  recency cap evicting rules before their recurrence arrives. Expected:
  recovers part of the floor at eps=0.25.
- **M2 matcher regime flip** (tolerant ↔ exact). Already exercised once
  (g-1 → g0, accepted: −1.27).
- **M3 world shift eps 0.25 → 0.** Not a policy mutation — it changes the
  task. Only permitted as a control generation, never counted as an
  improvement.
- **M4 length-mix recalibration** (more short episodes). Targets discovery-
  failure variation; registered for the generation after the support/verify
  question closes.

## 4. Selection rule (deterministic, no discretion)

1. Rank menu mutations by expected FULL E20 improvement implied by
   already-collected evidence (failure decompositions, prior contrasts).
2. Run the top candidate (2 h, same seed/schedule, paired).
3. Accept iff FULL E20 beats the parent's point estimate AND the parent's
   95% CI upper bound; otherwise revert to parent config and strike the
   mutation from the menu.
4. The next generation inherits the accepted config and strikes nothing
   else; the next proposal is the top remaining mutation, unless a NEW
   failure decomposition (probe-1 buckets, recomputed on the accepted run)
   promotes a different mutation — in which case the promotion and its
   evidence are logged in the lineage entry.

## 5. G1 (derived mechanically by §4 from existing evidence)

The failure decomposition promoted M1: at g0, probe-1 failures were
15 no-candidate / 15 flipped / 19 recovered — no-candidate is the largest
non-noise bucket, and it is caused by BOOK_CAP=5 recency eviction, not by
noise. So:

**G1 = g0 config + M1 (BOOK_CAP 13), eps=0.25, 2 h.**
Registered acceptance: FULL E20(G1) < min(2.347 [g0 point], 3.621−1.27 =
2.35 [g0-implied]) — i.e. strictly below g0's 2.347 beyond its CI upper
half-width; revert to cap 5 otherwise.

## 6. Lineage ledger

Each generation appends to `runs/rsi0_lineage.json`:
{gen, parent, config-diff, reason, evidence-links, FULL-E20 + CI,
accepted/reverted, failure-decomposition}. The file is the RSI-0 paper's
Table 1.
