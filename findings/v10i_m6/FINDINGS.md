# M6 PRE-REGISTER: delta retrieval — error-triggered historical-b recovery

**Registered before implementation** (2026-10-05 evening, prior to any
M6 run). External stimulus: cross-repo audit (2026-10-05) identified
"delta as second-class citizen — representation yes (M5), retrieval no"
as the top cheap gap; the audit's own readings (ε=0.15, R1-R8) were
verified WRONG and are NOT part of this registration.

## Background

V10 (M6=δ placeholder) showed drift kills both architectures. In the
PERIODIC family the drift is `b_k = (b0 + delta*k) mod 13` with
delta ∈ {1,2}, gcd(delta,13)=1 — so **the k-th and (k+13)-th visits
present the IDENTICAL rule**. M5's residual ledger (`res_seen`) keeps
every historical confirmed (x→y) observation per rule, across visits.
Neither the prediction path (wave_est anchors to recent pairs only)
nor the identification path ever looks up history.

## Hypothesis

On re-visits beyond cycle k=13 (state recurrence), an
error-triggered lookup of the rule's own historical confirmed pairs —
recovering the historical `b_hist = (y - a*x) mod p` consistent with
current observations — recovers the correct prediction immediately,
instead of re-learning from scratch (fresh identification ≈ full
episode of probes).

## Manipulation

Arm M5 (control): current FULL-RES behavior.
Arm M6 (`FLYLOOP_DELTA_RETRIEVE=1`): identical, plus — when the
current anchor prediction misses ≥2 consecutive probes (drift
signal), compute `b_cand = (y_obs - a*x_obs) mod p` from fresh
probes against the CURRENT fit's slope a (slope is drift-invariant
in PERIODIC), count historical occurrences of b_cand in the rule's
`res_seen` ledger (bucketed by visit era), and if a historical era
matches ≥2 fresh probes, predict with `b_cand` directly.

## Protocol

- World: COMPOSITE=1 (CAP=2) with PERIODIC family active, 4 arms
  (FULL-COMP / FULL / MATCHED / EPISODIC) as in M7 runs, 2h,
  paired schedule (same SEED), two RUNSEEDs (G4′ rule).
- PRIMARY metric: PERIODIC-family puzzle err100 on visits k≥13
  (post-recurrence), paired M6 − M5.
- SECONDARY: probes-to-first-correct after each recurrence.
- Adjudication: cluster bootstrap CI on the paired delta; numbers read
  from the run's own counters/events JSONL, never from console text.

## Opening conditions (both directions, pre-committed)

- M6 better, CI excludes 0 → ACCEPTED: delta gains retrieval rights.
- M6 not better (CI includes 0 or worse) → RETRACTED: delta keeps
  structural rights only (M5 stands); the retrieval ladder does NOT
  get a delta tier; V11 recovery protocol must not assume it.
- Either way the ledger records the audit's role as stimulus only.
