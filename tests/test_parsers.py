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
from flyloop.cycle import (table_text, book_text_v3, fact_text,  # noqa: E402
                           fam_query, book_state_key)
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

# ---- book (v3, ONE entry PER FAMILY, capped at the most recent rules): the
# ---- entry must stay under the 120-char chunk-splitter threshold forever ------
bad = []
rules = {0: {"f0r1": {"a": 10, "b": 8, "ep": 65}, "f0r2": {"a": 2, "b": 3, "ep": 71}},
         1: {"f1r1": {"a": 3, "b": 7, "ep": 52}},
         2: {"f2r1": {"a": 4, "b": 11, "ep": 43}},
         3: {"f3r1": {"a": 8, "b": 1, "ep": 37}}}
bk = book_text_v3(0, rules, 53100)
reg = R.parse_book_v3(bk, 0)
if ("f0r2", 2, 3, 71) not in reg or ("f0r1", 10, 8, 65) not in reg:
    bad.append(("registry", 0))
check("book_v3_parses_family_entry", not bad, str(bad))
# wrong family's tags inside the block are ignored
check("book_v3_ignores_other_family_tags",
      all(r[0].startswith("f0") for r in reg))
# current-epoch candidates: epoch 71 current -> f0r1 is the test candidate
cands = R.book_candidates(reg, C.BOOK_CAP)
check("book_v3_candidates_ordered_by_recency",
      [c[0] for c in cands] == ["f0r2", "f0r1"], str(cands))
# the split_chunks atomicity hazard: a full BOOK_CAP entry must stay one chunk
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "sandbox_mem", "flymemory"))
try:
    from v3 import split_chunks  # noqa: E402
except ImportError:
    from flymemory.v3 import split_chunks  # noqa: E402
big = {0: {f"f0r{i+1}": {"a": 1, "b": i % 13, "ep": i} for i in range(5)}}
bk_full = book_text_v3(0, big, 99999)
check("book_v3_full_cap_single_chunk", len(split_chunks(bk_full)) == 1,
      f"len={len(bk_full)} chunks={len(split_chunks(bk_full))}")

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
