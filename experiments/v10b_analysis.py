"""V10b E3 + ICR + E2: the Arena profile of flyloop discoveries, the ICR
table, and the Polanyi gap (stated vs operative registry rules).

E3: P-DISCOVERY profiled flymemory consolidations C 1.10 / N 0.13 / T 0.00
("not insight"). The same profile for flyloop rule discoveries (SDB bit
convention) -- registered expectation: INSIGHT-class (C>>1, N=1, T>0).
E2: stated (a,b) at discovery vs operative refit from confirmed pairs
(W9C res entries) -- P156's verbalization gap, mechanized.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from compare_v7 import load_probes_v7  # noqa: E402
from analyze_v4 import load_insights  # noqa: E402

P = 13
BITS_PER_CHAR = 4.7  # SDB convention


def bits(obj):
    s = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return len(s.encode("utf-8")) * BITS_PER_CHAR


def arena_profile():
    """E3: C/V/T/N for every first-DISCOVERY in the V10 FULL arm."""
    run = os.path.join(ROOT, "runs", "v10_20261001_2117")
    P_all = load_probes_v7(run)
    full = P_all.get("FULL", {})
    epi = P_all.get("EPISODIC", {})
    disc = load_insights(run)
    cs, ts = [], []
    for rid, dcyc in sorted(disc.items()):
        fam = int(rid[1])
        # pre-discovery observations: probes of this rid before/at discovery
        obs = []
        for k, ep in full.items():
            if ep["rule_id"] != rid:
                continue
            for p in ep["probes"]:
                if p["idx"] is not None:
                    obs.append([p["c"], p.get("error", 0)])
        if not obs:
            continue
        rule_bits = bits({"a": 1, "b": 1, "rid": rid})
        c_ratio = bits(obs[:24]) / max(rule_bits, 1.0)
        cs.append(c_ratio)
        # T: RECALL E20 delta vs EPISODIC on shared episodes
        mine, theirs = [], []
        for k, ep in full.items():
            if ep["rule_id"] != rid or ep["type"] != "RECALL":
                continue
            if k in epi and epi[k]["type"] == "RECALL":
                mine.append(ep["e20"])
                theirs.append(epi[k]["e20"])
        if mine:
            ts.append(np.mean(theirs) - np.mean(mine))
    say_c = (f"C (mdl_ratio, obs24/rule-entry): median {np.median(cs):.2f} "
             f"mean {np.mean(cs):.2f} n={len(cs)}")
    say_t = (f"T (RECALL E20 improvement vs EPISODIC): mean "
             f"{np.mean(ts):+.2f} n={len(ts)}"
             + (f" ({sum(1 for t in ts if t > 0)}/{len(ts)} rules positive)"
                if ts else ""))
    return say_c, say_t


def icr_table():
    """ICR per arm, SDB bit convention: bits(observations)/bits(stored)."""
    s = json.load(open(os.path.join(ROOT, "runs", "v10_20261001_2117",
                                    "state.json"), encoding="utf-8"))
    out = []
    n_probes = 2709  # per arm (STATUS), identical across arms
    obs_bits = bits({"pairs": [["x", "y"]] * n_probes})
    for name, r in (s.get("runners") or {}).items():
        c = r.get("counts") or {}
        stored = c.get("book_bytes", 0) + c.get("epireg_bytes", 0) + \
            c.get("pad_bytes", 0)
        out.append((name, obs_bits / max(stored * BITS_PER_CHAR, 1.0),
                    stored))
    return out


def polanyi_gap():
    """E2: stated vs operative registry rules in the W9D wave world.
    Operative = exhaustive refit from the rule's confirmed pairs (stored
    as residual entries in mem_FULL-RES's pickle -- read offline)."""
    import pickle
    pkl = os.path.join(ROOT, "runs", "w9c_20261001_2059", "mem_FULL.pkl")
    if not os.path.exists(pkl):
        return "(mem pickle missing)"
    with open(pkl, "rb") as f:
        db = pickle.load(f)
    entries = []
    try:
        items = db.items() if hasattr(db, "items") else []
    except Exception:
        items = []
    import re
    P_RES = re.compile(r"res=(\d+),(\d+),(\d+),([\d,]*)::((?:\(\d+,\d+\))*)")
    P_PT = re.compile(r"\((\d+),(\d+)\)")
    P_RULE = re.compile(r"[红蓝金银]r(\d+)=(\d+)x(\d+)")
    stated, pairs_by_rid = {}, {}
    for _, v in items:
        t = v if isinstance(v, str) else getattr(v, "text", "") or ""
        if "残差" in t:
            m = P_RES.search(t)
            mr = P_RULE.search(t)
            if m and mr:
                rid = f"f0r{mr.group(1)}"
                xs = [x for x in m.group(4).split(",") if x != ""]
                pts = P_PT.findall(m.group(5))
                pairs_by_rid[rid] = [(int(x), int(r)) for x, (_, r) in
                                     zip(xs, pts)]
        elif "规律" in t:
            mr = P_RULE.search(t)
            if mr:
                stated[f"f0r{mr.group(1)}"] = (int(mr.group(2)),
                                               int(mr.group(3)))
    gap = same = 0
    details = []
    for rid, prs in pairs_by_rid.items():
        st = stated.get(rid)
        if not st or len(prs) < 3:
            continue
        best_e, best = None, None
        for aa in range(P):
            for bb in range(P):
                e = sum(min((y - (aa * x + bb)) % P, (aa * x + bb - y) % P)
                        for x, y in prs)
                if best_e is None or e < best_e:
                    best_e, best = e, (aa, bb)
        op = best
        tol_ok = min((st[0] - op[0]) % P, (op[0] - st[0]) % P) <= 1 and \
            min((st[1] - op[1]) % P, (op[1] - st[1]) % P) <= 1
        if tol_ok:
            same += 1
        else:
            gap += 1
            details.append((rid, st, op))
    return (f"registry entries with >=3 confirmed pairs: {gap + same}; "
            f"stated==operative(+-1): {same}; POLANYI GAP (stated wrong): "
            f"{gap} {details[:6]}")


def main():
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("=== V10b E3/E2/ICR analysis (existing runs) ===")
    c_line, t_line = arena_profile()
    say("\n--- E3: Arena profile of flyloop discoveries (V10 FULL) ---")
    say(c_line)
    say("V (verification) = 1 by construction (consec-3 gate)")
    say("N (novelty)     = 1 by construction (first DISCOVERY, fresh rid)")
    say(t_line)
    say("flymemory consolidation baseline: C 1.10 / N 0.13 / T 0.00 "
        "(P-DISCOVERY: 'not insight')")
    say()
    say("--- ICR (SDB bit convention) ---")
    for name, ratio, stored in icr_table():
        say(f"{name:10s}: ICR ~{ratio:.1f} (stored {stored} B)")
    say()
    say("--- E2: Polanyi gap (W9C FULL-RES store, stated vs operative) ---")
    say(str(polanyi_gap()))
    out = os.path.join(ROOT, "findings", "v10b_e2e3.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main()
