"""Pre-launch similarity calibration against the REAL emitters.

Merge zone is 0.75 (0.75<sim<=0.92 rewrites in place); semantic duplicate is
0.92+. Hard constraints:
  - different entities of the same kind must stay BELOW 0.75 pairwise;
  - the same entity updated (same state) must stay ABOVE 0.75 (in-place);
  - each query must rank its own entity first.
Run:  python tests/calibrate_texts.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

from flyloop import config as C  # noqa: E402
from flyloop.cycle import table_text, book_text, fact_text, fam_query, book_query  # noqa: E402
from flyloop.world import distractor_text  # noqa: E402

m = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


def sim(a, b):
    e = m.encode([a, b], normalize_embeddings=True)
    return float(e[0] @ e[1])


def mx(pairs):
    return max(sim(a, b) for a, b in pairs) if pairs else 0.0


fails = []
def check(name, cond, val, detail=""):
    print(f"{'ok  ' if cond else 'FAIL'} {name}: {val:.3f} {detail}")
    if not cond:
        fails.append(name)


tabs = [table_text(f, 10 + f, 53000, "6:10 12:7 5:4 7:3 9:2") for f in range(4)]
tabs_upd = [table_text(f, 10 + f, 53100, "7:3 5:4 12:7 9:2 1:6") for f in range(4)]
rules = {0: (65, 10, 8), 1: (52, 3, 7), 2: (43, 4, 11), 3: (37, 8, 1)}
bk = book_text(rules, 53000)
bk2 = book_text({**rules, 0: (66, 7, 1)}, 53100)
facts = [fact_text(i, C.FACT_WORDS[i], "C", 53000, C.FACT_DESC[i]) for i in range(24)]
noises = [distractor_text(1), distractor_text(99)]

check("table cross-family < 0.75",
      mx([(tabs[i], tabs[j]) for i in range(4) for j in range(i + 1, 4)]) < 0.75,
      mx([(tabs[i], tabs[j]) for i in range(4) for j in range(i + 1, 4)]))
check("table same-fam update > 0.75",
      min(sim(tabs[i], tabs_upd[i]) for i in range(4)) > 0.75,
      min(sim(tabs[i], tabs_upd[i]) for i in range(4)))
check("book vs tables < 0.75", mx([(bk, t) for t in tabs]) < 0.75, mx([(bk, t) for t in tabs]))
check("book vs facts < 0.75", mx([(bk, f) for f in facts]) < 0.75, mx([(bk, f) for f in facts]))
check("book vs noise < 0.75", mx([(bk, n) for n in noises]) < 0.75, mx([(bk, n) for n in noises]))
check("book update > 0.75", sim(bk, bk2) > 0.75, sim(bk, bk2))
check("table vs facts < 0.75", mx([(t, f) for t in tabs for f in facts]) < 0.75,
      mx([(t, f) for t in tabs for f in facts]))
fact_pairs = [(facts[i], facts[j]) for i in range(24) for j in range(i + 1, 24)]
check("fact cross-station < 0.75", mx(fact_pairs) < 0.75, mx(fact_pairs))
check("fact same-station update > 0.75",
      sim(fact_text(0, C.FACT_WORDS[0], "A", 53000, C.FACT_DESC[0]),
          fact_text(0, C.FACT_WORDS[0], "D", 53100, C.FACT_DESC[0])) > 0.75,
      sim(fact_text(0, C.FACT_WORDS[0], "A", 53000, C.FACT_DESC[0]),
          fact_text(0, C.FACT_WORDS[0], "D", 53100, C.FACT_DESC[0])))

print("\n-- retrieval (own entity must rank first) --")
for f in range(4):
    q = fam_query(f)
    ss = sorted(((sim(q, tabs[g]), g) for g in range(4)), reverse=True)
    ok = ss[0][1] == f
    print(f"{'ok  ' if ok else 'FAIL'} fam{f} query -> best={ss[0][1]} {ss[0][0]:.3f} (2nd {ss[1][0]:.3f})")
    if not ok:
        fails.append(f"query_fam{f}")
qb = book_query()
s_book = sim(qb, bk)
s_tabs = mx([(qb, t) for t in tabs])
check("book query ranks book above tables", s_book > s_tabs, s_book, f"tables {s_tabs:.3f}")

print()
if fails:
    print(f"{len(fails)} FAILURES: {fails}")
    sys.exit(1)
print(f"ALL CALIBRATION CONSTRAINTS PASS (tables {max(len(t) for t in tabs)} chars max, "
      f"book {len(bk)}, facts {max(len(f) for f in facts)})")
