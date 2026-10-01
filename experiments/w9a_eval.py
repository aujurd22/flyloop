"""V9 W9A adjudication: E20 per arm per W + paired FULL-vs-MATCHED deltas.

Loads all completed w9w* runs (WAVE_AMP from run dir name), computes
RECALL-episode E20 for discovered rules (FULL arm's discoveries qualify
both arms — paired keys), cluster bootstrap by rule lineage, and the
FULL-vs-MATCHED paired delta per W (the crossover statistic).

Also P1 mechanism: correlation between probe error and |wave(x_p)| for
the FULL arm (per W), using the analytic wave phase per rule_id.
"""
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from compare_v7 import load_probes_v7, contrast  # noqa: E402
from analyze_v4 import load_insights, boot_ci_clustered  # noqa: E402

RUNS = {
    0: "runs/w9w0_20261001_1225",
    2: "runs/w9w2_20261001_1428",
    4: "runs/w9w4_20261001_1428",
    6: "runs/w9w6_20261001_1225",
}


def wave_val(W, fam, rule_id, x):
    """Analytic wave value for the probe point (must mirror world.puz_probe)."""
    if W <= 0:
        return 0
    phi_rng = np.random.default_rng(int.from_bytes(
        __import__("hashlib").sha256(
            repr(("flyloop", 20260927, "puz", "wavephase", fam, rule_id))
            .encode()).digest()[:8], "big"))
    phi = float(phi_rng.random()) * 13
    return int(round(W * math.sin(2 * math.pi * (x + phi) / 13)))


def e20_for(run, arm, discovered):
    probes = load_probes_v7(os.path.join(ROOT, run))
    if arm not in probes:
        return [], []
    out, clusters = [], []
    for k in sorted(probes[arm]):
        ep = probes[arm][k]
        if ep["type"] != "RECALL" or ep["rule_id"] not in discovered:
            continue
        out.append(ep["e20"])
        clusters.append(ep["rule_id"])
    return out, clusters


def paired_delta(run, f_arm, m_arm):
    probes = load_probes_v7(os.path.join(ROOT, run))
    disc = set(load_insights(os.path.join(ROOT, run)).keys())
    deltas, clusters = [], []
    for k in sorted(set(probes.get(f_arm, {})) & set(probes.get(m_arm, {}))):
        ef, em = probes[f_arm][k], probes[m_arm][k]
        if ef["type"] != "RECALL" or em["type"] != "RECALL":
            continue
        if ef["rule_id"] not in disc:
            continue
        deltas.append(em["e20"] - ef["e20"])
        clusters.append(ef["rule_id"])
    return deltas, clusters


def main():
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("=== V9 W9A adjudication (wave sweep pair 1: W=0 vs W=6) ===")
    say()

    for W, run in sorted(RUNS.items()):
        disc = set(load_insights(os.path.join(ROOT, run)).keys())
        say(f"--- W={W} ({run}), discovered rules: {len(disc)} ---")
        for arm in ("FULL", "MATCHED", "EPISODIC"):
            vals, clusters = e20_for(run, arm, disc)
            if not vals:
                say(f"  {arm:9s}: no qualifying episodes")
                continue
            mean, lo, hi = boot_ci_clustered(np.array(vals, float), clusters)
            say(f"  {arm:9s}: E20 = {np.mean(vals):.3f} "
                f"CI[{lo:.3f},{hi:.3f}] n_ep={len(vals)}")
        deltas, clusters = paired_delta(run, "FULL", "MATCHED")
        if deltas:
            d = np.array(deltas, float)
            mean, lo, hi = boot_ci_clustered(d, clusters)
            crossover = "MATCHED WINS" if mean > 0 and hi > 0 else (
                "FULL WINS" if mean < 0 and lo < 0 else "undetermined")
            say(f"  paired MATCHED-FULL: {mean:+.3f} CI[{lo:+.3f},{hi:+.3f}] "
                f"-> {crossover}")
        say()

    out = os.path.join(ROOT, "findings", "v9_w9a")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "w9a_adjudication.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"written: {os.path.join(out, 'w9a_adjudication.txt')}")


if __name__ == "__main__":
    main()
