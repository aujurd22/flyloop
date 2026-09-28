"""V3 endpoint adjudication: paired Full-vs-Episodic statistics from events.jsonl.

Applies verdicts V3-P01..P08 to the run ledger (the worker pre-registers and
deliberately does NOT adjudicate: paired bootstrap needs the full event log).

Usage:
    python experiments/analyze_v3.py --run-dir runs/v3_<ts> [--boot 10000]

Each RECALL episode is one statistical unit; FULL and EPI probes are paired by
(family, epoch, probe_idx). Report: effect size, 95% CI, raw counts (V3 §12).
"""
import argparse
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flyloop import config as C, world  # noqa: E402

PHASES = (("A", 0, 30000, 1), ("B", 30000, 60000, 2), ("C", 60000, None, 4))
REC_WINDOW = 20


def load_probes(run_dir):
    """{arm: {(fam, epoch): episode}} with probe lists in order."""
    out = {"FULL": {}, "EPI": {}}
    path = os.path.join(run_dir, "events.jsonl")
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("lane") != "puzzle":
                continue
            arm = r.get("memory_arm", "FULL")
            key = (r.get("family"), r.get("epoch"))
            ep = out[arm].setdefault(key, {"probes": [], "type": r.get("episode_type"),
                                           "gap": r.get("rule_age", 0),
                                           "rule_id": r.get("rule_id"),
                                           "start_c": None, "discoveries": []})
            ep["probes"].append({
                "idx": r.get("probe_idx", len(ep["probes"]) + 1),
                "c": r.get("c"), "error": int(bool(r.get("error"))),
                "method": r.get("method"),
                "stale": int(bool(r.get("stale_intrusion"))),
                "stale_cand": int(bool(r.get("stale_candidate_present"))),
                "discovery": int(bool(r.get("discovery"))),
                "rule_id": r.get("rule_id")})
            if ep["start_c"] is None:
                ep["start_c"] = r.get("c")
    for arm in out:
        for ep in out[arm].values():
            ep["probes"].sort(key=lambda p: p["idx"])
            first20 = ep["probes"][:REC_WINDOW]
            ep["e20"] = sum(p["error"] for p in first20)
            hit = next((p["idx"] for p in first20 if p["error"] == 0), REC_WINDOW + 1)
            ep["latency"] = hit
            ep["intrusions20"] = sum(p["stale"] for p in first20)
            ep["probes20"] = len(first20)
    return out


def paired(arms, etype, metric):
    """Per-episode paired deltas (EPI - FULL) for episodes of `etype` present
    in both arms. Returns (deltas, keys)."""
    F, E = arms["FULL"], arms["EPI"]
    keys = sorted(set(F) & set(E))
    d = []
    for k in keys:
        if F[k]["type"] != etype:
            continue
        d.append(E[k][metric] - F[k][metric])
    return np.array(d, dtype=float), keys


def boot_ci(deltas, n_boot=10000, seed=7):
    rng = np.random.default_rng(seed)
    if len(deltas) == 0:
        return None, None, None
    means = [float(np.mean(rng.choice(deltas, size=len(deltas), replace=True)))
             for _ in range(n_boot)]
    return float(np.mean(deltas)), float(np.percentile(means, 2.5)), \
        float(np.percentile(means, 97.5))


def perm_p(deltas, n=20000, seed=7):
    rng = np.random.default_rng(seed)
    if len(deltas) == 0:
        return None
    obs = abs(float(np.mean(deltas)))
    if obs == 0:
        return 1.0
    signs = rng.choice([-1.0, 1.0], size=(n, len(deltas)))
    null = np.abs((signs * deltas).mean(axis=1))
    return float((null >= obs - 1e-12).mean())


def episode_types(arms):
    F, E = arms["FULL"], arms["EPI"]
    for k in set(F) | set(E):
        t = (F.get(k) or E.get(k))["type"]
        yield k, t


def sir(arms):
    """Stale intrusion rate over the first 20 probes after every episode start."""
    out = {}
    for arm in ("FULL", "EPI"):
        num = den = 0
        for ep in arms[arm].values():
            num += ep["intrusions20"]
            den += ep["probes20"]
        out[arm] = num / den if den else None
        out[arm + "_raw"] = (num, den)
    return out


def useful_insight(arms, n_perm=1000, seed=11):
    """UIR: fraction of discovered rules whose recurrences show E20 benefit for
    FULL. Null = rule->recurrence assignment permuted across rules."""
    F, E = arms["FULL"], arms["EPI"]
    discovered = set()
    for ep in F.values():
        for p in ep["probes"]:
            if p["discovery"] and p["rule_id"]:
                discovered.add(p["rule_id"])
    recurrences = {}
    for k, ep in F.items():
        if ep["type"] == "RECALL" and ep["rule_id"] in discovered:
            recurrences.setdefault(ep["rule_id"], []).append(k)
    def benefit(rule, keys):
        f = np.mean([F[k]["e20"] for k in keys])
        e = np.mean([E[k]["e20"] for k in keys if k in E])
        return e > f
    rules = sorted(r for r in discovered if r in recurrences)
    if not rules:
        return None, None
    uir = float(np.mean([benefit(r, recurrences[r]) for r in rules]))
    all_rec = [recurrences[r] for r in rules]
    rng = np.random.default_rng(seed)
    pool = [k for k in F if F[k]["type"] == "RECALL"]
    null = []
    for _ in range(n_perm):
        draw = [pool[i] for i in rng.integers(0, len(pool), size=len(all_rec))]
        null.append(float(np.mean([benefit(rules[i], [draw[i]])
                                   for i in range(len(rules))])))
    return uir, float(np.percentile(null, 95))


def phase_of(cycle):
    for name, lo, hi, _ in PHASES:
        if hi is None or cycle < hi:
            if cycle >= lo:
                return name
    return "C"


def make_figures(arms, run_dir, ph, uir, null95):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    figdir = os.path.join(run_dir, "figs")
    os.makedirs(figdir, exist_ok=True)
    F, E = arms["FULL"], arms["EPI"]

    # 1) the cost matrix (V3 §16): episode type x arm
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    types = ["NEW", "VARIANT", "RECALL"]
    for ax, metric, title in ((axes[0], "e20", "errors in first 20 probes"),
                              (axes[1], "latency", "recovery latency (probe idx)")):
        vals = {arm: [np.mean([ep[metric] for ep in arms[arm].values()
                               if ep["type"] == t]) if any(
                   ep["type"] == t for ep in arms[arm].values()) else 0
                   for t in types] for arm in ("FULL", "EPI")}
        x = np.arange(len(types))
        ax.bar(x - 0.18, vals["FULL"], 0.36, label="FULL", color="#2b6cb0")
        ax.bar(x + 0.18, vals["EPI"], 0.36, label="EPI", color="#c05621")
        ax.set_xticks(x, types)
        ax.set_title(title)
        ax.legend()
    fig.suptitle("memory arms x episode type (learn / adapt / recover)")
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, "v3_cost_matrix.png"), dpi=130)
    plt.close(fig)

    # 2) memory gap -> recovery latency
    fig, ax = plt.subplots(figsize=(6, 4))
    for arm, color in (("FULL", "#2b6cb0"), ("EPI", "#c05621")):
        xs, ys = [], []
        for gap in sorted(C.RECALL_GAPS):
            lat = [ep["latency"] for ep in arms[arm].values()
                   if ep["type"] == "RECALL" and ep["gap"] == gap]
            if lat:
                xs.append(gap)
                ys.append(float(np.mean(lat)))
        ax.plot(xs, ys, marker="o", label=arm, color=color)
    ax.set_xlabel("recurrence gap (epochs)")
    ax.set_ylabel("mean recovery latency")
    ax.set_title("memory gap -> recovery latency")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, "v3_gap_latency.png"), dpi=130)
    plt.close(fig)

    # 3) noise pressure -> memory advantage
    fig, ax = plt.subplots(figsize=(6, 4))
    names = [n for n, _, _, _ in PHASES if ph.get(n, {}).get("dE") is not None]
    des = [ph[n]["dE"] for n in names]
    mults = [ph[n]["mult"] for n in names]
    ax.bar([f"{n}\n{m}x noise" for n, m in zip(names, mults)], des,
           color="#2f855a")
    ax.set_ylabel("dE20 (EPI - FULL) on RECALL")
    ax.set_title("noise pressure -> memory advantage")
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, "v3_noise_advantage.png"), dpi=130)
    plt.close(fig)

    # 4) discovery -> future predictive benefit (UIR vs null)
    if uir is not None:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist([uir], bins=[0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0],
                alpha=0.7, label="UIR", color="#2b6cb0")
        ax.axvline(null95, color="#c05621", linestyle="--",
                   label=f"permutation null 95th = {null95:.2f}")
        ax.axvline(uir, color="#2b6cb0", linestyle="-", label=f"UIR = {uir:.2f}")
        ax.set_xlabel("useful-insight rate")
        ax.set_title("discovery -> future predictive benefit")
        ax.legend()
        fig.tight_layout()
        fig.savefig(os.path.join(figdir, "v3_insight_benefit.png"), dpi=130)
        plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--boot", type=int, default=10000)
    args = ap.parse_args()
    run_dir = os.path.abspath(args.run_dir)
    arms = load_probes(run_dir)
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say(f"# V3 analysis — {run_dir} — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    # engineering gate
    st_path = os.path.join(run_dir, "state.json")
    run_status = "OK"
    if os.path.exists(st_path):
        with open(st_path, encoding="utf-8") as f:
            run_status = json.load(f).get("run_status", "OK")
    say(f"run_status: {run_status}")

    n_ep = {}
    for _, t in episode_types(arms):
        n_ep[t] = n_ep.get(t, 0) + 1
    say(f"episodes observed (paired log): {n_ep}")

    results = {}

    # ---- P1 / P2: RECALL primary endpoints
    dE, _ = paired(arms, "RECALL", "e20")
    dT, _ = paired(arms, "RECALL", "latency")
    mE, loE, hiE = boot_ci(dE, args.boot)
    pE = perm_p(dE)
    say(f"P1 dE20 (EPI-FULL) on RECALL: n={len(dE)} mean={mE:.3f} "
        f"CI=[{loE:.3f},{hiE:.3f}] perm_p={pE}")
    results["P1"] = (mE, loE, hiE, pE)
    mT, loT, hiT = boot_ci(dT, args.boot)
    pT = perm_p(dT)
    say(f"P2 dLatency (EPI-FULL) on RECALL: n={len(dT)} mean={mT:.3f} "
        f"CI=[{loT:.3f},{hiT:.3f}] perm_p={pT}")
    results["P2"] = (mT, loT, hiT, pT)

    # ---- P3: advantage across gaps
    gap_ok, gap_detail = True, []
    for gap in sorted(C.RECALL_GAPS):
        F, E = arms["FULL"], arms["EPI"]
        dd = [E[k]["e20"] - F[k]["e20"] for k in set(F) & set(E)
              if F[k]["type"] == "RECALL" and F[k]["gap"] == gap]
        if dd:
            gap_detail.append((gap, len(dd), float(np.mean(dd))))
            if np.mean(dd) <= 0:
                gap_ok = False
    say(f"P3 gap buckets (gap, n, dE): {gap_detail} -> all favor FULL: {gap_ok}")
    results["P3"] = gap_detail

    # ---- P4: VARIANT vs RECALL (NC1)
    dV, _ = paired(arms, "VARIANT", "e20")
    dR, _ = paired(arms, "RECALL", "e20")
    mv, mr = (float(np.mean(dV)) if len(dV) else None,
              float(np.mean(dR)) if len(dR) else None)
    say(f"P4 |dE| VARIANT={abs(mv):.3f} (n={len(dV)}) vs RECALL={abs(mr):.3f} "
        f"(n={len(dR)}) -> variant_smaller={abs(mv) < abs(mr)}")
    results["P4"] = (mv, len(dV), mr, len(dR))

    # ---- P5: stale intrusion
    s = sir(arms)
    ratio = (s["FULL"] / s["EPI"]) if s["EPI"] else None
    say(f"P5 SIR FULL={s['FULL']:.4f} {s['FULL_raw']} vs EPI={s['EPI']:.4f} "
        f"{s['EPI_raw']} -> ratio={ratio if ratio is not None else 'n/a'}")
    results["P5"] = (s, ratio)

    # ---- P6: useful insight rate
    uir, null95 = useful_insight(arms)
    say(f"P6 UIR={uir if uir is None else round(uir, 3)} vs permutation null "
        f"95th pct={null95 if null95 is None else round(null95, 3)}")
    results["P6"] = (uir, null95)

    # ---- P7: noise phases
    ph = {}
    for name, _, _, mult in PHASES:
        dd, _ = [], None
        F, E = arms["FULL"], arms["EPI"]
        dd = [E[k]["e20"] - F[k]["e20"] for k in set(F) & set(E)
              if F[k]["type"] == "RECALL" and F[k]["start_c"] is not None
              and phase_of(F[k]["start_c"]) == name]
        f_all = [p["error"] for ep in F.values() for p in ep["probes"][:REC_WINDOW]
                 if p["c"] is not None and phase_of(p["c"]) == name]
        e_all = [p["error"] for ep in E.values() for p in ep["probes"][:REC_WINDOW]
                 if p["c"] is not None and phase_of(p["c"]) == name]
        ph[name] = {"mult": mult, "n_recall": len(dd),
                    "dE": float(np.mean(dd)) if dd else None,
                    "full_first20_err": float(np.mean(f_all)) if f_all else None,
                    "epi_first20_err": float(np.mean(e_all)) if e_all else None}
    say(f"P7 phases: {ph}")
    results["P7"] = ph

    # ---- P8: fact lane regression (NC2)
    fact = {}
    for arm, tag in (("FULL", "F"), ("EPI", "E")):
        path = os.path.join(run_dir, "events.jsonl")
        vals = {"A": {1: [], 0: []}, "B": {1: [], 0: []}}
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("memory_arm", "FULL") != arm:
                    continue
                ph_name = phase_of(r.get("c", 0)) if r.get("c") else None
                if ph_name not in ("A", "C"):
                    continue
                for a in ("A", "B"):
                    if r.get(f"fact{a}_err") is not None:
                        vals[a][1 if ph_name == "C" else 0].append(r[f"fact{a}_err"])
        m = {a: {"phaseA": float(np.mean(vals[a][0])) if vals[a][0] else None,
                 "phaseC": float(np.mean(vals[a][1])) if vals[a][1] else None}
             for a in ("A", "B")}
        fact[arm] = m
    say(f"P8 fact lane: {fact}")
    results["P8"] = fact

    # ---- verdicts ------------------------------------------------------------
    def verdict(band):
        return "INVALID" if run_status.startswith("ENGINEERING_INVALID") else band

    def apply(pid, status, evidence):
        path = os.path.join(run_dir, "ledger.jsonl")
        rows = [json.loads(l) for l in open(path, encoding="utf-8")]
        for r in rows:
            if r.get("claim", "").startswith(f"V3-{pid}") and \
                    r.get("status") in ("REGISTERED", "INVALID"):
                r["status"] = status
                r["evidence"] = str(evidence)[:290]
                r["adjudicated_ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, path)

    if mE is not None:
        p1 = verdict("CONFIRMED" if (mE > 0 and loE > 0) else
                     ("PARTIAL" if mE > 0 else "REFUTED"))
        apply("P01", p1, f"n={len(dE)} dE20={mE:.3f} CI=[{loE:.3f},{hiE:.3f}] perm_p={pE}")
        p2 = verdict("CONFIRMED" if (mT > 0 and loT > 0) else
                     ("PARTIAL" if mT > 0 else "REFUTED"))
        apply("P02", p2, f"n={len(dT)} dLat={mT:.3f} CI=[{loT:.3f},{hiT:.3f}] perm_p={pT}")
        p3 = verdict("CONFIRMED" if gap_ok and all(n >= 10 for _, n, _ in gap_detail)
                     else ("PARTIAL" if gap_ok else "REFUTED"))
        apply("P03", p3, str(gap_detail))
        p4 = verdict("CONFIRMED" if (mv is not None and mr is not None and
                                     abs(mv) < abs(mr)) else "REFUTED")
        apply("P04", p4, f"variant |dE|={abs(mv):.3f} vs recall |dE|={abs(mr):.3f}")
        if ratio is not None:
            p5 = verdict("CONFIRMED" if ratio <= 1.5 else "REFUTED")
            apply("P05", p5, f"SIR F={s['FULL']:.4f} E={s['EPI']:.4f} ratio={ratio:.3f}")
        if uir is not None:
            p6 = verdict("CONFIRMED" if uir > null95 else
                         ("PARTIAL" if uir > 0.5 else "REFUTED"))
            apply("P06", p6, f"UIR={uir:.3f} null95={null95:.3f}")
        dC, dA = ph["C"]["dE"], ph["A"]["dE"]
        if dC is not None and dA is not None:
            p7 = verdict("CONFIRMED" if (dC - dA) > 0 else "REFUTED")
            apply("P07", p7, f"phase dE: A={dA:.3f} C={dC:.3f} (Full degrades slower "
                             f"if C-gap > A-gap)")
        ok8, ev8 = True, []
        for arm in ("FULL", "EPI"):
            for a in ("A", "B"):
                pa, pc = fact[arm][a]["phaseA"], fact[arm][a]["phaseC"]
                if pa is None or pc is None:
                    continue
                ok = pc <= max(2 * pa, 0.20) if pa > 0 else pc <= 0.20
                ok8 &= ok
                ev8.append(f"{arm}-{a}: A={pa:.3f} C={pc:.3f}")
        p8 = verdict("CONFIRMED" if ok8 else "REFUTED")
        apply("P08", p8, "; ".join(ev8))

    with open(os.path.join(run_dir, "analysis_v3.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    try:
        make_figures(arms, run_dir, ph, uir, null95)
        say("figures written to figs/")
    except Exception as e:
        say(f"figures failed: {e}")
    say("verdicts applied to ledger.jsonl; analysis written to analysis_v3.md")


if __name__ == "__main__":
    main()
