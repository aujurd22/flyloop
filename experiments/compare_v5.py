"""V5 adjudication: the condition law — does observation noise shrink the
compression's advantage? Compares run B (eps=0.25) against run A (eps=0,
the V4 early-stop run, same seed and schedule).

Usage:
    python experiments/compare_v5.py --run-a runs/v4_20260928_1636 \
        --run-b runs/v5_<ts> [--boot 10000]

Applies verdicts V5-P01..P05 to run B's ledger. Cluster bootstrap by rule
lineage; between-run contrasts via independent cluster resampling.
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


def dmf(arms, discovered_only=True, first=None):
    """Per-episode dE20(M−F) over discovered-rule RECALL episodes."""
    F, M = arms["FULL"], arms["MATCHED"]
    keys = sorted(set(F) & set(M))
    d, cl = [], []
    for k in keys:
        if F[k]["type"] != "RECALL":
            continue
        if discovered_only and (first is None or F[k]["rule_id"] not in first):
            continue
        d.append(M[k]["e20"] - F[k]["e20"])
        cl.append(F[k]["rule_id"])
    return np.array(d, dtype=float), cl


def contrast_between(dA, cA, dB, cB, n_boot=10000, seed=17):
    """CI for mean(dB) - mean(dA) with independent cluster resampling."""
    rng = np.random.default_rng(seed)
    if len(dA) == 0 or len(dB) == 0:
        return None, None, None
    dA, cA = np.asarray(dA, float), np.asarray(cA)
    dB, cB = np.asarray(dB, float), np.asarray(cB)
    uA, uB = np.unique(cA), np.unique(cB)
    bA = {u: dA[cA == u] for u in uA}
    bB = {u: dB[cB == u] for u in uB}
    means = []
    for _ in range(n_boot):
        kA = rng.choice(uA, size=len(uA), replace=True)
        kB = rng.choice(uB, size=len(uB), replace=True)
        mA = np.concatenate([bA[u] for u in kA]).mean()
        mB = np.concatenate([bB[u] for u in kB]).mean()
        means.append(float(mB - mA))
    return float(dB.mean() - dA.mean()), float(np.percentile(means, 2.5)), \
        float(np.percentile(means, 97.5))


def discovery_rate(run_dir, arms):
    first = load_insights(run_dir)
    F = arms["FULL"]
    born = sum(1 for ep in F.values() if ep["type"] in ("NEW", "VARIANT"))
    return len(first), born, (len(first) / born if born else None)


def e20_delta_between(armsA, armsB, arm, discovered_only, first):
    """E20 delta of `arm` between runs (B − A) on the same episode keys —
    noise's absolute damage to one arm."""
    A, B = armsA[arm], armsB[arm]
    keys = sorted(set(A) & set(B))
    d, cl = [], []
    for k in keys:
        if A[k]["type"] != "RECALL":
            continue
        if discovered_only and (first is None or A[k]["rule_id"] not in first):
            continue
        d.append(B[k]["e20"] - A[k]["e20"])
        cl.append(A[k]["rule_id"])
    return np.array(d, dtype=float), cl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-a", required=True, help="eps=0 baseline (V4 run)")
    ap.add_argument("--run-b", required=True, help="eps>0 run")
    ap.add_argument("--boot", type=int, default=10000)
    args = ap.parse_args()
    runA, runB = os.path.abspath(args.run_a), os.path.abspath(args.run_b)
    armsA = load_probes(runA)
    armsB = load_probes(runB)
    firstA = load_insights(runA)
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say(f"# V5 analysis — B({runB}) vs A({runA}) — "
        f"{time.strftime('%Y-%m-%d %H:%M:%S')}")

    # P01: replication at eps=0 (run A)
    dA, cA = dmf(armsA, True, firstA)
    mA, loA, hiA = boot_ci_clustered(dA, cA, args.boot)
    say(f"P1 eps=0 (run A) dE20(M-F) on discovered recurrences: n={len(dA)} "
        f"mean={mA if mA is None else round(mA, 3)} "
        f"CI=[{loA if loA is None else round(loA, 3)},"
        f"{hiA if hiA is None else round(hiA, 3)}]")

    # P02 headline: the contrast shrinks under noise
    dB, cB = dmf(armsB, True, load_insights(runB))
    mB, loB, hiB = boot_ci_clustered(dB, cB, args.boot)
    cC, loC, hiC = contrast_between(dA, cA, dB, cB, args.boot)
    say(f"P2 eps=0.25 (run B) dE20(M-F): n={len(dB)} "
        f"mean={mB if mB is None else round(mB, 3)} "
        f"CI=[{loB if loB is None else round(loB, 3)},"
        f"{hiB if hiB is None else round(hiB, 3)}]")
    say(f"P2 between-run contrast (noise effect on compression advantage): "
        f"{cC if cC is None else round(cC, 3)} CI=[{loC if loC is None else round(loC, 3)},"
        f"{hiC if hiC is None else round(hiC, 3)}]")

    # P03: discovery rate
    dA_r = discovery_rate(runA, armsA)
    dB_r = discovery_rate(runB, armsB)
    say(f"P3 discovery rate: A {dA_r[0]}/{dA_r[1]}={dA_r[2]:.3f} vs "
        f"B {dB_r[0]}/{dB_r[1]}={dB_r[2]:.3f}")

    # P04: book_test success collapse
    def bt_success(arms, first):
        F = arms["FULL"]
        keys = sorted(set(F))
        tries = hits = 0
        for k in keys:
            if F[k]["type"] != "RECALL" or F[k]["rule_id"] not in first:
                continue
            for p in F[k]["probes"]:
                if p["method"] == "book_test":
                    tries += 1
                    hits += 1 - p["error"]
        return hits, tries
    hA, tA = bt_success(armsA, firstA)
    hB, tB = bt_success(armsB, load_insights(runB))
    say(f"P4 book_test success: A {hA}/{tA}={hA/max(1,tA):.3f} vs "
        f"B {hB}/{tB}={hB/max(1,tB):.3f}")

    # P05: absolute noise damage per arm
    dmg = {}
    for arm in ("FULL", "MATCHED", "EPISODIC"):
        d, cl = e20_delta_between(armsA, armsB, arm, True, firstA)
        m, lo, hi = boot_ci_clustered(d, cl, args.boot)
        dmg[arm] = (m, lo, hi, len(d))
        say(f"P5 damage {arm}: dE20(B-A) n={len(d)} "
            f"mean={m if m is None else round(m, 3)} "
            f"CI=[{lo if lo is None else round(lo, 3)},"
            f"{hi if hi is None else round(hi, 3)}]")

    # ---- verdicts into run B's ledger ---------------------------------------
    def apply(pid, status, evidence):
        path = os.path.join(runB, "ledger.jsonl")
        rows = [json.loads(l) for l in open(path, encoding="utf-8")]
        for r in rows:
            if r.get("claim", "").startswith(f"V5-{pid}"):
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

    # the run-B ledger has no V5 rows unless the worker pre-registered them;
    # register on demand (worker predates V5 claims)
    lpath = os.path.join(runB, "ledger.jsonl")
    rows = [json.loads(l) for l in open(lpath, encoding="utf-8")]
    if not any(r.get("claim", "").startswith("V5-P") for r in rows):
        claims = {
            "V5-P01": "replication at eps=0: F-M advantage positive on discovered "
                      "recurrences in run A",
            "V5-P02": "condition law: dE20(M-F) larger at eps=0.25 than at eps=0 "
                      "(noise shrinks the compression advantage); between-run CI excludes 0",
            "V5-P03": "discovery rate drops under noise (C1 extraction degraded)",
            "V5-P04": "FULL book_test success collapses under noise (mechanism)",
            "V5-P05": "EPISODIC degrades slowest in absolute error under noise",
        }
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        for pid, claim in claims.items():
            rows.append({"id": f"FL-V5-{pid[-4:]}", "kind": "run", "claim": claim,
                         "status": "REGISTERED", "evidence": "", "ts": ts})
        with open(lpath, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    if mA is not None:
        apply("P01", "CONFIRMED" if (mA > 0 and loA > 0) else
              ("PARTIAL" if mA > 0 else "REFUTED"),
              f"run A n={len(dA)} dE20(M-F)={mA:.3f} CI=[{loA:.3f},{hiA:.3f}]")
    if cC is not None:
        apply("P02", "CONFIRMED" if (cC > 0 and loC > 0) else
              ("PARTIAL" if cC > 0 else "REFUTED"),
              f"A n={len(dA)}: {mA:.3f}; B n={len(dB)}: {mB:.3f}; "
              f"between-run contrast={cC:.3f} CI=[{loC:.3f},{hiC:.3f}]")
    if dA_r[2] is not None and dB_r[2] is not None:
        apply("P03", "CONFIRMED" if dB_r[2] < dA_r[2] else "REFUTED",
              f"A {dA_r[0]}/{dA_r[1]}={dA_r[2]:.3f} vs B {dB_r[0]}/{dB_r[1]}={dB_r[2]:.3f}")
    if tA and tB:
        rA, rB = hA / tA, hB / tB
        apply("P04", "CONFIRMED" if rB < rA - 0.1 else
              ("PARTIAL" if rB < rA else "REFUTED"),
              f"A {hA}/{tA}={rA:.3f} vs B {hB}/{tB}={rB:.3f}")
    vals = [v for v in dmg.values() if v[0] is not None]
    if len(vals) == 3:
        e_slowest = dmg["EPISODIC"][0] <= min(dmg["FULL"][0], dmg["MATCHED"][0])
        apply("P05", "CONFIRMED" if e_slowest else "REFUTED",
              "; ".join(f"{a}: {v[0]:.3f} CI[{v[1]:.3f},{v[2]:.3f}]"
                        for a, v in dmg.items()))

    with open(os.path.join(runB, "analysis_v5.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    say("verdicts applied to run B ledger; analysis written to analysis_v5.md")


if __name__ == "__main__":
    main()
