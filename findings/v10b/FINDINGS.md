# V10b findings — the P-COMBO in-loop test FAILS honestly: there is no inference-time chain to cut (and V10's P2 was overclaimed)

Run: 2026-10-02 02:41 → 04:42, composite world, **BOOK_CAP=2**, arms FULL /
MATCHED / EPISODIC, 6092 cycles, 0 failures. Baseline: V10 (same seed,
CAP=5). Adjudication data: `v10b_e1.txt`.

## E1 verdict: strong-form prediction REFUTED

| composite (FULL) | CAP=5 (V10) | CAP=2 (V10b) |
|---|---|---|
| RECALL E20 | 1.333 | 1.545 (+0.444 CI[+0.000,+1.000], **n.s.**) |
| probe-1 hit | 56% (5/9) | 36% (4/11) — direction only, n=9 |

Generic budget cost shows up on standard rules (+0.72 E20), not the
targeted hop-2 destruction P-COMBO predicts. MATCHED unchanged (its read
cap is independent), as predicted.

## Root cause: the capability whose budget-sensitivity we tested does not exist

P-COMBO's mechanism operates at INFERENCE time: the hop-2 entry matters
because the system composes relations from retrieved predecessors at
query time. Flyloop's registry does nothing of the sort — it discovers
every rule directly from observations and never reads predecessor rules
to derive anything. With no inference-time chain, recency eviction cannot
destroy one. CAP=2 costs generic capacity, nothing targeted.

**And this forces a correction to V10's P2** (committed 84cfdcd): the
"56% composition transfer" claim was overclaimed. Probe-1 of composite
RECALL episodes happens AFTER the rule's own NEW episode observed it —
the 56% is ordinary registry advantage on a discovered rule, NOT answers
to unobserved structure. True composition transfer would require the
registry to write R_i's entry from R_{i-2}, R_{i-1} WITHOUT observation —
a capability that has never been implemented. V10's composite E20
asymmetry (1.33 vs 5.22) stands as a real registry-vs-archive result;
its transfer interpretation is retracted.

## Registered: M7 (composition inference) — the preconditions P-COMBO needs

Write preemptive composite entries: when the book holds R_{i-2}, R_{i-1}
(derivation = episode params (a_{i-2}+a_{i-1}, b_{i-2}−b_{i-1})), write
R_i's entry BEFORE its first observation, flagged `derived=1`. Only then:
(a) does the registry answer unobserved composite structure (the real
TRANSFER test), and (b) does the P-COMBO budget test become meaningful
(evicting predecessors must kill the preemptive entries — the chain now
exists to be cut). M7 supersedes M6 in priority: same derivation
machinery, and drift (δ) storage rides the same preemptive-write path.

## What stands from V10b

- E3 (Arena profile): flyloop discoveries C 7.23 / N 1 / T +2.16 vs
  consolidation C 1.10 / N 0.13 / T 0.00 — INSIGHT-class, the umbrella
  answer. Untouched by this correction (it never relied on P2).
- ICR: FULL 1.7 / MATCHED 1.6 / EPISODIC 0.8 — compression ratio is not
  the differentiator; accuracy-per-bit is.
- E1's generic budget curve (CAP=2 costs standard rules ~0.7 E20) is a
  usable capacity-price data point.

## Process note

This is the second overclaim caught by designing the test that would have
confirmed it (the first: G4's fake replication). The pattern generalizes:
a claim made when interpreting a favorable number must be re-derived when
designing the experiment that depends on it — interpretation optimism and
mechanism reality part ways exactly there.
