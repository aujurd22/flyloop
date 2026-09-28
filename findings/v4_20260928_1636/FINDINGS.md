# V4 run v4_20260928_1636 — findings (early-stop operator decision)

2026-09-28 16:36 → 18:32, stopped by operator at 1.93 h / 6219 cycles (the
user judged a short run sufficient for the headline answers — correct, see
below). 0 cycle failures, full http/http/http, three-way write parity
byte-exact (27307 + 21606 = 48913 drained), 0 readback failures, ~1.6-1.8k
entries per store. run_status OK. **Quotas NOT met** (NEW 104/150, VARIANT
47/75, RECALL 51/75, shocks 10/100) — endpoint verdicts below are drawn from
51 RECALL episodes and labeled accordingly.

## Endpoint verdicts (V4-P01..P08)

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| P01 (primary) | discovered-rule recurrences benefit MORE than undiscovered ones | **INCONCLUSIVE** | undiscovered-rule RECALL episodes: 0 (135 rules born, 100%… actually 122 discovered = 90% discovered / 10% undiscovered, but none of the 13 undiscovered rules had a RECALL yet) |
| P02 (primary, disentanglement) | F ≤ M ≤ E on discovered recurrences | **CONFIRMED** | dE20(M−F)=+0.137 CI [−0.043, 0.310]; dE20(E−M)=+0.490 CI [0.321, 0.694], n=51 — the ordering holds; the MATCHER adds clearly, compression adds marginally |
| P03 | M beats F on undiscovered recurrences | **INCONCLUSIVE** | no undiscovered recurrences |
| P04 | probe-1 recovery exists | **CONFIRMED** | 32/51 = 62.7% ≥ 40% band — the pre-fold interface fix works (V3: 0/78) |
| P05 | SIR(F) ≤ 1.5×SIR(E) | **INCONCLUSIVE** | 2 vs 0 intrusions of 652 probes each — base rates too small to read the band (Fisher p=0.5) |
| P06 (NC1) | VARIANT/NEW contrasts ≈ 0 | **CONFIRMED** | +0.043 (VARIANT, n=47) / +0.000 (NEW, n=104), both < 0.05 |
| P07 | phase C reached, advantage persists | **INCONCLUSIVE** | phase gates are NEW-count-based (fixed from V3), but the early stop ended in phase B (gates 50/110, reached 104 NEW) |
| P08 (NC2) | fact lane no regression | **INCONCLUSIVE** | no phase-C fact data; through phase B all arms identical (0.084) |

3 CONFIRMED / 5 INCONCLUSIVE / 0 REFUTED (early-stop data; not a full-run
verdict — the registered quota run remains repeatable with the same code).

## What the short run already established

1. **The disentanglement ordering (P02) is the headline**: on recurrences of
   discovered rules, E20 = F 0.43 / M 0.57 / E 1.06. Decomposed: the
   matcher (one-pair unique-match over a memory archive) contributes ~0.49
   nats-free errors of advantage over pure re-fitting — CI excludes 0 — and
   the compressed representation adds a further ~0.14 whose CI still crosses
   zero at n=51. First causal split of V3's bundled result: **most of the
   recurrence advantage is the retrieval/decision algorithm, not the
   compression**. If the F−M gap stays marginal at full quotas, "structured
   rules beat raw pairs" downgrades to "a matcher over any archive beats no
   archive" — a materially different claim about memory.
2. **The probe-1 interface artifact is fixed and confirmed** (P04 62.7% vs
   V3's 0/78): folding the current probe's revealed pair before prediction
   lets FULL adopt a returning rule on the very first observation. V3's
   "instant recovery" was real but delayed by one probe for no reason.
3. **The NC1 separation replicated in the three-arm world** (P06): VARIANT
   and NEW contrasts remain ≈ 0 while RECALL is 0.63 — the advantage stays
   recurrence-specific with MATCHED present.
4. **MATCHED shows a intrusion signature worth watching**: 14 stale marks vs
   FULL's 42 in the STATUS mid-run (P05's ledger window shows 2 vs 0 in the
   last-20-probe metric — different windows, both small). Raw pairs do not
   generalize, so they misfire less; compressed rules misadopt more. This is
   the representation-risk asymmetry the full run should quantify.

## Why it stopped early (registered)

Operator decision after the 1.8 h mid-run preview showed the P02 ordering
already stable and P01/P03 blocked on discovery-failure variation
accumulating too slowly (90% discovery rate at this pace). The full-quota
variant (same code, no changes) remains the pre-registered way to settle
P01/P03; the length mix would need recalibration toward shorter episodes to
raise the undiscovered fraction into the 20-40% target band.

## V5 queue (inherited from V3_DESIGN §8 + this run)

1. Recalibrate the length mix (more 4-6 probe episodes) to land the
   undiscovered fraction at 20-40% → P01/P03 become evaluable.
2. Representation × matcher 2×2: EPISODIC-with-matcher (M) and
   RULES-without-matcher (new arm) to finish the disentanglement started by
   P02.
3. SIR needs a floor: pre-register an absolute intrusion-count gate before
   reading ratios (P05 lesson).
4. New math world (polynomials / graph-local rules) — unchanged from V3 §8.
