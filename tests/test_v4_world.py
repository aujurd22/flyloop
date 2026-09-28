"""V4 world tests: variable-length schedule, quota-gated phases, epoch lookup.
Run: python tests/test_v4_world.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flyloop import config as C, world  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        FAILS.append(name)


# ---- determinism ----------------------------------------------------------
s1 = world.puz_schedule()
world._SCHEDULE = None
s2 = world.puz_schedule()
check("schedule deterministic", s1 == s2)

# ---- structure: lengths, prefix sums, horizon ------------------------------
ok_len = ok_prefix = True
for fam in range(C.PUZ_FAMILIES):
    eps = s1[fam]
    prev_end = 0
    for ep in eps:
        if ep["n_probes"] not in C.EPISODE_PROBE_LENS:
            ok_len = False
        if ep["start_cycle"] != prev_end:
            ok_prefix = False
        if ep["end_cycle"] != ep["start_cycle"] + C.PUZ_PROBE_CADENCE * ep["n_probes"]:
            ok_prefix = False
        prev_end = ep["end_cycle"]
check("all lengths in mix", ok_len)
check("prefix sums consistent", ok_prefix)
check("horizon respected", all(eps[-1]["end_cycle"] <= C.SCHEDULE_HORIZON + C.PUZ_PROBE_CADENCE * 40
                               for eps in s1.values()),
      {f: s1[f][-1]["end_cycle"] for f in range(C.PUZ_FAMILIES)})

# ---- episode mix ----------------------------------------------------------
from collections import Counter  # noqa: E402
tot = Counter()
for fam in range(C.PUZ_FAMILIES):
    for ep in s1[fam]:
        tot[ep["type"]] += 1
n = sum(tot.values())
check("episode mix ~ 50/25/25",
      abs(tot["NEW"] / n - .5) < .08 and abs(tot["VARIANT"] / n - .25) < .06
      and abs(tot["RECALL"] / n - .25) < .06, dict(tot))

# ---- RECALL returns the exact old rule ------------------------------------
ok = True
for fam in range(C.PUZ_FAMILIES):
    eps = s1[fam]
    for i, ep in enumerate(eps):
        if ep["type"] == "RECALL":
            src = eps[i - ep["gap"]]
            if src["rule_id"] != ep["rule_id"] or (src["a"], src["b"]) != (ep["a"], ep["b"]):
                ok = False
check("RECALL returns exact old rule", ok)
gaps = Counter(ep["gap"] for fam in range(C.PUZ_FAMILIES)
               for ep in s1[fam] if ep["type"] == "RECALL")
check("gaps within {2,3,4,5}", set(gaps) <= {2, 3, 4, 5}, dict(gaps))

# ---- epoch lookup vs brute force ------------------------------------------
import random  # noqa: E402
random.seed(3)
ok = True
for _ in range(120):
    fam = random.randrange(C.PUZ_FAMILIES)
    eps = s1[fam]
    c = random.randrange(0, min(eps[-1]["end_cycle"], 30000))
    got = world.puz_epoch(fam, c)
    brute = next(i for i, ep in enumerate(eps) if ep["start_cycle"] <= c < ep["end_cycle"])
    if got != brute:
        ok = False
check("puz_epoch matches brute force", ok)

# ---- probes score the CURRENT episode's rule ------------------------------
import numpy as np  # noqa: E402
ok = True
for _ in range(80):
    c = random.randrange(0, 20000)
    if c % 2 != 0:
        continue
    fam = (c // 2) % C.PUZ_FAMILIES
    ep = world.puz_episode(fam, c)
    (x1, y1), xp, truth = world.puz_probe(fam, c)
    if truth != (ep["a"] * xp + ep["b"]) % C.PUZ_P:
        ok = False
    if y1 != (ep["a"] * x1 + ep["b"]) % C.PUZ_P:
        ok = False
check("puz_probe uses current episode rule", ok)

# ---- quota-gated phases ----------------------------------------------------
new_total = sum(1 for fam in range(C.PUZ_FAMILIES) for ep in s1[fam]
                if ep["type"] == "NEW")
ok = True
for _ in range(60):
    c = random.randrange(0, 30000)
    nn = world.puz_episode_counts(c)["NEW"]
    expect = "A"
    for name, gate in C.NOISE_PHASE_GATES:
        if nn >= gate:
            expect = name
    if world.puz_phase(c) != expect or world.noise_every(c) != C.NOISE_EVERY_BY_PHASE[expect]:
        ok = False
check("quota-gated phases consistent", ok)
c_a = world.puz_rotation_cycle(0, 0)
check("phase A at start", world.puz_phase(1) == "A")
# find a cycle past the B gate and past the C gate
b_cycle = next(ep["start_cycle"] for fam in range(C.PUZ_FAMILIES)
               for ep in s1[fam]
               if world.puz_episode_counts(ep["start_cycle"])["NEW"] >= 50)
c_cycle = next(ep["start_cycle"] for fam in range(C.PUZ_FAMILIES)
               for ep in s1[fam]
               if world.puz_episode_counts(ep["start_cycle"])["NEW"] >= 110)
check("phase B reached", world.puz_phase(b_cycle + 1) in ("B", "C"),
      f"at cycle {b_cycle}")
check("phase C reached inside horizon", world.puz_phase(c_cycle + 1) == "C",
      f"at cycle {c_cycle}")

# ---- rotation events at boundaries -----------------------------------------
c0 = s1[0][1]["start_cycle"]
check("rotation event at episode boundary", ("rotate", 0) in
      [(k, w) for k, w in world.puz_rotation_events(c0)], f"c={c0}")
check("no rotation event mid-episode", world.puz_rotation_events(c0 + 1) == [])

print()
print("FAILURES:", FAILS if FAILS else "none")
sys.exit(1 if FAILS else 0)
