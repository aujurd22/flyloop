"""RSI-0 G4 adjudication: replication of the adaptive read policy (gen 3 -> gen 4).

Metric (same convention as compare_v7.py):
  E20 = errors over the first 20 probes of a RECALL episode, averaged over
  qualifying episodes (RECALL episodes of rules DISCOVERED by the run's own
  adaptive arm), cluster bootstrap by rule lineage.

Outputs:
  1. E20 per arm in G4 (FULL-ADAPT / MATCHED / EPISODIC) with CI
  2. Paired contrast G4 FULL-ADAPT vs parent v6t FULL (gen 0 config,
     MATCH_MIN_FRAC=0.6 fixed) on common (family, epoch) keys
  3. Replication contrast G4 FULL-ADAPT vs G3 FULL-ADAPT (independent runs,
     same mutation)

Usage: python experiments/rsi0_g4_eval.py
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from compare_v7 import load_probes_v7, contrast  # noqa: E402
from analyze_v4 import load_insights, boot_ci_clustered  # noqa: E402

RUNS = {
    "v6t (gen0 fixed)": ("runs/v6t_20260928_2159", "FULL"),
    "g3 (gen3 adaptive)": ("runs/rsi0_g3_20260930_0808", "FULL-ADAPT"),
    "g4 (gen4 adaptive)": ("runs/rsi0_g4_20260930_1045", "FULL-ADAPT"),
    "g4 MATCHED": ("runs/rsi0_g4_20260930_1045", "MATCHED"),
    "g4 EPISODIC": ("runs/rsi0_g4_20260930_1045", "EPISODIC"),
}


def e20_list(run_dir, arm, discovered):
    """e20 per qualifying RECALL episode + rule clusters."""
    arms = load_probes_v7(run_dir)
    if arm not in arms:
        return [], []
    out, clusters = [], []
    for k in sorted(arms[arm]):
        ep = arms[arm][k]
        if ep["type"] != "RECALL" or ep["rule_id"] not in discovered:
            continue
        out.append(ep["e20"])
        clusters.append(ep["rule_id"])
    return out, clusters


def main():
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("=== RSI-0 G4 adjudication (adaptive read policy replication) ===")
    say(f"generated: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}")
    say()

    per_run = {}
    for label, (run, arm) in RUNS.items():
        discovered = set(load_insights(os.path.join(ROOT, run)).keys())
        vals, clusters = e20_list(os.path.join(ROOT, run), arm, discovered)
        per_run[label] = (vals, clusters)
        if not vals:
            say(f"{label}: NO qualifying episodes")
            continue
        mean, lo, hi = boot_ci_clustered(np.array(vals, float), clusters)
        say(f"{label}: E20 = {np.mean(vals):.3f} "
            f"CI[{lo:.3f},{hi:.3f}] n_ep={len(vals)} "
            f"n_rules={len(set(clusters))}")

    say()
    say("--- Paired contrasts (common (family,epoch) RECALL keys, "
        "cluster bootstrap) ---")

    def paired(a, b, key_a, key_b):
        """deltas on common keys; qualification: RECALL + discovered by a's own
        adaptive/FULL arm in each run."""
        ra, aa = RUNS[a]
        rb, ab = RUNS[b]
        A = load_probes_v7(os.path.join(ROOT, ra))[aa]
        B = load_probes_v7(os.path.join(ROOT, rb))[ab]
        da = set(load_insights(os.path.join(ROOT, ra)).keys())
        db = set(load_insights(os.path.join(ROOT, rb)).keys())
        deltas, clusters = [], []
        for k in sorted(set(A) & set(B)):
            if A[k]["type"] != "RECALL" or B[k]["type"] != "RECALL":
                continue
            if A[k]["rule_id"] not in da or B[k]["rule_id"] not in db:
                continue
            deltas.append(B[k]["e20"] - A[k]["e20"])
            clusters.append(A[k]["rule_id"])
        d = np.array(deltas, float)
        mean, lo, hi = boot_ci_clustered(d, clusters)
        effect = "IMPROVEMENT" if mean < 0 else "regression"
        sig = "SIG" if hi < 0 or lo > 0 else "n.s."
        say(f"{b} - {a}: {mean:+.3f} CI[{lo:+.3f},{hi:+.3f}] "
            f"n_ep={len(d)} -> {effect} ({sig})")

    paired("v6t (gen0 fixed)", "g4 (gen4 adaptive)", None, None)
    say()
    paired("g3 (gen3 adaptive)", "g4 (gen4 adaptive)", None, None)

    out_path = os.path.join(ROOT, "runs", "rsi0_g4_20260930_1045",
                            "g4_adjudication.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwritten: {out_path}")


if __name__ == "__main__":
    main()
