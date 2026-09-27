"""V3 unit tests: schedule properties, reasoner v3 hierarchy, padding parity,
event fields. Run: python tests/test_v3.py"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flyloop import config as C, world, reasoner  # noqa: E402
from flyloop.cycle import PadSync, book_text_v3, pad_text  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        FAILS.append(name)


# ---- schedule -------------------------------------------------------------
s1 = world.puz_schedule()
world._SCHEDULE = None
s2 = world.puz_schedule()
check("schedule deterministic", s1 == s2)
from collections import Counter  # noqa: E402
tot = Counter()
for fam in range(C.PUZ_FAMILIES):
    for ep in s1[fam][:100]:
        tot[ep["type"]] += 1
n = sum(tot.values())
check("episode mix ~ 50/25/25",
      abs(tot["NEW"] / n - .5) < .08 and abs(tot["VARIANT"] / n - .25) < .06
      and abs(tot["RECALL"] / n - .25) < .06, dict(tot))
gaps = Counter(ep["gap"] for fam in range(C.PUZ_FAMILIES)
               for ep in s1[fam][:100] if ep["type"] == "RECALL")
check("gaps within {2,3,4,5}", set(gaps) <= {2, 3, 4, 5}, dict(gaps))
# RECALL returns the exact rule from k epochs ago
ok = True
for fam in range(C.PUZ_FAMILIES):
    eps = s1[fam]
    for i, ep in enumerate(eps):
        if ep["type"] == "RECALL":
            src = eps[i - ep["gap"]]
            if src["rule_id"] != ep["rule_id"] or (src["a"], src["b"]) != (ep["a"], ep["b"]):
                ok = False
check("RECALL returns exact old rule", ok)
# world rule follows schedule
for fam in range(C.PUZ_FAMILIES):
    for cyc in (0, 1, 499, 500, 5000, 77777):
        ep = world.puz_episode(fam, cyc)
        a, b = world.puz_rule(fam, cyc)
        if (a, b) != (ep["a"], ep["b"]):
            ok = False
check("puz_rule matches schedule", ok)

# ---- book registry parse + candidates ------------------------------------
reg_text = book_text_v3(0, {0: {"f0r1": {"a": 3, "b": 5, "ep": 1},
                                "f0r7": {"a": 10, "b": 2, "ep": 7}}}, 123)
reg = reasoner.parse_book_v3(reg_text, 0)
check("parse_book_v3 roundtrip", ("f0r1", 3, 5, 1) in reg and ("f0r7", 10, 2, 7) in reg)
cands = reasoner.book_candidates(reg, C.BOOK_CAP)
check("book candidates ordered by recency", cands[0][0] == "f0r7", str(cands))

# ---- book_test: unique match adopts, ambiguity falls through --------------
p = C.PUZ_P
cands = [("r1", 3, 5, 1), ("r2", 7, 2, 2)]
rule, rank, n_m = reasoner.book_test(cands, [(5, (3 * 5 + 5) % p)], p)
check("book_test unique match", rule is not None and rule[0] == "r1" and rank == 1,
      f"r1={(3*5+5)%p} r2={(7*5+2)%p}")
other = [(a, b) for a in range(1, p) for b in range(p) if (a, b) != (3, 5)
         and (a * 5 + b) % p == (3 * 5 + 5) % p][:1]
rule, rank, n_m = reasoner.book_test([("r1", 3, 5, 1), ("rx", other[0][0], other[0][1], 2)],
                                     [(5, (3 * 5 + 5) % p)], p)
check("book_test ambiguity falls through", rule is None and n_m == 2)
rule, rank, n_m = reasoner.book_test(cands, [(5, (3 * 5 + 5) % p), (9, 99 % p)], p)
check("book_test rejects non-matching second pair", rule is None)

# ---- predict hierarchy ----------------------------------------------------
entries = []  # no memory tables
obs = [(2, (3 * 2 + 5) % p)]
y, method, _, _, ab, aux = reasoner.predict_puzzle_v3(
    entries, 0, 9, 7, cands=cands, obs=[])
check("no obs -> not book_test", method in ("cold", "guess"))
y, method, _, _, ab, aux = reasoner.predict_puzzle_v3(
    entries, 0, 9, 7, cands=[("r1", 3, 5, 1)], obs=obs)
check("1-pair book_test fires", method == "book_test" and ab == (3, 5))
truth_y = (3 * 7 + 5) % p
check("book_test prediction correct", y == truth_y)
# two distinct obs -> fit wins when no candidates
y2, method2, _, _, ab2, _ = reasoner.predict_puzzle_v3(
    entries, 0, 9, 7, cands=None, obs=[(2, (3 * 2 + 5) % p), (4, (3 * 4 + 5) % p)])
check("2-pair fit recovers rule", method2 == "fit" and ab2 == (3, 5))
# stale fit from memory table
old_table = f"REDLOG persona【2:11 4:{(3*4+5)%p} | f0 red c=1 e3】"
y3, method3, _, _, _, _ = reasoner.predict_puzzle_v3(
    [(1, old_table)], 0, 9, 7, cands=None, obs=[])
check("stale fallback flagged", method3 == "fit_stale")

# ---- padding parity -------------------------------------------------------
pad = PadSync()
pad.charge(100)
pad.charge(250)
n1 = pad.take(); n2 = pad.take(); n3 = pad.take()
check("pad fifo + empty", (n1, n2, n3) == (100, 250, None) and
      pad.parity()["charged"] == 350)
t = pad_text(100, 1)
check("pad text exact bytes", len(t.encode("ascii")) == 100 and t.startswith(C.PAD_HEAD))

print()
print("FAILURES:", FAILS if FAILS else "none")
sys.exit(1 if FAILS else 0)
