"""Parser fuzz + truncation tests for flyloop v2 (run before launch).

Simulates the exact recall truncation (80 chars) and asserts every text form
the loop writes remains parseable, PLUS the v1 failure mode is now impossible
(c= sits before any pair list). Book entries are read via state_lookup which
does NOT truncate, but they are still checked under an 80-char cut for safety.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flyloop import config as C
from flyloop import reasoner as R
from flyloop.cycle import table_text, book_text, fact_text, BOOK_KEY
from flyloop.world import puz_probe, puz_rule, fact_channel  # noqa: F401

TRUNC = 80  # recall truncation in mcp_v3.py

fails = []
def check(name, cond, detail=""):
    if not cond:
        fails.append(f"{name}: {detail}")
        print(f"FAIL {name} {detail}")
    else:
        print(f"ok   {name}")

# ---- fact: parse under truncation for all 24 stations, channels, cycles ------
bad = []
for st in range(C.FACT_STATIONS):
    for ch in "ABCDE":
        for c in (1, 999, 53100, 123456):
            t = fact_text(st, C.FACT_WORDS[st], ch, c, C.FACT_DESC[st])
            m = R.P_FACT.search(t[:TRUNC])
            if not (m and int(m.group(1)) == st and m.group(3) == ch and int(m.group(4)) == c):
                bad.append((st, ch, c, t[:TRUNC]))
check("fact_all_24x5x4_parse_under_truncation", not bad, str(bad[:1]))

# ---- table: parse under truncation, pairs FIRST (a cut can never fabricate a
# ---- half pair token), c= early; with <=5 pairs the whole text fits in 80 ----
import random
random.seed(7)
bad = []
for fam in range(4):
    for ep in (0, 3, 17, 65):
        for c in (500, 53100, 99999):
            pairs = " ".join(f"{x}:{y}" for x, y in
                             [(random.randrange(13), random.randrange(13)) for _ in range(5)])
            t = table_text(fam, ep, c, pairs)
            m = R.P_PAIRS.search(t[:TRUNC])
            ok = (m and int(m.group(2)) == fam and int(m.group(4)) == c
                  and int(m.group(5)) == ep and len(R.parse_pairs(m.group(1))) >= 2)
            if not ok:
                bad.append((fam, ep, c, t[:TRUNC]))
check("table_always_parseable_with_2plus_pairs_under_truncation", not bad, str(bad[:1]))

# ---- length bounds -----------------------------------------------------------
maxlen = max(len(table_text(f, 65, 99999, "12:12 11:11 10:10 9:9 8:8")) for f in range(4))
check("table_len<=80", maxlen <= 80, f"maxlen={maxlen}")
maxf = max(len(fact_text(i, C.FACT_WORDS[i], "A", 99999, C.FACT_DESC[i])) for i in range(24))
check("fact_len<=90", maxf <= 90, f"maxlen={maxf}")

# ---- book: parse for all families, epochs; survives truncation too -----------
bad = []
rules = {0: (65, 10, 8), 1: (52, 3, 7), 2: (43, 4, 11), 3: (37, 8, 1)}
bk = book_text(rules, 53100)
for fam, (ep, a, b) in rules.items():
    if R.parse_book(bk, fam, ep) != (a, b):
        bad.append(("full", fam))
    if R.parse_book(bk[:TRUNC], fam, ep) != (a, b):
        bad.append(("trunc", fam))
check("book_parses_all_families_full_and_truncated", not bad, str(bad))
check("book_stale_epoch_rejected", R.parse_book(bk, 0, 64) is None)
check("book_len<=80", len(bk) <= 80, f"len={len(bk)}")

# ---- reasoner end-to-end on synthetic entries --------------------------------
a_true, b_true = 10, 8
pairs = [(3, (a_true*3+b_true) % 13), (5, (a_true*5+b_true) % 13),
         (7, (a_true*7+b_true) % 13)]
t = table_text(0, 4, 53100, " ".join(f"{x}:{y}" for x, y in pairs))
y, method, eids, n_ver, ab = R.predict_puzzle([(1, t)], 0, 4, 9)
check("puzzle_fit_finds_rule",
      method == "fit" and ab == (a_true, b_true) and y == (a_true*9+b_true) % 13,
      f"method={method} ab={ab} y={y}")
y, method, eids, n_ver, ab = R.predict_puzzle([(1, table_text(0, 3, 53100, "3:12 5:6"))], 0, 4, 9)
check("puzzle_stale_fit_flagged", method == "fit_stale" and ab == (a_true, b_true),
      f"method={method} ab={ab}")
y, method, eids, n_ver, ab = R.predict_puzzle([], 0, 4, 9)
check("puzzle_empty_is_cold", method == "cold")

# ---- fact from state_lookup response -----------------------------------------
resp = f"[flyloop/st-7] CURRENT: {fact_text(7, C.FACT_WORDS[7], 'C', 53123, C.FACT_DESC[7])} (since just now)"
ch, evid = R.predict_fact_from_state(resp, 7)
check("fact_state_lookup_parse", ch == "C")
ch, evid = R.predict_fact_from_state(resp, 8)
check("fact_state_lookup_wrong_station", ch is None)

print()
if fails:
    print(f"{len(fails)} FAILURES")
    sys.exit(1)
print("ALL PARSER TESTS PASS")
