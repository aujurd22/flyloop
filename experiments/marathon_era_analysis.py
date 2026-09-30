"""Marathon era analysis (12.5h x 3 launched lines; adaptive==rsi bit-duplicates,
so effectively TWO lines: frozen FULL vs adaptive FULL-ADAPT, same world).

Per era (ERA_SCHEDULE: eps + active families change every ~2500 cycles, the
system is NOT told when):
  - mean probe error (all probes / RECALL only) per memory arm
  - boundary spike (first 60 probes after the boundary)
  - recovery: probes after boundary until a trailing-60 window mean falls
    to <= 1.25 x steady + 0.02 (steady = mean over the era's last 200 probes)

Paired frozen-vs-adaptive deltas per era (same C.SEED world, different
system config -- the legitimate paired contrast).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flyloop.config import ERA_SCHEDULE  # noqa: E402

RUNS = {
    "frozen": "runs/marathon_frozen_20260930_1545",
    "adaptive": "runs/marathon_adaptive_20260930_1545",
}
MEM_ARM = {"frozen": "FULL", "adaptive": "FULL-ADAPT"}


def era_of(cycle):
    for era in reversed(ERA_SCHEDULE):
        if cycle >= era["start"]:
            return era["era"]
    return ERA_SCHEDULE[0]["era"]


def era_end(idx):
    if idx + 1 < len(ERA_SCHEDULE):
        return ERA_SCHEDULE[idx + 1]["start"]
    return 10 ** 9


def load_arm_events(run, arm):
    out = []
    with open(os.path.join(ROOT, run, "events.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("lane") != "puzzle" or r.get("memory_arm") != arm:
                continue
            out.append({"c": r["c"], "err": int(bool(r.get("error"))),
                        "type": r.get("episode_type")})
    out.sort(key=lambda e: e["c"])
    return out


def window_mean(events, lo, hi, etype=None):
    vals = [e["err"] for e in events
            if lo <= e["c"] < hi and (etype is None or e["type"] == etype)]
    return (sum(vals) / len(vals), len(vals)) if vals else (None, 0)


def recovery_probes(events, boundary, steady, cap):
    """Probes after `boundary` until trailing-60 mean <= 1.25*steady + 0.02."""
    post = [e for e in events if e["c"] >= boundary][:cap]
    thr = 1.25 * steady + 0.02
    for i in range(60, len(post) + 1):
        m = sum(x["err"] for x in post[i - 60:i]) / 60.0
        if m <= thr:
            return i
    return None


def main():
    lines = []

    def say(s=""):
        lines.append(s)
        print(s, flush=True)

    say("=== Marathon era analysis (12.5h, 12-era scheduler) ===")
    say("note: adaptive and rsi lines are bit-identical duplicates "
        "(no mutation engine implemented); frozen-vs-adaptive is the "
        "paired contrast (same world, different config).")
    say()

    per_run = {}
    for tag, run in RUNS.items():
        arm = MEM_ARM[tag]
        ev = load_arm_events(run, arm)
        epi = [e for e in ev if e["type"] == "RECALL"]
        per_run[tag] = {"all": ev, "epi": epi}
        say(f"--- {tag} ({arm}), {len(ev)} probes, {len(epi)} RECALL probes ---")
        say(f"{'era':>4} {'eps':>5} {'n':>6} {'err':>6} {'errR':>6} "
            f"{'spike60':>8} {'recover':>8}")
        for i, era in enumerate(ERA_SCHEDULE):
            hi = min(era_end(i), ev[-1]["c"] + 1)
            m, n = window_mean(ev, era["start"], hi)
            mr, nr = window_mean(ev, era["start"], hi, "RECALL")
            spike, _ = window_mean(ev, era["start"], era["start"] + 2000)
            steady, _ = window_mean(ev, max(era["start"], hi - 2500), hi)
            rec = recovery_probes(ev, era["start"], steady or 0,
                                  hi - era["start"]) if i > 0 else None
            say(f"{era['era']:>4} {era['eps']:>5.2f} {n:>6} "
                f"{m if m is not None else float('nan'):>6.3f} "
                f"{mr if mr is not None else float('nan'):>6.3f} "
                f"{spike if spike is not None else float('nan'):>8.3f} "
                f"{str(rec) if rec is not None else '-':>8}")
        say()

    say("--- Paired frozen-vs-adaptive era deltas (same world) ---")
    say(f"{'era':>4} {'frozen':>7} {'adapt':>7} {'delta':>7}")
    deltas = []
    for i, era in enumerate(ERA_SCHEDULE):
        row = []
        for tag in ("frozen", "adaptive"):
            ev = per_run[tag]["all"]
            hi = min(era_end(i), ev[-1]["c"] + 1)
            m, _ = window_mean(ev, era["start"], hi)
            row.append(m)
        if None not in row:
            deltas.append(row[1] - row[0])
            say(f"{era['era']:>4} {row[0]:>7.3f} {row[1]:>7.3f} "
                f"{row[1]-row[0]:>+7.3f}")
    wins = sum(1 for d in deltas if d < 0)
    say(f"adaptive better in {wins}/{len(deltas)} eras; "
        f"mean delta {sum(deltas)/len(deltas):+.4f}" if deltas else "no eras")

    out = os.path.join(ROOT, "findings", "marathon_20260930_1545")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "era_analysis.txt"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nwritten: {os.path.join(out, 'era_analysis.txt')}")


if __name__ == "__main__":
    main()
