# V11 PRE-REGISTER (design): the world that hits back

Design registration only — implementation deferred until M6
adjudicates (the recovery protocol below depends on whether delta
retrieval earns retrieval rights). Registered 2026-10-05 evening.

## Motivation

Every law in this program was measured in a closed world: the
schedule is a pure function of the seed, error never confounds
(world.py cannot be changed by what the agent does). V8-LLM showed
closed-world laws do not guarantee extrapolation. The known gap
(registry, P-series): intervention-rich worlds (OED-style) — the
agent cannot distinguish "my calibration is off" from "the world
changed", because the world never reacts and never hides.

## What changes (world.py v11)

1. **Hidden state**: a latent variable θ_t in the world, not
   observable from any probe output directly, evolving by a seeded
   stochastic rule (schedule keys stay C.SEED; realization keys
   C.RUNSEED — the G4′ split carries over).
2. **Reactivity**: agent probes consume or perturb θ (e.g., probing
   a family advances its drift clock; writing a wrong rule poisons
   the next episode's noise draw). The agent's own actions move the
   world — error attribution becomes non-trivial.
3. **Probe = prediction**: every probe returns a score, and the
   world logs the counterfactual branch (what the score would have
   been under not-probing) at a capped budget — this is the
   mechanism that makes error confounding decidable post-hoc.

## Pre-registered predictions

- P11.1 (failure): the current M5/M7 registry protocol degrades in
  the reactive world — drift-era attribution errors rise (recovery
  time after reactive events worse than after schedule-driven era
  changes of equal magnitude), because the agent's attribution is
  "world changed" vs "I changed" blind.
- P11.2 (fix): counterfactual double-run (hold one branch fixed per
  ambiguous event) restores recovery to closed-world levels, at ~2x
  probe budget; the delta-retrieval mechanism (M6, if ACCEPTED)
  reduces the double-run budget needed.
- P11.3 (curiosity): a probe-selection policy minimizing expected
  post-probe error (active sampling) beats uniform probing in the
  reactive world but NOT in the closed world — the reactive world
  is what makes curiosity measurable.

## Opening conditions

- P11.1 fails (attribution error does not rise) → the reactive
  world adds no measurement value at this scale; register what it
  does change instead, or retract the axis.
- P11.2's double-run budget >4x → flag as impractical, redesign.
- P11.3 uniform ≈ active in reactive world → curiosity claim dead.

## Cost & dependency

world.py rewrite (pure function → stateful class) + supervisor
compat + re-running the anchor contrasts (M5 registry arms) in the
reactive world. 1-2 weeks engineering. Depends on M6 verdict only
for P11.2's second clause; P11.1/P11.3 can run before M6 lands.
