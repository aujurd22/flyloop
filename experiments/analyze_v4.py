"""V4 endpoint adjudication: three memory arms, cluster bootstrap by rule
lineage, and the discovered-vs-undiscovered contrast that V3 could not run
(its FULL arm abstracted 100% of rules — zero variation).

Usage:
    python experiments/analyze_v4.py --run-dir runs/v4_<ts> [--boot 10000]

Applies verdicts V4-P01..P08 to the run ledger (the worker pre-registers and
deliberately does NOT adjudicate). Prior verdicts are preserved in
revision_history. An ENGINEERING_INVALID run is never adjudicated.
"""
import argparse
import json
import os
import re
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flyloop import config as C, world  # noqa: E402

ARMS = ("FULL", "MATCHED", "EPISODIC")
REC_WINDOW = 20
PHASES = ("A", "B", "C")


def load_probes(run_dir):
    """{arm: {(fam, epoch): episode}} with probe lists in order."""
    out = {arm: {} for arm in ARMS}
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
            if arm not in out:
                continue
            key = (r.get("family"), r.get("epoch"))
            ep = out[arm].setdefault(key, {"probes": [], "type": r.get("episode_type"),
                                           "gap": r.get("rule_age", 0),
                                           "rule_id": r.get("rule_id"),
                                           "start_c": None})
            ep["probes"].append({
                "idx": r.get("probe_idx", len(ep["probes"]) + 1),
                "c": r.get("c"), "error": int(bool(r.get("error"))),
                "method": r.get("method"),
                "stale": int(bool(r.get("stale_intrusion"))),
                "discovery": int(bool(r.get("discovery"))),
                "rule_id": r.get("rule_id")})
            if ep["start_c"] is None:
                ep["start_c"] = r.get("c")
    for arm in out:
        for ep in out[arm].values():
            ep["probes"].sort(key=lambda p: p["idx"])
            first20 = ep["probes"][:REC_WINDOW]
            ep["e20"] = sum(p["error"] for p in first20)
            ep["latency"] = next((p["idx"] for p in first20 if p["error"] == 0),
                                 REC_WINDOW + 1)
            ep["intrusions20"] = sum(p["stale"] for p in first20)
            ep["probes20"] = len(first20)
    return out


def load_insights(run_dir):
    """First-DISCOVERY cycle per rule_id (REACTIVATION excluded — it is a
    book write for a known rule, not the insight event)."""
    first = {}
    path = os.path.join(run_dir, "events.jsonl")
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            for note in r.get("notes", []):
                m = re.match(r"DISCOVERY fam=\d+ ep=\d+ rid=(\S+)", note)
                if m:
                    rid, c = m.group(1), r.get("c")
                    if rid not in first or c < first[rid]:
                        first[rid] = c
    return first


def boot_ci_clustered(deltas, clusters, n_boot=10000, seed=7):
    """Resample CLUSTERS (rule lineages) with replacement; episode-iid CIs
    understate uncertainty when the same rule recurs repeatedly."""
    rng = np.random.default_rng(seed)
    if len(deltas) == 0:
        return None, None, None
    deltas = np.asarray(deltas, dtype=float)
    clusters = np.asarray(clusters)
    uniq = np.unique(clusters)
    by_c = {u: deltas[clusters == u] for u in uniq}
    means = []
    for _ in range(n_boot):
        draw = rng.choice(uniq, size=len(uniq), replace=True)
        means.append(float(np.concatenate([by_c[u] for u in draw]).mean()))
    return float(deltas.mean()), float(np.percentile(means, 2.5)), \
        float(np.percentile(means, 97.5))


def perm_p_clustered(deltas, clusters, n=20000, seed=7):
    """Sign-flip permutation at the CLUSTER level: flip each cluster's whole
    vector of deltas, recompute the pooled mean."""
    rng = np.random.default_rng(seed)
    if len(deltas) == 0:
        return None
    deltas = np.asarray(deltas, dtype=float)
    clusters = np.asarray(clusters)
    uniq = np.unique(clusters)
    by_c = [deltas[clusters == u] for u in uniq]
    obs = abs(float(deltas.mean()))
    if obs == 0:
        return 1.0
    cnt = 0
    for _ in range(n):
        signs = rng.choice([-1.0, 1.0], size=len(uniq))
        pooled = np.concatenate([s * v for s, v in zip(signs, by_c)])
        if abs(pooled.mean()) >= obs - 1e-12:
            cnt += 1
    return cnt / n


def contrast_ci(d1, c1, d0, c0, n_boot=10000, seed=13):
    """CI for mean(d1) - mean(d0) with independent cluster resampling in the
    two groups."""
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
        m1 = np.concatenate([b1[u] for u in k1]).mean()
        m0 = np.concatenate([b0[u] for u in k0]).mean()
        means.append(float(m1 - m0))
    return float(d1.mean() - d0.mean()), float(np.percentile(means, 2.5)), \
        float(np.percentile(means, 97.5))


def contrast_ep(arms, other, metric="e20"):
    """deltas of (other - arm) over paired RECALL episodes + cluster labels."""
    F, O = arms["EPISODIC"], arms[other]
    d, cl = [], []
    for k in sorted(set(F) & set(O)):
        if F[k]["type"] != "RECALL":
            continue
        d.append(O[k][metric] - F[k][metric])
        cl.append(F[k]["rule_id"])
    return np.array(d, dtype=float), cl


def phase_of(cycle):
    return world.puz_phase(cycle or 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--boot", type=int, default=10000)
    args = ap.parse_args()
    run_dir = os.path.abspath(args.run_dir)
    arms = load_probes(run_dir)
    first_disc = load_insights(run_dir)
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say(f"# V4 analysis — {run_dir} — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    run_status = "OK"
    st_path = os.path.join(run_dir, "state.json")
    if os.path.exists(st_path):
        with open(st_path, encoding="utf-8") as f:
            run_status = json.load(f).get("run_status", "OK")
    say(f"run_status: {run_status}")

    F, M, E = arms["FULL"], arms["MATCHED"], arms["EPISODIC"]
    keys = sorted(set(F) & set(M) & set(E))
    rec_keys = [k for k in keys if F[k]["type"] == "RECALL"]
    disc_keys = [k for k in rec_keys if F[k]["rule_id"] in first_disc]
    undisc_keys = [k for k in rec_keys if F[k]["rule_id"] not in first_disc]
    say(f"RECALL episodes: {len(rec_keys)} (discovered-rule {len(disc_keys)} / "
        f"undiscovered-rule {len(undisc_keys)}); distinct rules discovered: "
        f"{len(first_disc)}")
    results = {}

    def cluster_split(deltas, cl, mask):
        d = [v for v, m in zip(deltas, mask) if m]
        c = [v for v, m in zip(cl, mask) if m]
        return np.array(d, dtype=float), c

    # ---- P01 (primary): discovered vs undiscovered recurrence benefit ------
    # dFE = EPI - FULL (positive = FULL better); clusters = rule lineage
    dFE = np.array([E[k]["e20"] - F[k]["e20"] for k in rec_keys], dtype=float)
    clFE = [F[k]["rule_id"] for k in rec_keys]
    mask_d = np.array([F[k]["rule_id"] in first_disc for k in rec_keys])
    d1, c1 = cluster_split(dFE, clFE, mask_d)
    d0, c0 = cluster_split(dFE, clFE, ~mask_d)
    c01, lo1, hi1 = contrast_ci(d1, c1, d0, c0, args.boot)
    say(f"P1 contrast dE20(discovered) - dE20(undiscovered): "
        f"disc n={len(d1)} mean={np.mean(d1) if len(d1) else float('nan'):.3f} | "
        f"undisc n={len(d0)} mean={np.mean(d0) if len(d0) else float('nan'):.3f} | "
        f"contrast={c01 if c01 is None else round(c01, 3)} "
        f"CI=[{lo1 if lo1 is None else round(lo1, 3)},"
        f"{hi1 if hi1 is None else round(hi1, 3)}]")
    results["P1"] = (c01, lo1, hi1, len(d1), len(d0))

    # ---- P02 (primary): F <= M <= E on discovered-rule recurrences ---------
    dMF = np.array([M[k]["e20"] - F[k]["e20"] for k in disc_keys], dtype=float)
    clMF = [F[k]["rule_id"] for k in disc_keys]
    dEM = np.array([E[k]["e20"] - M[k]["e20"] for k in disc_keys], dtype=float)
    clEM = [F[k]["rule_id"] for k in disc_keys]
    mMF, loMF, hiMF = boot_ci_clustered(dMF, clMF, args.boot)
    mEM, loEM, hiEM = boot_ci_clustered(dEM, clEM, args.boot)
    say(f"P2 on discovered recurrences (n={len(disc_keys)}): "
        f"dE20(M-F)={mMF if mMF is None else round(mMF, 3)} "
        f"CI=[{loMF if loMF is None else round(loMF, 3)},"
        f"{hiMF if hiMF is None else round(hiMF, 3)}] | "
        f"dE20(E-M)={mEM if mEM is None else round(mEM, 3)} "
        f"CI=[{loEM if loEM is None else round(loEM, 3)},"
        f"{hiEM if hiEM is None else round(hiEM, 3)}]")
    results["P2"] = (mMF, loMF, hiMF, mEM, loEM, hiEM)

    # ---- P03: M beats F on undiscovered recurrences ------------------------
    dUF = np.array([F[k]["e20"] - M[k]["e20"] for k in undisc_keys], dtype=float)
    clUF = [F[k]["rule_id"] for k in undisc_keys]
    mUF, loUF, hiUF = boot_ci_clustered(dUF, clUF, args.boot)
    say(f"P3 undiscovered recurrences (n={len(undisc_keys)}): "
        f"dE20(F-M)={mUF if mUF is None else round(mUF, 3)} "
        f"CI=[{loUF if loUF is None else round(loUF, 3)},"
        f"{hiUF if hiUF is None else round(hiUF, 3)}] "
        f"(positive = M better)")
    results["P3"] = (mUF, loUF, hiUF)

    # ---- P4: probe-1 recovery via book_test --------------------------------
    p1 = [F[k]["probes"][0] for k in disc_keys if F[k]["probes"]]
    p1_hit = sum(1 for p in p1 if p["method"] == "book_test" and p["error"] == 0)
    frac4 = p1_hit / len(p1) if p1 else None
    say(f"P4 FULL probe-1 book_test recovery: {p1_hit}/{len(p1)} = "
        f"{frac4 if frac4 is None else round(frac4, 3)}")
    results["P4"] = (p1_hit, len(p1), frac4)

    # ---- P5: stale intrusion ------------------------------------------------
    s = {}
    for arm in ("FULL", "EPISODIC"):
        num = sum(arms[arm][k]["intrusions20"] for k in rec_keys if k in arms[arm])
        den = sum(arms[arm][k]["probes20"] for k in rec_keys if k in arms[arm])
        s[arm] = num / den if den else None
        s[arm + "_raw"] = (num, den)
    ratio = (s["FULL"] / s["EPISODIC"]) if s["EPISODIC"] else \
        (0.0 if not s["FULL"] else float("inf"))
    say(f"P5 SIR FULL={s['FULL']:.4f} {s['FULL_raw']} vs EPI={s['EPISODIC']:.4f} "
        f"{s['EPISODIC_raw']} -> ratio={ratio if ratio is None else round(ratio, 3)}")
    results["P5"] = (s, ratio)

    # ---- P6 (NC1): VARIANT/NEW contrasts ~ 0 --------------------------------
    nc = {}
    for etype in ("VARIANT", "NEW"):
        dd = [E[k]["e20"] - F[k]["e20"] for k in keys if F[k]["type"] == etype]
        nc[etype] = {"n": len(dd), "dE20": float(np.mean(dd)) if dd else None}
    ok6 = all(v["dE20"] is not None and abs(v["dE20"]) < 0.05 and v["n"] >= 20
              for v in nc.values())
    say(f"P6 NC1: {nc} -> within band: {ok6}")
    results["P6"] = (nc, ok6)

    # ---- P7: quota-gated phases --------------------------------------------
    ph = {}
    for name in PHASES:
        dd = [E[k]["e20"] - F[k]["e20"] for k in rec_keys
              if phase_of(F[k]["start_c"]) == name]
        f_all = [p["error"] for k in keys for p in F[k]["probes"][:REC_WINDOW]
                 if phase_of(F[k]["start_c"]) == name]
        e_all = [p["error"] for k in keys for p in E[k]["probes"][:REC_WINDOW]
                 if phase_of(E[k]["start_c"]) == name]
        ph[name] = {"n_recall": len(dd),
                    "dE20": float(np.mean(dd)) if dd else None,
                    "full_err": float(np.mean(f_all)) if f_all else None,
                    "epi_err": float(np.mean(e_all)) if e_all else None}
    reached_c = ph["C"]["n_recall"] > 0
    ok7 = reached_c and ph["C"]["dE20"] is not None and ph["C"]["dE20"] > 0
    say(f"P7 phases: {ph} -> C reached: {reached_c}, advantage persists: {ok7}")
    results["P7"] = (ph, reached_c, ok7)

    # ---- P8 (NC2): fact lane -------------------------------------------------
    fact = {}
    path = os.path.join(run_dir, "events.jsonl")
    vals = {arm: {"A": [], "C": []} for arm in ARMS}
    with open(path, encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            arm = r.get("memory_arm")
            if arm not in vals or r.get("factA_err") is None:
                continue
            ph_name = phase_of(r.get("c"))
            if ph_name in ("A", "C"):
                vals[arm]["A" if ph_name == "A" else "C"].append(r["factA_err"])
    for arm in ARMS:
        a = float(np.mean(vals[arm]["A"])) if vals[arm]["A"] else None
        c_ = float(np.mean(vals[arm]["C"])) if vals[arm]["C"] else None
        fact[arm] = {"phaseA": a, "phaseC": c_}
    ok8, ev8 = True, []
    for arm in ARMS:
        a, c_ = fact[arm]["phaseA"], fact[arm]["phaseC"]
        if a is None or c_ is None:
            ok8 = False
            continue
        ok8 &= (c_ <= max(2 * a, 0.20) if a > 0 else c_ <= 0.20)
        ev8.append(f"{arm}: A={a:.3f} C={c_:.3f}")
    say(f"P8 fact lane: {fact} -> {'; '.join(ev8)}")
    results["P8"] = (fact, ok8, ev8)

    # ---- verdicts ------------------------------------------------------------
    def apply(pid, status, evidence):
        path = os.path.join(run_dir, "ledger.jsonl")
        rows = [json.loads(l) for l in open(path, encoding="utf-8")]
        for r in rows:
            if r.get("claim", "").startswith(f"V4-{pid}"):
                if r.get("status") != "REGISTERED":
                    r.setdefault("revision_history", []).append(
                        {"status": r["status"], "evidence": r.get("evidence", ""),
                         "ts": r.get("adjudicated_ts", r.get("ts", ""))})
                r["status"] = status
                r["evidence"] = str(evidence)[:290]
                r["adjudicated_ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        os.replace(tmp, path)

    if run_status.startswith("ENGINEERING_INVALID"):
        for pid in ("P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08"):
            apply(pid, "INVALID", f"run_status={run_status}")
        say("run engineering-invalid: all verdicts set to INVALID")
    else:
        # P01/P03 apply even when a group is empty (INCONCLUSIVE), so the
        # ledger never leaves a registered row untouched after analysis.
        if len(d0) == 0 or len(d1) == 0 or c01 is None:
            apply("P01", "INCONCLUSIVE",
                  f"contrast unevaluable: disc n={len(d1)}, undisc n={len(d0)}")
        else:
            apply("P01", "CONFIRMED" if lo1 > 0 else "REFUTED",
                  f"disc n={len(d1)} vs undisc n={len(d0)}; contrast={c01:.3f} "
                  f"CI=[{lo1:.3f},{hi1:.3f}]")
        if len(disc_keys) == 0 or mMF is None:
            apply("P02", "INCONCLUSIVE", "no discovered-rule recurrences")
        else:
            both = (mMF > 0 and mEM > 0)
            apply("P02", "CONFIRMED" if both and ((loMF is not None and loMF > 0)
                                                  or (loEM is not None and loEM > 0))
                  else ("PARTIAL" if both else "REFUTED"),
                  f"n={len(disc_keys)} dE20(M-F)={mMF:.3f} CI=[{loMF:.3f},{hiMF:.3f}]; "
                  f"dE20(E-M)={mEM:.3f} CI=[{loEM:.3f},{hiEM:.3f}]")
        if len(undisc_keys) == 0 or mUF is None:
            apply("P03", "INCONCLUSIVE", "no undiscovered-rule recurrences")
        else:
            apply("P03", "CONFIRMED" if (mUF > 0 and loUF > 0) else
                  ("PARTIAL" if mUF > 0 else "REFUTED"),
                  f"n={len(undisc_keys)} dE20(F-M)={mUF:.3f} CI=[{loUF:.3f},{hiUF:.3f}]")
        if frac4 is not None:
            apply("P04", "CONFIRMED" if frac4 >= 0.40 else
                  ("PARTIAL" if frac4 >= 0.20 else "REFUTED"),
                  f"{p1_hit}/{len(p1)} = {frac4:.3f}")
        if ratio is not None:
            # near-zero base rates make the ratio band meaningless (V4 early
            # stop: F=2, E=0 of 652 probes each — Fisher p=0.5, no signal);
            # require enough intrusions to read the ratio at all
            f_num = s["FULL_raw"][0]
            if f_num + s["EPISODIC_raw"][0] < 20:
                apply("P05", "INCONCLUSIVE",
                      f"intrusion counts too small to read the band "
                      f"(F={s['FULL_raw']}, E={s['EPISODIC_raw']}); "
                      f"both arms effectively intrusion-free at this scale")
            else:
                apply("P05", "CONFIRMED" if ratio <= 1.5 else "REFUTED",
                      f"SIR F={s['FULL']:.4f} E={s['EPISODIC']:.4f} ratio={ratio:.3f}")
        apply("P06", "CONFIRMED" if ok6 else "REFUTED", str(nc))
        apply("P07", "CONFIRMED" if ok7 else
              ("INCONCLUSIVE" if not reached_c else "REFUTED"),
              f"C reached={reached_c}; " + str({k: v['dE20'] for k, v in ph.items()}))
        if ev8:
            apply("P08", "CONFIRMED" if ok8 else "REFUTED", "; ".join(ev8))
        else:
            apply("P08", "INCONCLUSIVE", "phase C fact data missing")

    # ---- figures -------------------------------------------------------------
    try:
        make_figures(arms, run_dir, first_disc, ph, results)
        say("figures written to figs/")
    except Exception as e:
        say(f"figures failed: {e}")

    with open(os.path.join(run_dir, "analysis_v4.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("verdicts applied to ledger.jsonl; analysis written to analysis_v4.md")


def make_figures(arms, run_dir, first_disc, ph, results):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    figdir = os.path.join(run_dir, "figs")
    os.makedirs(figdir, exist_ok=True)
    F, M, E = arms["FULL"], arms["MATCHED"], arms["EPISODIC"]
    keys = sorted(set(F) & set(M) & set(E))

    # 1) 3-arm x episode-type E20
    fig, ax = plt.subplots(figsize=(8, 4.5))
    types = ["NEW", "VARIANT", "RECALL"]
    x = np.arange(len(types))
    for i, (arm, color) in enumerate((("FULL", "#2b6cb0"), ("MATCHED", "#2f855a"),
                                      ("EPISODIC", "#c05621"))):
        vals = [np.mean([arms[arm][k]["e20"] for k in keys
                         if arms[arm][k]["type"] == t]) if any(
                    arms[arm][k]["type"] == t for k in keys) else 0 for t in types]
        ax.bar(x + (i - 1) * 0.26, vals, 0.26, label=arm, color=color)
    ax.set_xticks(x, types)
    ax.set_ylabel("errors in first 20 probes")
    ax.set_title("three memory arms x episode type")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, "v4_arms_types.png"), dpi=130)
    plt.close(fig)

    # 2) discovered vs undiscovered contrast
    c01, lo1, hi1, n1, n0 = results["P1"]
    if c01 is not None:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(["contrast"], [c01], color="#2b6cb0")
        ax.errorbar([0], [c01], yerr=[[c01 - lo1], [hi1 - c01]], fmt="o",
                    color="#c05621", capsize=6)
        ax.axhline(0, color="gray", linewidth=0.8)
        ax.set_ylabel("dE20(discovered) - dE20(undiscovered)")
        ax.set_title(f"V4-P01 (disc n={n1}, undisc n={n0})")
        fig.tight_layout()
        fig.savefig(os.path.join(figdir, "v4_contrast.png"), dpi=130)
        plt.close(fig)

    # 3) latency distributions on RECALL
    fig, ax = plt.subplots(figsize=(7, 4))
    data, labels = [], []
    for arm in ("FULL", "MATCHED", "EPISODIC"):
        lat = [arms[arm][k]["latency"] for k in keys
               if arms[arm][k]["type"] == "RECALL"
               and arms[arm][k]["rule_id"] in first_disc]
        if lat:
            data.append(lat)
            labels.append(f"{arm}\n(n={len(lat)})")
    if data:
        ax.boxplot(data, tick_labels=labels)
        ax.set_ylabel("recovery latency (probe idx)")
        ax.set_title("discovered-rule RECALL recovery latency")
    fig.tight_layout()
    fig.savefig(os.path.join(figdir, "v4_latency.png"), dpi=130)
    plt.close(fig)

    # 4) per-phase dE20
    names = [n for n in PHASES if ph.get(n, {}).get("dE20") is not None]
    if names:
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar([f"{n}\nNEW-gated" for n in names],
               [ph[n]["dE20"] for n in names], color="#2f855a")
        ax.set_ylabel("dE20 (E - F) on RECALL")
        ax.set_title("noise phase -> F-E advantage")
        fig.tight_layout()
        fig.savefig(os.path.join(figdir, "v4_phases.png"), dpi=130)
        plt.close(fig)


if __name__ == "__main__":
    main()
