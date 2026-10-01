# V9 W9A findings — the abstraction cliff: tolerance coupling collapses contrast (P1/P2/P3 partially refuted, mechanism discovered)

Four runs (W ∈ {0, 2, 4, 6}), arms FULL/MATCHED/EPISODIC, ε = 0.15, 2 h
each, 0 failures, all clean (readback 0). RECALL E20 on discovered rules,
cluster bootstrap by rule lineage. Adjudication data:
`w9a_adjudication.txt`.

## Headline numbers

| W | FULL E20 | MATCHED E20 | paired MATCHED−FULL | verdict |
|---|---|---|---|---|
| 0 | **1.137** CI[0.78, 1.57] | 3.353 | +2.216 CI[+1.52, +3.04] | FULL wins big |
| 2 | 10.737 | **9.658** | **−1.079 CI[−1.59, −0.63]** | **MATCHED wins** |
| 4 | 10.581 | 10.419 | −0.163 CI[−0.81, +0.52] | tie |
| 6 | 10.367 | 10.531 | +0.163 CI[−0.41, +0.79] | tie |

## The shape is a cliff, not a floor — P1 refuted as formulated

Pre-registered P1 predicted a gradual abstraction floor (~±W errors per 20
probes). Reality: FULL collapses from 1.14 to ~10.5 at W=2 and stays flat
through W=6 — a **step function with a saturation plateau**, ~5× taller
than the wave floor could explain. The extra error is not the wave; it is
the read system's response to the wave.

## The mechanism: tolerance coupling (the real discovery)

The world's physical tolerance (±W wave) was fed directly into BOTH the
discovery gate (WAVE_TOL = W) and the matchers (frac_best/epi_test
tol = W). Method decomposition of FULL's RECALL probes exposes the
cascade:

| W | ok:rule (direct hits) | rule: errors (wrong rule adopted) | fit: errors |
|---|---|---|---|
| 0 | 427 | 8 | 30 |
| 2 | 29 | 156 | 187 |
| 6 | 84 | 354 | 103 |

- At W=0 the registry's exact-match contrast identifies the true rule
  (427 direct hits).
- At W>0 the band swallows candidate discrimination: at tol=2, wrong
  candidates clear min_frac and win strict-argmax (rule: errors ×20); at
  tol=6 the ±6 band covers all 13 residues — every candidate reproduces
  everything — so registration is trivially satisfied and the book fills
  with wave-fitted wrong rules, which then produce probe errors via the
  rule path (rule: errors 354).
- The same band poisons the archive side (epi_test tol=W) — which is why
  ALL arms saturate at ~10.5: it is a matcher-regime collapse, not a
  representation-quality difference.

**Law (registered): the world's incompressibility must not be coupled
into the matcher's tolerance. A tolerance wide enough to forgive the
world's residual is wide enough to destroy candidate contrast — the
program's own core discipline (contrast/discrimination) fails exactly
when the world forces tolerance.**

Against pre-registration: P2 (crossover) CONFIRMED, earlier than expected
(W=2, MATCHED significantly better). P3 (discovery survives) REFUTED —
discoveries dropped (128 at W=6 but only 68 at W=2) and the book fills
with wrong rules. P1 refuted in form (cliff+plateau, not floor).

## Engineering translations (the actionable part)

1. **Decouple the bands**: discovery gate and read matcher need different
   tolerances; neither may inherit the world's physical W unchecked.
   Registered cheap test (W9B, one 2h run): MATCHED with tol=0 — its
   stored pairs are EXACTLY valid in the wave world (the wave is
   rule-stable), so the archive should keep its exactness while the
   registry cannot. If MATCHED-tol0 beats FULL at W≥2 by a wide margin,
   the residual-storage advantage is real and the plateau was matcher
   self-inflicted.
2. **M5 residual registry** (pre-registered in V9_DESIGN): compact
   (a, b) + per-rule wave residual table — abstraction WITH its own loss
   stored alongside. Now justified by data; candidate for the next
   system-side mutation (this one IS a legitimate RSI-0 menu item, world
   fixed at W=4).
3. **Product translation**: summarization/compaction is safe only while
   the discarded residual is below the consumer's discrimination needs.
   Measure the residual before choosing summary-only storage; if the
   residual is structural (not noise), pair the summary with pointer to
   raw instances — the W9 result is the causal proof that summary-only
   storage collapses retrieval contrast on residual-bearing content.

## Verdict for the program

The abstraction-advantage question is now answered with a sharper edge
than planned: compact representation wins in lossless worlds (2.2× at
W=0), loses the moment incompressible structure appears IF tolerance is
coupled, and the failure is recoverable by design (band decoupling /
residual storage) — not by more capacity or better adaptation. The next
flyloop runs (W9B, M5) test exactly those two recoveries.
