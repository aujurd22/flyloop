"""Launch preflight gate: static asserts that would have caught the two
V7-pair harness bugs BEFORE burning a 2 h run. Run before every multi-arm
launch; any FAILURE aborts the launch.

Checks (each maps 1:1 to a past incident):
  1. PORT-ISOLATION (V7C incident): every arm maps to a DISTINCT service URL
     -- two arms on one store I1-supersede each other's writes and the
     between-arm contrast collapses to exactly 0.
  2. ARM-NAME FAMILIES (V7A incident): every arm's name must be handled by
     the cycle runner's memory-read path -- a new arm that only adds a WRITE
     path but no READ path degenerates both arms to identical fit-only
     behavior (E20 identical to the digit across arms).
  3. BOOK-MODE CONSISTENCY (G1 incident): perrule mode requires per-rule
     state keys; a single-entry key with >~7 rules exceeds the 120-char
     split_chunks threshold and state_key writes get silently rejected.

Usage: python -m tests.preflight --arms FULL,MATCHED,EPISODIC --mode single
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from flyloop import config as C  # noqa: E402

KNOWN_READ_FAMILIES = ("FULL", "FULL-RAW", "MATCHED", "MATCHED-VER", "EPISODIC")
RULE_FAMILIES = ("FULL", "FULL-RAW")
PERRULE_MAX_SAFE_RULES = 7      # ~45 chars/rule entry; >120 splits and rejects


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default=os.environ.get("FLYLOOP_ARMS", "FULL,MATCHED,EPISODIC"))
    ap.add_argument("--mode", default=os.environ.get("FLYLOOP_BOOK_MODE", "single"))
    args = ap.parse_args()
    arms = tuple(a.strip() for a in args.arms.split(",") if a.strip())
    fails = []

    # 1. port/URL isolation
    urls = []
    ports_env = os.environ.get("FLYLOOP_PORTS", "")
    port_list = [p for p in ports_env.split(",") if p] or None
    for arm in arms:
        if port_list:
            url = f"http://{C.MEM_HOST}:{int(port_list[len(urls) % len(port_list)])}/mcp"
        elif arm in ("FULL", "FULL-RAW"):
            url = C.MEM_URL
        elif arm in ("MATCHED", "MATCHED-VER"):
            url = C.MEM_URL_MATCHED
        elif arm == "EPISODIC":
            url = C.MEM_URL_EPI
        else:
            fails.append(f"no URL mapping for arm {arm}")
            continue
        urls.append((arm, url))
    if len({u for _, u in urls}) != len(urls):
        fails.append(f"arms share a service URL: {urls}")

    # 2. arm-name handled by the read path
    for arm in arms:
        if arm not in KNOWN_READ_FAMILIES:
            fails.append(f"arm {arm} not in cycle.py read families")

    # 3. perrule length guard (G1 incident)
    if args.mode == "perrule" or any(a.startswith("FULL") for a in arms):
        n_rules_max = min(C.BOOK_CAP, PERRULE_MAX_SAFE_RULES)
        approx_len = 40 + n_rules_max * 12
        if approx_len > 110:
            fails.append(f"perrule entry ~{approx_len} chars > 110: split_chunks "
                         "threshold risk (G1: silent state_key rejection)")

    # 4. EPISODIC drainer must exist when parity matters
    if "EPISODIC" not in arms and len(arms) > 1:
        print("WARN  no EPISODIC arm: write-parity drained=0 by design (V7A)")

    for arm, url in urls:
        print(f"ok   {arm:12s} -> {url}")
    print(f"ok   book mode: {args.mode}, arms: {arms}, NOISE_EPS: "
          f"{os.environ.get('FLYLOOP_NOISE_EPS', '0')}, "
          f"MATCH_MIN_FRAC: {os.environ.get('FLYLOOP_MATCH_MIN_FRAC', '1.0')}")
    if fails:
        print()
        for f_ in fails:
            print("FAIL", f_)
        sys.exit(1)
    print("PREFLIGHT PASS")


if __name__ == "__main__":
    main()
