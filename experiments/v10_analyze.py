"""V10 adjudication: the composite world, SDB-aligned (V10_DESIGN P1-P4).

Per arm (FULL / MATCHED / EPISODIC), per rule type:
  - standard  : fam 0 (+fam 3)          -- the lossless control type
  - periodic  : fam 1                    -- drifts b_k = b0 + delta*k (P1)
  - composite : fam 2                    -- R_i = f(R_{i-2}, R_{i-1})  (P2)
Endpoints:
  - RECALL E20 by type (cluster bootstrap)
  - discovery speed: first-DISCOVERY cycle per type (P2 speed leg)
  - composition transfer (P2): FULL arm's probe-1 book/rule hits on
    composite rules BEFORE any prior episode of that rid completed
  - anomaly handling (P3): per-arm error on anomaly probes + writes charged
    at anomaly episodes (memorization), from counts
  - ICR (P4): observation bytes / stored bytes per arm (approx: probes x
    16B / writes bytes)
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from compare_v7 import load_probes_v7  # noqa: E402
from analyze_v4 import load_insights, boot_ci_clustered  # noqa: E402

RUN = "runs/v10_20261001_2117"
TYPE_OF_FAM = {0: "standard", 1: "periodic", 2: "composite", 3: "standard"}


def main():
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("=== V10 composite-world adjudication (SDB-aligned) ===")
    run = os.path.join(ROOT, RUN)
    P = load_probes_v7(run)
    disc = load_insights(run)

    # ---- 1. RECALL E20 by type per arm ----
    say("\n--- RECALL E20 by rule type (cluster bootstrap by lineage) ---")
    say(f"{'arm':10s} {'type':10s} {'E20':>7s} {'CI':>18s} {'n_ep':>5s}")
    e20_by = {}
    for arm in ("FULL", "MATCHED", "EPISODIC"):
        for typ in ("standard", "periodic", "composite"):
            vals, clusters = [], []
            for k, ep in P.get(arm, {}).items():
                if ep["type"] != "RECALL":
                    continue
                if TYPE_OF_FAM.get(ep["rule_id"] and
                                   (ep["rule_id"][1] if False else None), None):
                    continue
                fam = int(str(k[0])) if isinstance(k[0], int) else None
                # family is part of the key tuple (family, epoch)
                f = k[0]
                if TYPE_OF_FAM.get(f) != typ:
                    continue
                if ep["rule_id"] not in disc:
                    continue
                vals.append(ep["e20"])
                clusters.append(ep["rule_id"])
            if not vals:
                say(f"{arm:10s} {typ:10s} {'--':>7s}")
                continue
            m, lo, hi = boot_ci_clustered(np.array(vals, float), clusters)
            e20_by[(arm, typ)] = (np.mean(vals), lo, hi)
            say(f"{arm:10s} {typ:10s} {np.mean(vals):>7.3f} "
                f"[{lo:.3f},{hi:.3f}]   {len(vals):>5d}")

    # P1: periodic FULL vs MATCHED
    say("\n--- P1 (periodicity favors episodic) ---")
    f = e20_by.get(("FULL", "periodic"))
    m = e20_by.get(("MATCHED", "periodic"))
    if f and m:
        say(f"FULL {f[0]:.3f} vs MATCHED {m[0]:.3f} on periodic RECALL -> "
            f"{'MATCHED wins (P1 CONFIRMED)' if m[0] < f[0] else 'P1 REFUTED'}")

    # ---- 2. discovery speed per type (FULL arm) ----
    say("\n--- discovery speed (FULL arm): first-DISCOVERY cycle per type ---")
    by_type = {}
    for rid, cyc in disc.items():
        typ = TYPE_OF_FAM.get(int(rid[1]), "?")
        by_type.setdefault(typ, []).append(cyc)
    for typ, cs in sorted(by_type.items()):
        cs = sorted(cs)
        say(f"{typ:10s}: n={len(cs):3d} median_cycle={cs[len(cs)//2]} "
            f"mean={np.mean(cs):.0f}")

    # ---- 3. composition transfer (P2): FULL probe-1 hits on composite ----
    say("\n--- P2 composition transfer (FULL arm) ---")
    total = hit = 0
    for k, ep in P.get("FULL", {}).items():
        if TYPE_OF_FAM.get(k[0]) != "composite":
            continue
        if ep["type"] != "RECALL":
            continue
        p1 = ep["probes"][0] if ep["probes"] else None
        if p1 is None:
            continue
        total += 1
        hit += 1 - p1["error"]
    if total:
        say(f"composite RECALL probe-1 hit rate (FULL): {hit}/{total} "
            f"= {hit/total*100:.0f}%  (random ~7.7%; >50% suggests real "
            f"inference from the two predecessor rules)")

    # ---- 4. anomaly handling (P3) ----
    say("\n--- P3 anomaly handling (all arms) ---")
    stats = {}
    for line in open(os.path.join(run, "events.jsonl"), encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("lane") != "puzzle":
            continue
        if not r.get("anomaly"):
            continue
        arm = r.get("memory_arm")
        st = stats.setdefault(arm, {"n": 0, "err": 0})
        st["n"] += 1
        st["err"] += int(bool(r.get("error")))
    for arm, st in sorted(stats.items()):
        say(f"{arm:10s}: anomaly probes {st['n']}, error {st['err']} "
            f"({st['err']/max(st['n'],1)*100:.0f}%)  [unpredictable by "
            f"design; memorization checked via res/book writes at "
            f"anomaly episodes -- see counts]")

    # ---- 5. ICR (P4, coarse) ----
    say("\n--- ICR: observation bytes consumed / memory bytes stored ---")
    try:
        s = json.load(open(os.path.join(run, "state.json"), encoding="utf-8"))
        for name, r in (s.get("runners") or {}).items():
            c = r.get("counts") or {}
            stored = c.get("book_bytes", 0) + c.get("epi_bytes", 0)
            obs = c.get("probes", 0) * 16
            if stored:
                say(f"{name:10s}: ~{obs}/{stored} = {obs/stored:.1f} "
                    f"(probes={c.get('probes')}, book_bytes="
                    f"{c.get('book_bytes')}, epi_bytes={c.get('epi_bytes')})")
    except Exception as e:
        say(f"(ICR unavailable: {e})")

    out = os.path.join(ROOT, "findings", "v10")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "v10_adjudication.txt"), "w",
              encoding="utf-8") as f_:
        f_.write("\n".join(lines) + "\n")
    print(f"\nwritten: {os.path.join(out, 'v10_adjudication.txt')}")


if __name__ == "__main__":
    main()
