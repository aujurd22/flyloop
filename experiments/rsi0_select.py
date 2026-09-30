"""RSI-0 mechanical selector: given the lineage file, deterministically pick
the next generation's config + reason (no LLM, no discretion — the rules are
registered in RSI0_DESIGN.md §4).

Usage:
    python experiments/rsi0_select.py --lineage runs/rsi0_lineage.json
"""
import argparse
import json
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lineage", required=True)
    args = ap.parse_args()
    lin = json.load(open(args.lineage, encoding="utf-8"))
    gens = lin["generations"]
    struck = set(lin.get("struck_mutations", []))
    parent = gens[-1]

    # registered expected-improvement ranking (from §3 evidence); a mutation
    # already equal to the parent config is skipped; struck ones are skipped.
    # G3 note: M2 is now the ACCEPTED adaptive policy (g0 -> G3, -0.347), so
    # the tolerant↔exact flip is only available as a CONTROL (never counted
    # as improvement); the adaptive-vs-fixed axis is where the next gains lie.
    menu = [
        {"id": "M1", "kind": "BOOK_CAP", "from": 5, "to": 13,
         "reason": "no-candidate floor (15-19 probe-1 failures) is the largest "
                   "non-noise bucket; caused by recency eviction",
         "expected": -0.5, "struck": "G2 REJECTED on merit (no E20 improvement; "
         "floor is noise-bound not candidate-bound)"},
        {"id": "M2", "kind": "MATCH_MIN_FRAC", "from": 1.0, "to": 0.6,
         "reason": "tolerance rescued FULL under noise (g-1 -> g0: -1.27); "
                   "G3 refined this into the adaptive variant (accepted)",
         "expected": -1.27 if parent["config"].get("MATCH_MIN_FRAC") == 1.0 else 0.0},
        {"id": "M3", "kind": "NOISE_EPS", "from": 0.25, "to": 0.0,
         "reason": "CONTROL ONLY -- world shift, never counted as improvement",
         "expected": -2.0, "control": True},
        {"id": "M4", "kind": "READ_POLICY", "from": "fixed", "to": "adaptive",
         "reason": "G3 accepted: rolling flip estimate adjusts min_frac "
                   "(-0.347 vs parent); registered as a first-class mutation "
                   "axis for future generations",
         "expected": -0.35},
    ]
    cand = [m for m in menu
            if m["id"] not in struck
            and not m.get("struck")
            and parent["config"].get(m["kind"]) != m["to"]]
    # §3: control mutations (world shifts) are excluded from the improvement
    # ranking -- they change the task, so they can never be counted as the
    # system improving itself. They run only on explicit operator order.
    improvements = [m for m in cand if not m.get("control")]
    if improvements:
        improvements.sort(key=lambda m: m["expected"])
        nxt = improvements[0]
    else:
        cand.sort(key=lambda m: m["expected"])
        nxt = cand[0]
    out = {
        "next_generation": parent["gen"] + 1,
        "parent_gen": parent["gen"],
        "mutation": {"id": nxt["id"], "kind": nxt["kind"],
                     "from": parent["config"].get(nxt["kind"]), "to": nxt["to"]},
        "reason": nxt["reason"],
        "rule": "top expected-improvement mutation not yet equal to parent; "
                "accept iff FULL E20 < parent point beyond CI; else revert "
                "and strike",
    }
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
