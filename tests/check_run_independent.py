"""Run-independence checker (G4 incident): verify that a run claiming to be
a replication is NOT a bit-identical prefix of its parent.

The flyloop world is a pure function of (schedule seed, run seed). Before the
RUN_SEED split, same-config re-runs were bit-prefixes of their parents and
"replication confirmed" claims were vacuous. This checker makes that failure
mechanical: it compares the puzzle-lane event tuples of two runs and exits 1
if the common prefix is identical beyond --max-events.

Usage:
    python tests/check_run_independent.py runs/parent runs/child [--max-events 2000]
Exit codes: 0 = independent (or diverged within budget), 1 = IDENTICAL PREFIX.
"""
import argparse
import json
import sys


def puzzle_tuples(run_dir, max_events):
    out = []
    with open(run_dir + "/events.jsonl", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("lane") != "puzzle":
                continue
            out.append((r.get("c"), r.get("memory_arm"), r.get("family"),
                        r.get("epoch"), r.get("probe_idx"), r.get("error"),
                        r.get("method")))
            if len(out) >= max_events:
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parent")
    ap.add_argument("child")
    ap.add_argument("--max-events", type=int, default=2000)
    args = ap.parse_args()
    a = puzzle_tuples(args.parent, args.max_events)
    b = puzzle_tuples(args.child, args.max_events)
    n = min(len(a), len(b))
    if n == 0:
        print(f"INDETERMINATE: no common puzzle events "
              f"(parent={len(a)}, child={len(b)})")
        sys.exit(2)
    same = sum(1 for x, y in zip(a[:n], b[:n]) if x == y)
    print(f"parent={args.parent} ({len(a)} events)")
    print(f"child ={args.child} ({len(b)} events)")
    print(f"common prefix: {n} events, identical: {same} ({same/n*100:.1f}%)")
    if same == n:
        print("FAIL: child is a bit-identical prefix of parent -- NOT a "
              "replication (G4 incident). Set a distinct FLYLOOP_RUNSEED.")
        sys.exit(1)
    first = next(i for i, (x, y) in enumerate(zip(a[:n], b[:n])) if x != y)
    print(f"PASS: runs diverge at event {first} -- independent realizations.")
    if same / n > 0.95:
        print("WARN: >95% identical -- divergence is late; check the seed "
              "actually feeds the sampled paths.")


if __name__ == "__main__":
    main()
