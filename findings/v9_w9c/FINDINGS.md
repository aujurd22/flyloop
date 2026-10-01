# W9C findings — M5 (residual registry) works: first significant recovery of the abstraction cliff, pending replication

Run: 2026-10-01 20:59 → 22:59, W=4, ε=0.15, arms **FULL-RES** (M5) / FULL /
EPISODIC, 5370 cycles, 0 failures. World bit-identical to W9A/B W=4.

## Controls

**FULL reproduced the W9B FULL bit-for-bit: 2685/2685 puzzle events
identical** — third consecutive harness pass. The paired contrast below is
measured against a control whose trajectory is provably the same world.

## Verdict: the residual registry recovers a significant slice of the cliff

| arm (W=4) | E20 | CI | n_ep |
|---|---|---|---|
| W9A/B FULL (=W9C control) | 10.58–10.92 | — | 43–50 |
| **W9C FULL-RES (M5)** | **9.696** | [8.32, 11.22] | 46 |

**Paired FULL − FULL-RES = +0.787, CI [+0.229, +1.364]** — excludes zero.
Probe-level: res-armed predictions err 75% vs 85% unarmed (253 armed of
3987 rule-path probes). Engineering: 118 residual writes, 0 res_err, 0
readback failures.

## Reading: a recovery, not a rescue

The cliff was ~9 E20 points deep (1.14 → ~10.5); M5 recovers ~0.8 (~7%).
Why only that: the residual table holds ≤4 confirmed pairs per rule over
13 residues — between the nearest stored x and the probe x, the wave's
shape difference remains unpredictable. The 75%-vs-85% armed gap is the
anchor working; the remaining ~75% is sparsity, not mechanism failure.
Registered scaling lever (W9D, queued): RES_CAP ↑ and longer runs fill
the table; the true replication (fresh RUNSEED) must precede any
"accepted" language per the G4 rule.

## Process notes (what the G4 discipline bought)

- The paired contrast is same-seed by design and the control is
  bit-identical — the comparison is exact.
- This is the first NEW-AXIS mutation (store the abstraction's own loss)
  after the menu-exhaustion conclusion, and the first positive paired
  delta since G3 — but unlike G3, it enters the lineage as
  "single-run, replication queued", never as confirmed.
- Implementation battle wounds (all caught before burning the run):
  refit-residual added back to the polluted fit (never took effect),
  write-capped table truncating samples, string table keys, and a
  shared-store FULL-RES/FULL draft (preflight check #1 caught it — the
  V7C lesson repeating productively).

## Ledger

| hypothesis | verdict |
|---|---|
| W9B "prediction-layer compression carries the plateau" | CONFIRMED (adding the residual back recovers a significant slice) |
| M5 P1 "beat the plateau by a wide margin" | PARTIAL: significant, ~7% not ~50% |
| M5 P2 "advantage grows with table fill" | SUPPORTED directionally (armed 75% vs unarmed 85%); scaling test queued |
| M5 P3 "flip resistance via 2-of-2 confirmation" | HELD (0 poison events, 0 res_err) |

---

**REPLICATION RESOLVED (10-02 01:07).** W9D (fresh RUNSEED=20261001,
independent realizations, diverges from W9C at event 0, 2979 cycles, 0
failures): **FULL-RES advantage +1.208, CI [+0.526, +1.793]** — replicated,
same direction, larger magnitude, 151 res-armed probes. Two independent
realizations, both significant:

| run | realizations | paired FULL−FULL-RES | verdict |
|---|---|---|---|
| W9C | same-seed (bit-identical control) | +0.804 CI[+0.244, +1.404] | SIG |
| W9D | fresh-seed | +1.208 CI[+0.526, +1.793] | SIG |

**M5 is ACCEPTED into the lineage** — the first accepted mutation on a new
axis (storing the abstraction's own loss), and the first to pass the full
G4-rule gauntlet: same-seed paired contrast + fresh-seed independent
replication, both excluding zero. Lineage gen-6 upgraded.
