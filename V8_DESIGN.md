# DESIGN V8 — noise × read-tolerance × coverage: can the system distinguish
# "no candidate" from "candidate exists but the observation is flipped"?

Status: registered 2026-09-29 morning, before launch. Follows the operator
review's Layer-1 priority and the V7B/V7C conclusions.

## 1. The question

V7A/V5B/V6T's probe-1 failure decomposition (unexplained = 0) showed the
failures split into ~50% flipped-reveal and ~30-50% no-candidate. G2 proved
that adding candidates does NOT recover flipped observations. V7C proved
shallow write beats deep write under noise. The open question, per the
review:

> **Can the system distinguish "no candidate" from "candidate exists but the
> observation is flipped"?**

If YES (the flip rate is estimable online), the read policy can ADAPT: lower
the match bar as estimated noise rises, keeping true rules recoverable while
the strict-argmax constraint still refuses garbage. That is RSI-0's first
"mechanism self-change" mutation — the policy adjusts itself to a measured
world property, not to a hand-tuned constant.

## 2. Manipulation and arms

- **World**: ε (reveal-flip probability) swept ∈ {0.15, 0.40} as two short
  runs, compared against the existing ε=0.25 body (V5B/V6T/V7A/V7C — same
  schedule/seed). ε=0.15 tests the low-noise end; ε=0.40 tests whether the
  adaptive policy degrades gracefully past the g0 design point.
- **Arms** (each run, 3 arms):
  - FULL-ADAPT: rule registry; matcher min_frac ADAPTS online —
    `min_frac_eff = clamp(BASE − k·ε̂, 0.50, BASE)` where ε̂ is the rolling
    estimate of the reveal-flip rate over the last 20 live pairs vs the
    best-matching stored rule, and BASE = 0.6.
  - FULL-FIX06: min_frac fixed at 0.6 regardless of ε (V6T/V7C behavior).
  - EPISODIC: live-fit only (unchanged control).
- MATCHED arm dropped this round: V7A/V7C showed the sparse archive is
  dominated under noise; removing it doubles the per-cycle speed and the
  question does not involve it.

## 3. Registered predictions

| ID | Claim |
|---|---|
| V8-P01 | ε̂ tracks ε: at ε=0.15, ε̂ ∈ [0.08, 0.22]; at ε=0.40, ε̂ ∈ [0.30, 0.50]; monotone in ε across runs. (The estimator works.) |
| V8-P02 | FULL-ADAPT beats FULL-FIX06 at ε=0.40 (E20 difference, cluster CI excludes 0): the adaptive bar keeps true rules recoverable when fixed-tolerance starts failing. |
| V8-P03 | At ε=0.15, ADAPT ≈ FIX06 (no harm at low noise; CI of the difference includes 0). |
| V8-P04 | probe-1 recovery: ADAPT ≥ 50% at ε=0.40 (the adaptive bar accepts 1-pair matches that exact matching would refuse). |
| V8-P05 | Stale-intrusion cost of adaptation ≤ 1.5× the fixed arm's (the V7A lesson gate). |

## 4. Implementation

- `cycle.py`: FULL-ADAPT arm (env `FLYLOOP_ARMS` gains "FULL-ADAPT"); the
  runner keeps a deque(20) of live-pair match outcomes vs the best stored
  rule; ε̂ = 1 − mean(match_frac); `min_frac_eff` recomputed per probe.
- `reasoner.py`: `frac_best` and the book_test path take min_frac as a
  parameter (already done in V6/V7 work — verified).
- The world ε knob already exists (`NOISE_EPS`, V5) — unchanged.

## 5. Stop rules

RECALL ≥ 45 or 2.5 h per run; engineering tripwires unchanged. Both runs
share the schedule/seed → paired.

## 6. Registered next (Layers 2-3, from the operator review)

- intuition-mechanism: P91 n-expansion (20-30 matched pairs, degree/gdepth
  balanced); prime/composite boundary theorem (character/genus obstruction
  formalized — no more composite-d Pell formula hunting).
- flymemory: freeze TREE/cleanup lines; new = coarse→needle retrieval and
  the dedup-threshold × storage × fidelity triple.
- Synthesis target: the Memory Geometry Controller becomes RSI-0's mutation
  menu — the controller's outputs (memory type, capacity, eviction, write
  verification depth, query gate) ARE the policy axes this program has been
  measuring.
