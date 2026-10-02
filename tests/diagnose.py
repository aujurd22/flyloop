"""Run diagnostic: is this experiment healthy at its current progress?

Checks (each maps to a real incident class):
  1. heartbeat freshness  -- ts older than --max-age minutes = worker dead
  2. fails counter        -- any worker-reported failure
  3. cycle progress       -- actual cycles vs cycles expected at elapsed
                             time (detects stall/thrash)
  4. readback failures    -- silent write corruption (fact/book/table)
  5. discoveries present  -- zero discoveries past 25% of the horizon
                             means the discovery machinery never armed
  6. custom gates         -- --gate name>0@fraction: counter `name` must
                             exceed 0 once elapsed fraction passes fraction
                             (e.g. derived_writes>0@0.25, derived_use>0@0.5)

Usage:
  python tests/diagnose.py --run-dir runs/X [--gate derived_writes>0@0.25 ...]
Exit codes: 0 = PASS/WARN, 1 = FAIL (caller can wake the operator).
"""
import argparse
import json
import os
import re
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--max-age", type=float, default=5.0,
                    help="heartbeat max age in minutes")
    ap.add_argument("--gate", action="append", default=[],
                    help="counter>0@fraction, repeatable")
    ap.add_argument("--expected-cycles-per-hour", type=float, default=2600.0,
                    help="rough throughput for the stall check")
    args = ap.parse_args()
    rd = args.run_dir
    fails = []
    warns = []

    def say(s):
        print(s, flush=True)

    # 1. heartbeat freshness + fails + cycle
    hb_path = os.path.join(rd, "heartbeat.json")
    hb = None
    if os.path.exists(hb_path):
        try:
            hb = json.load(open(hb_path, encoding="utf-8"))
        except Exception:
            pass
    if hb is None:
        print(f"FAIL no heartbeat at {hb_path}")
        sys.exit(1)
    age_min = (time.time() - os.path.getmtime(hb_path)) / 60.0
    if age_min > args.max_age:
        fails.append(f"heartbeat stale: {age_min:.1f} min old "
                     f"(> {args.max_age})")
    if hb.get("fails", 0) > 0:
        fails.append(f"worker fails counter = {hb['fails']}")
    cycle = hb.get("cycle", 0)
    say(f"heartbeat: cycle={cycle} fails={hb.get('fails')} "
        f"age={age_min:.1f}min ram={hb.get('ram_gb')}GB")

    # 2. elapsed vs deadline
    dl_path = os.path.join(rd, "deadline.json")
    elapsed_h = None
    if os.path.exists(dl_path):
        dl = json.load(open(dl_path, encoding="utf-8"))
        elapsed_h = (time.time() - dl["wall_start"]) / 3600.0
        say(f"elapsed: {elapsed_h:.2f} h")
        expected = elapsed_h * args.expected_cycles_per_hour
        if elapsed_h > 0.15 and cycle < expected * 0.4:
            fails.append(f"cycle stall: {cycle} vs expected ~{expected:.0f}")

    # 3. readback failures (STATUS.md)
    st_path = os.path.join(rd, "STATUS.md")
    if os.path.exists(st_path):
        txt = open(st_path, encoding="utf-8").read()
        for m in re.finditer(r"readback fails fact=(\d+) book=(\d+) table=(\d+)",
                             txt):
            f_, b_, t_ = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if f_ + b_ + t_ > 0:
                fails.append(f"readback failures fact={f_} book={b_} "
                             f"table={t_}")

    # 4. discoveries present past 25% (FULL-family arms only)
    s_path = os.path.join(rd, "state.json")
    counts = {}
    if os.path.exists(s_path):
        try:
            s = json.load(open(s_path, encoding="utf-8"))
            for name, r in (s.get("runners") or {}).items():
                counts[name] = r.get("counts") or {}
        except Exception:
            pass
    full_arms = {k: v for k, v in counts.items()
                 if k.startswith("FULL") or k == "FULL"}
    if full_arms and elapsed_h is not None:
        tot_disc = sum(c.get("discoveries", 0) for c in full_arms.values())
        if elapsed_h > 0.5 and tot_disc == 0:
            fails.append(f"zero discoveries at {elapsed_h:.2f}h -- "
                         "discovery machinery never armed")
        elif tot_disc == 0:
            warns.append("zero discoveries so far (early)")
        for name, c in full_arms.items():
            say(f"{name}: discoveries={c.get('discoveries', 0)} "
                f"book_writes={c.get('book_writes', 0)}")

    # 5. custom gates
    frac = elapsed_h if elapsed_h is not None else 0.0
    for g in args.gate:
        m = re.match(r"(\w+)>(\d+)@([\d.]+)", g)
        if not m:
            warns.append(f"unparseable gate: {g}")
            continue
        cname, thr, gate_frac = m.group(1), int(m.group(2)), float(m.group(3))
        if frac < gate_frac:
            continue  # gate not yet due
        val = sum((c.get(cname, 0) or 0) for c in counts.values()) \
            if counts else 0
        if val <= thr:
            fails.append(f"gate {cname}={val} at {frac:.2f}h "
                         f"(needed >{thr} past {gate_frac})")
        else:
            say(f"gate ok: {cname}={val} (>{thr} past {gate_frac})")

    for w in warns:
        say(f"WARN {w}")
    for f_ in fails:
        say(f"FAIL {f_}")
    if fails:
        sys.exit(1)
    print("DIAG PASS")


if __name__ == "__main__":
    main()
