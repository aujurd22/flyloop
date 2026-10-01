"""V10b E1 adjudication: BOOK_CAP=2 vs V10 BOOK_CAP=5 (same seed), the
P-COMBO evidence-chain destruction test. Per-type RECALL E20 + composite
probe-1 hit rate, FULL vs MATCHED, cross-run paired by (family, epoch)."""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from compare_v7 import load_probes_v7  # noqa: E402
from analyze_v4 import load_insights, boot_ci_clustered  # noqa: E402

TYPE_OF_FAM = {0: "standard", 1: "periodic", 2: "composite", 3: "standard"}
RUNS = {
    "CAP5 (V10)": "runs/v10_20261001_2117",
    "CAP2 (V10b)": "runs/v10_cap2_20261002_0241",
}


def main():
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("=== V10b E1: evidence-chain budget (BOOK_CAP=2 vs 5) ===")
    for tag, run in RUNS.items():
        P = load_probes_v7(os.path.join(ROOT, run))
        disc = set(load_insights(os.path.join(ROOT, run)).keys())
        say(f"\n--- {tag} ---")
        for arm in ("FULL", "MATCHED"):
            for typ in ("standard", "periodic", "composite"):
                vals, cl = [], []
                for k, ep in P.get(arm, {}).items():
                    if ep["type"] != "RECALL" or TYPE_OF_FAM.get(k[0]) != typ:
                        continue
                    if ep["rule_id"] not in disc:
                        continue
                    vals.append(ep["e20"])
                    cl.append(ep["rule_id"])
                if not vals:
                    continue
                m, lo, hi = boot_ci_clustered(np.array(vals, float), cl)
                say(f"  {arm:8s} {typ:10s}: E20 {np.mean(vals):6.3f} "
                    f"[{lo:.3f},{hi:.3f}] n={len(vals)}")
        # composite probe-1 (FULL)
        tot = hit = 0
        for k, ep in P.get("FULL", {}).items():
            if TYPE_OF_FAM.get(k[0]) != "composite" or ep["type"] != "RECALL":
                continue
            if not ep["probes"]:
                continue
            tot += 1
            hit += 1 - ep["probes"][0]["error"]
        if tot:
            say(f"  FULL composite probe-1: {hit}/{tot} = {hit/tot*100:.0f}%")

    # paired composite deltas (FULL, CAP2 - CAP5) on common episode keys
    say("\n--- paired FULL composite E20 (CAP2 - CAP5) ---")
    A = load_probes_v7(os.path.join(ROOT, RUNS["CAP5 (V10)"]))["FULL"]
    B = load_probes_v7(os.path.join(ROOT, RUNS["CAP2 (V10b)"]))["FULL"]
    dA = set(load_insights(os.path.join(ROOT, RUNS["CAP5 (V10)"])).keys())
    deltas, cl = [], []
    for k in sorted(set(A) & set(B)):
        if (TYPE_OF_FAM.get(k[0]) != "composite" or
                A[k]["type"] != "RECALL" or B[k]["type"] != "RECALL"):
            continue
        if A[k]["rule_id"] not in dA:
            continue
        deltas.append(B[k]["e20"] - A[k]["e20"])
        cl.append(A[k]["rule_id"])
    if deltas:
        m, lo, hi = boot_ci_clustered(np.array(deltas, float), cl)
        say(f"composite FULL degradation: {m:+.3f} CI[{lo:+.3f},{hi:+.3f}] "
            f"n={len(deltas)} {'(SIG)' if hi < 0 or lo > 0 else '(n.s.)'}")

    out = os.path.join(ROOT, "findings", "v10b_e1.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
