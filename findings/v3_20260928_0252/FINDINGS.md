# V3 run v3_20260928_0252 — findings (recurrent drift × memory consolidation)

2026-09-28 02:52 → 12:52, 10 h deadline, 48317 cycles, 0 cycle failures, 0
breaker trips, full http/http, write parity byte-exact (36339 = 36339), 0
readback failures, ~10.5k entries per store. run_status OK. Paired design:
FULL (rule registry) vs EPISODIC (tables only), identical world schedule
(NEW 135 / VARIANT 71 / RECALL 78 episodes), padding writes matched exactly.

## Endpoint verdicts (pre-registered V3-P01..P08, applied by analyze_v3.py)

| ID | Claim | Verdict | Evidence |
|---|---|---|---|
| P01 (primary) | FULL lower E20 on RECALL | **CONFIRMED** | dE20=+0.641, 95% CI [0.513, 0.769], n=78, perm_p<1e-4 |
| P02 (primary) | FULL shorter recovery latency | **CONFIRMED** | dLat=+0.551, CI [0.423, 0.679], perm_p<1e-4 |
| P03 | advantage at every gap 2/3/4/5 | **CONFIRMED** | +0.63 / +0.71 / +0.47 / +0.75 (n=24/17/17/20) |
| P04 (NC1) | VARIANT |dE| << RECALL |dE| | **CONFIRMED** | 0.014 vs 0.641 — the advantage is recurrence-specific |
| P05 | SIR(FULL) <= 1.5 x SIR(EPI) | **CONFIRMED** | 0.0408 vs 0.0287, ratio 1.42 — real interference, inside the band |
| P06 | useful-insight rate above null | **CONFIRMED (narrow)** | UIR 0.712 vs null-95 0.693 — above the pre-registered line by a hair; treat as weak |
| P07 | FULL degrades slower with noise | **INCONCLUSIVE** | phase C (60k+) never entered: 48317 < 60000. Design mis-calibration |
| P08 (NC2) | fact lane no regression | **INCONCLUSIVE** | no regression observed through phase B (0.0696/0.0681, arms identical), but the registered phase-C criterion is unevaluable |

6 CONFIRMED / 2 INCONCLUSIVE, 0 REFUTED.

## The mechanism, resolved

RECALL recovery is a two-observation story, and the whole advantage lives in
the one-observation head start:

```text
probe 1  FULL: fit_stale 56 / cold 22   (blind — previous episode's table)
         EPI:  fit_stale / cold          (same blindness)
probe 2  FULL: book_test 52/78          (ONE live pair uniquely matches a
         EPI:  guess 26 / fit needs 2    stored rule -> adopted)
probe 3  FULL: book_test 76/78
         EPI:  fit (two pairs now available)
latency: FULL 1:12, 2:44, 3:20 | EPI 1:10, 2:8, 3:55
```

E20 by episode type: RECALL 1.179 (FULL) vs 1.821 (EPI); NEW 1.926 vs 1.933;
VARIANT 1.761 vs 1.775. Structured memory buys ~0.64 errors per recurrence —
and nothing at all on parameter changes (VARIANT) or fresh rules (NEW). That
is the clean signature of *reuse*, not generic capability: the registry pays
exactly when the past returns.

## The cost is real and measured

SIR(FULL)=0.0408 vs SIR(EPI)=0.0287 (ratio 1.42, inside the registered 1.5
band): remembering more means intruding more — old rules adopted for the
current episode. The pre-registered reading holds: memory acceleration and
memory interference are the same mechanism's two faces, and the band is where
the trade stays acceptable.

## Honest failures

1. **P07/P08 unevaluable by design**: the three-phase noise schedule
   (phase C at 60k+) assumed more cycles than 10 h delivers at the paired
   pace (48.3k). Phase C never ran. Registered as a design mis-calibration;
   both verdicts INCONCLUSIVE, not failed.
2. **P06 margin is thin** (0.712 vs 0.693): the useful-insight rate clears
   the permutation null but not convincingly. The UIR definition (discovery
   counts only if its rule later pays off) is the right target; a follow-up
   should either collect more recurrences per rule or use a stricter null.
3. **Probe-1 is never an instant recovery**: 0/78 for both arms. "Instant"
   in this design means one observation, not zero. A zero-observation
   recognition path would need a different retrieval interface (query the
   book BEFORE the first probe — plausible next iteration).

## Quotas

RECALL 78/75 met; NEW 135/150, VARIANT 71/75, shocks 80/100 unmet — deadline
was the binding stop (anticipated by the spec). Statistics on RECALL (the
primary unit) are above quota.

## Ties to the program

- FlyPoet side: "surprise-gating = update throttling" (v2 CL result) said
  *when* to write matters less than *how much*. V3 now shows the payoff side:
  *what* you keep (structured rules vs raw episodes) decides how fast the
  future re-learns — with a measurable interference tax.
- intuition-mechanism side: P32-h's "recognition without novelty" and P34-d's
  "cue extraction" split perceiving structure from detecting change. V3's
  stale-intrusion rate is the closed-loop version of that dissociation: a
  memory system can recognize the returning past AND still misfile it as the
  present — both happened, both were counted, the band held.
- The useful-insight criterion (P06: a discovery is insight only if a future
  recurrence shows verifiable benefit) is FlyLoop's operational answer to
  "discovery != insight".
