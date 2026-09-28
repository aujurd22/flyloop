"""V7 Phase A adjudication: the 2x2 factorial (support x write-verification).

Cells (RECALL episodes of discovered rules, eps=0.25, paired cross-run by
(family, epoch, probe_idx) — the world is a pure function of the schedule):
  FULL      (V5B run: rule registry, verified write)
  F-RAW     (V7A run: rule registry, raw write)
  M         (V5B run: sparse archive, raw write)
  M-VER     (V7A run: sparse archive, verified write)

Factorial contrasts (cluster bootstrap by rule lineage):
  dW_full   = E20(F-RAW) - E20(F)     write-verification effect at full support
  dW_sparse = E20(M) - E20(M-VER)    write-verification effect at sparse support
  dS_ver    = E20(M-VER) - E20(F)    support effect at verified write
  dS_raw    = E20(M) - E20(F-RAW)    support effect at raw write

Usage:
    python experiments/compare_v7.py --ref runs/v5b_... --run runs/v7a_...
"""
import argparse
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from analyze_v4 import load_probes, load_insights, boot_ci_clustered  # noqa: E402


def contrast(d1, c1, d0, c0, n_boot=10000, seed=23):
    rng = np.random.default_rng(seed)
    if len(d1) == 0 or len(d0) == 0:
        return None, None, None
    d1, c1 = np.asarray(d1, float), np.asarray(c1)
    d0, c0 = np.asarray(d0, float), np.asarray(c0)
    u1, u0 = np.unique(c1), np.unique(c0)
    b1 = {u: d1[c1 == u] for u in u1}
    b0 = {u: d0[c0 == u] for u in u0}
    means = []
    for _ in range(n_boot):
        k1 = rng.choice(u1, size=len(u1), replace=True)
        k0 = rng.choice(u0, size=len(u0), replace=True)
        means.append(float(np.concatenate([b1[u] for u in k1]).mean()
                           - np.concatenate([b0[u] for u in k0]).mean()))
    return float(d1.mean() - d0.mean()), float(np.percentile(means, 2.5)), \
        float(np.percentile(means, 97.5))


def cell_gaps(run_dir):
    """Per-episode (M−F) gaps + rule clusters + episode metadata."""
    arms = load_probes(run_dir)
    F, M = arms["FULL-RAW"] if "FULL-RAW" in arms else arms["FULL"], \
        arms["MATCHED-VER"] if "MATCHED-VER" in arms else arms["MATCHED"]
    keys = sorted(set(F) & set(M))
    rows = []
    for k in keys:
        if F[k]["type"] != "RECALL":
            continue
        rows.append({"key": k, "gap": M[k]["e20"] - F[k]["e20"],
                     "rule": F[k]["rule_id"]})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", required=True, help="V5B run dir (verified/raw cells)")
    ap.add_argument("--run", required=True, help="V7A run dir (raw/verified cells)")
    ap.add_argument("--boot", type=int, default=10000)
    args = ap.parse_args()
    ref, run = os.path.abspath(args.ref), os.path.abspath(args.run)
    ref_rows = cell_gaps(ref)
    run_rows = cell_gaps(run)
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say(f"# V7 Phase A analysis — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    say(f"ref={args.ref}  run={args.run}")
    say(f"episodes: ref n={len(ref_rows)}, run n={len(run_rows)}")

    def gaps(rows, pred):
        return np.array([r["gap"] for r in rows if pred(r)], float), \
            [r["rule"] for r in rows if pred(r)]

    # cells: rule-lineage pairing is not required across runs (independent
    # draws of the same schedule); each cell's mean is cluster-bootstrapped
    F = np.array([r["gap"] for r in ref_rows], float)        # verified/full (M-F gaps)
    T = np.array([r["gap"] for r in run_rows], float)        # raw/ver (M-VER - F-RAW)
    loF, hiF = boot_ci_clustered(F, [r["rule"] for r in ref_rows], args.boot)
    loT, hiT = boot_ci_clustered(T, [r["rule"] for r in run_rows], args.boot)
    say(f"dW_sparse (M vs M-VER, ref run):  {float(np.mean(F)):.3f} "
        f"CI[{loF:.3f},{hiF:.3f}] n={len(F)}")
    say(f"dW_full_raw (M-VER vs F-RAW, run): {float(np.mean(T)):.3f} "
        f"CI[{loT:.3f},{hiT:.3f}] n={len(T)}")

    # cross-run cell gaps: F-RAW vs F and M-VER vs M need per-episode pairing
    # across DIFFERENT runs — not paired (different arms wrote them); use
    # independent cluster bootstrap on each side's mean
    def arm_mean(run_dir, arm):
        arms = load_probes(run_dir)
        A = arms[arm]
        keys = sorted(set(A))
        rec = [k for k in keys if A[k]["type"] == "RECALL"]
        d = np.array([A[k]["e20"] for k in rec], float)
        cl = [A[k]["rule_id"] for k in rec]
        m, lo, hi = boot_ci_clustered(d, cl, args.boot)
        return m, lo, hi, len(d)

    mF = arm_mean(args.ref, "FULL")
    mFR = arm_mean(args.run, "FULL-RAW")
    mM = arm_mean(args.ref, "MATCHED")
    mMV = arm_mean(args.run, "MATCHED-VER")
    say(f"E20 FULL     (V5B, verified/full):      {mF[0]:.3f} CI[{mF[1]:.3f},{mF[2]:.3f}] n={mF[3]}")
    say(f"E20 FULL-RAW (V7A, raw/full):          {mFR[0]:.3f} CI[{mFR[1]:.3f},{mFR[2]:.3f}] n={mFR[3]}")
    say(f"E20 MATCHED  (V5B, raw/sparse):        {mM[0]:.3f} CI[{mM[1]:.3f},{mM[2]:.3f}] n={mM[3]}")
    say(f"E20 M-VER    (V7A, verified/sparse):   {mMV[0]:.3f} CI[{mMV[1]:.3f},{mMV[2]:.3f}] n={mMV[3]}")

    dW_full = mFR[0] - mF[0]
    dW_sparse = mM[0] - mMV[0]
    dS_ver = mMV[0] - mF[0]
    dS_raw = mM[0] - mFR[0]
    say(f"factorial: dW_full={dW_full:.3f} dW_sparse={dW_sparse:.3f} "
        f"dS_ver={dS_ver:.3f} dS_raw={dS_raw:.3f}")

    with open(os.path.join(run, "analysis_v7a.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("analysis written to analysis_v7a.md (factorial verdicts applied by "
        "operator review — the registered bands live in V7_DESIGN.md)")


if __name__ == "__main__":
    main()
