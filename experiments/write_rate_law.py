"""Write-rate scaling law  p*(r)  on a drifting, interference-limited memory.

Registered experiment, 2026-09-27 (Mushroom-Body Program direction "when is it
worth writing?", abstracted from the flypoet finding that surprise-gated
updates buy nothing over random throttling).

WHY THIS MODEL (design note, recorded before the sweep)
-------------------------------------------------------
Two earlier candidates were tried and rejected in pilot runs (see git history):
  (1) linear Hebbian memory with a write-cost norm cap: monotone — in a linear
      associative memory writes are near-orthogonal, so more writes never hurt;
  (2) delta-rule with renormalization: same monotonicity for the same reason.
The tradeoff in real systems (and in flypoet's continual-learning arms) comes
from GRADIENT STEPS: every update displaces shared parameters and damages
previously fitted tasks. So the model here is two linear-regression tasks
sharing one parameter vector:

    theta in R^d
    OLD task: teacher w_o fixed forever;  loss_o = E[(theta-w_o)^2]-ish
    NEW task: teacher w_n(t) drifts as a random walk, step variance s^2/step
    per cycle with probability p: one LMS step on a fresh sample of the NEW task
    metric_new = ||theta - w_n||^2  (excess, scale-normalised)
    metric_old = ||theta - w_o||^2  (excess, scale-normalised)
    objective  = metric_new + metric_old   (equal weights)

Predicted (pre-run) shape: metric_new ~ eta*d/2 + s^2/(2*eta*p)   (noise floor
+ tracking lag), metric_old grows with p (cumulative displacement).
Optimum of the sum: interior in p for every r = s^2.

REGISTERED PREDICTIONS (experiments/ledger.jsonl, written before the sweep)
---------------------------------------------------------------------------
R1  interior optimum in p for >= 7 of 9 drift rates (both metrics logged).
R2  exponent alpha in p* ~ r^alpha lies in [0.5, 2.0] (alpha=1 i.e. linear
    drift-tracking predicted by the lag term; superlinear if interference
    steepens the cost).
R3  metric_old is non-decreasing in p (>= 8/9 levels, Spearman >= 0.8) — the
    interference cost is the mechanism, not a construct.
R4  a read-error-gated policy at its realized write rate is within 25% of the
    best stochastic policy's total objective (thresholding again vs selection).

Run:  python experiments/write_rate_law.py            (full, ~1 min)
Out:  experiments/results.json, experiments/ledger.jsonl, figs/write_rate_law.png
"""
import argparse
import json
import os
import time
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_JSON = os.path.join(HERE, "results.json")
LEDGER = os.path.join(HERE, "ledger.jsonl")
FIGS = os.path.join(ROOT, "figs")

D = 64
ETA = 0.01        # stable LMS step (stability bound ~2/(D+2*sqrt(D)) ~ 0.028)
T = 8000
BURN = 4000
DRIFTS = [0.00005, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02]
PS = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.7, 1.0]
SEEDS = [1, 2, 3, 4, 5, 6]

# Theory anchor (derived for the linear regime before the sweep): balancing
# the tracking lag (b/p with b = r/(2*ETA)) against the accumulated
# displacement cost (a*c*p) gives p* = sqrt(r) / (ETA^2 * D * sqrt(T)), i.e.
# alpha = 1/2 in the noise-floor-dominated regime. Superlinear alpha appears
# when interference, not lag, binds. R2's band [0.5, 2.0] brackets both.


def seed_for(*parts):
    return zlib.crc32("|".join(str(p) for p in parts).encode()) & 0x7FFFFFFF


def sim(r, p, seed, gated=False):
    """r = random-walk variance per step of the new teacher (drift rate)."""
    rng = np.random.default_rng(seed)
    w_o = rng.standard_normal(D) * 0.5          # old task (fixed)
    w_n = w_o + rng.standard_normal(D) * 0.5    # start near the old solution
    theta = w_o + rng.standard_normal(D) * 0.5
    s = np.sqrt(r)

    new_acc, old_acc = [], []
    writes = 0
    for t in range(T):
        # drift the new teacher (all coordinates, per step)
        w_n = w_n + rng.standard_normal(D) * s
        x = rng.standard_normal(D)
        y = float(w_n @ x)
        noise = rng.standard_normal() * 0.0      # noiseless regression (clean signal)
        pred = float(theta @ x)
        do = (abs(pred - y) > 3.0 * np.sqrt(D) * 0.5 if gated
              else rng.random() < p)
        if do:
            theta = theta + ETA * (y + noise - pred) * x
            writes += 1
        if t >= BURN and t % 50 == 0:
            new_acc.append(float(np.sum((theta - w_n) ** 2)))
            old_acc.append(float(np.sum((theta - w_o) ** 2)))
    n0 = np.mean(new_acc)
    o0 = np.mean(old_acc)
    return {"new_err": float(n0 / D), "old_err": float(o0 / D),
            "total": float((n0 + o0) / D), "write_rate": writes / T}


def parabolic_refine_trunc(ps, errs, k):
    if k <= 0 or k >= len(ps) - 1:
        return float(ps[k])
    x = np.log(ps[k - 1:k + 2]).astype(float)
    y = np.array(errs[k - 1:k + 2], dtype=float)
    denom = (y[0] - 2 * y[1] + y[2])
    if abs(denom) < 1e-12:
        return float(ps[k])
    xv = x[1] + 0.5 * (y[0] - y[2]) / denom * (x[1] - x[0])
    return float(np.exp(np.clip(xv, x[0], x[2])))


def fit_alpha(rs, pstars):
    x = np.log(np.asarray(rs, dtype=float))
    y = np.log(np.asarray(pstars, dtype=float))
    A = np.vstack([x, np.ones_like(x)]).T
    slope, intercept = np.linalg.lstsq(A, y, rcond=None)[0]
    yhat = A @ [slope, intercept]
    ss_res = float(((y - yhat) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return float(slope), 1.0 - ss_res / max(ss_tot, 1e-12)


def register():
    if os.path.exists(LEDGER):
        return
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    rows = [
        {"id": "R1", "claim": "interior optimum in p for >=7/9 drift rates",
         "status": "REGISTERED", "ts": ts},
        {"id": "R2", "claim": "p* ~ r^alpha with alpha in [0.5, 2.0]",
         "status": "REGISTERED", "ts": ts},
        {"id": "R3", "claim": "old-task error non-decreasing in p (>=8/9, Spearman>=0.8)",
         "status": "REGISTERED", "ts": ts},
        {"id": "R4", "claim": "error-gated policy within 25% of best stochastic "
                              "objective at matched realized rate", "status": "REGISTERED",
         "ts": ts},
    ]
    with open(LEDGER, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    print(f"[ledger] registered 4 predictions -> {LEDGER}")


def spearman(a, b):
    a, b = np.asarray(a), np.asarray(b)
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    drifts = DRIFTS[:4] if args.pilot else DRIFTS
    ps = PS[::2] if args.pilot else PS
    seeds = SEEDS[:2] if args.pilot else SEEDS
    register()
    t0 = time.time()
    results = {"config": {"D": D, "ETA": ETA, "T": T, "BURN": BURN,
                          "drifts": drifts, "ps": ps, "seeds": seeds,
                          "objective": "excess_new/D + excess_old/D (equal weights)",
                          "model": "two linear tasks, one theta, LMS writes, "
                                   "random-walk new teacher"},
               "curves": {}, "pstar": {}, "gated": {}}

    pstars, r_ok = [], []
    print("==== stochastic write policy ====")
    for r in drifts:
        curve = {}
        seed_opts = []
        for p in ps:
            vals = [sim(r, p, seed=seed_for(r, p, s)) for s in seeds]
            curve[f"{p:g}"] = {
                "new_err": float(np.mean([v["new_err"] for v in vals])),
                "old_err": float(np.mean([v["old_err"] for v in vals])),
                "total": float(np.mean([v["total"] for v in vals])),
                "write_rate": float(np.mean([v["write_rate"] for v in vals])),
            }
        results["curves"][f"{r:g}"] = curve
        order = [f"{p:g}" for p in ps]
        totals = [curve[k]["total"] for k in order]
        kbest = int(np.argmin(totals))
        interior = 0 < kbest < len(order) - 1
        for s in seeds:
            st = [sim(r, p, seed=seed_for(r, p, s)) for p in ps]
            tt = [v["total"] for v in st]
            seed_opts.append(parabolic_refine_trunc(ps, tt, int(np.argmin(tt))))
        pstar = float(np.median(seed_opts))
        pstars.append(pstar); r_ok.append(r)
        old_vs_p = [curve[k]["old_err"] for k in order]
        print(f"  r={r:g}: best p={order[kbest]} total={totals[kbest]:.4f} "
              f"[new={curve[order[kbest]]['new_err']:.3f} "
              f"old={curve[order[kbest]]['old_err']:.3f}] "
              f"{'interior' if interior else 'EDGE'} p*={pstar:.5f} "
              f"rho(old~p)={spearman(ps, old_vs_p):+.2f} [{time.time()-t0:.0f}s]",
              flush=True)
    alpha, r2 = fit_alpha(r_ok, pstars)
    results["pstar"]["stochastic"] = {"r": r_ok, "pstar": pstars,
                                      "alpha": alpha, "r2": r2}
    print(f"  -> alpha={alpha:.2f} (R^2={r2:.3f})")

    print("\n==== error-gated policy ====")
    for r in drifts:
        vals = [sim(r, 1.0, seed=seed_for(r, "gated", s), gated=True) for s in seeds]
        g = {"new_err": float(np.mean([v["new_err"] for v in vals])),
             "old_err": float(np.mean([v["old_err"] for v in vals])),
             "total": float(np.mean([v["total"] for v in vals])),
             "write_rate": float(np.mean([v["write_rate"] for v in vals]))}
        closest_p = min(ps, key=lambda p: abs(np.log(p / max(g["write_rate"], 1e-9))))
        ref = results["curves"][f"{r:g}"][f"{closest_p:g}"]
        g["ref_p"] = float(closest_p); g["ref_total"] = ref["total"]
        g["ratio"] = g["total"] / max(ref["total"], 1e-9)
        results["gated"][f"{r:g}"] = g
        print(f"  r={r:g}: gated total={g['total']:.4f} rate={g['write_rate']:.4f} "
              f"vs p={closest_p:g} total={ref['total']:.4f} ratio={g['ratio']:.2f}")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=1)
    print(f"\nsaved {OUT_JSON} in {time.time()-t0:.0f}s")
    make_figure(results)


def make_figure(results):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"[fig] skipped: {e}")
        return
    os.makedirs(FIGS, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.4), dpi=150)
    ax = axes[0]
    for r, curve in results["curves"].items():
        ps = [float(k) for k in curve]
        tot = [curve[k]["total"] for k in curve]
        ax.plot(ps, tot, "o-", ms=3, label=f"r={r}")
    ax.set_xscale("log"); ax.set_xlabel("write rate p")
    ax.set_ylabel("total excess error")
    ax.set_title("Error vs write rate (min = optimal)")
    ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=7)
    ax = axes[1]
    for r in ("0.001", "0.01"):
        if r in results["curves"]:
            curve = results["curves"][r]
            ps = [float(k) for k in curve]
            ax.plot(ps, [curve[k]["new_err"] for k in curve], "o-", ms=3,
                    label=f"new task r={r}")
            ax.plot(ps, [curve[k]["old_err"] for k in curve], "s--", ms=3,
                    label=f"old task r={r}")
    ax.set_xscale("log"); ax.set_xlabel("write rate p"); ax.set_ylabel("excess error")
    ax.set_title("The tradeoff: new falls, old rises")
    ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=7)
    ax = axes[2]
    d = results["pstar"]["stochastic"]
    ax.plot(d["r"], d["pstar"], "o-", ms=4, label=f"p* (alpha={d['alpha']:.2f}, R2={d['r2']:.2f})")
    rs = np.array(d["r"])
    if len(rs):
        base = np.median(np.array(d["pstar"]) / rs)
        ax.plot(rs, base * rs, ":", color="gray", label="alpha=1 reference")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("drift rate r"); ax.set_ylabel("optimal write rate p*")
    ax.set_title("Scaling law")
    ax.grid(alpha=0.25, which="both"); ax.legend(fontsize=7)
    fig.tight_layout()
    out = os.path.join(FIGS, "write_rate_law.png")
    fig.savefig(out)
    print(f"[fig] -> {out}")


if __name__ == "__main__":
    main()
