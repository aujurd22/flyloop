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
from flyloop.cycle import (table_text, book_text_v3, pad_text, fact_text,  # noqa: E402
                           fam_query)
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
books = [book_text_v3(f, {f: {f"f{f}r1": {"a": 10, "b": 8, "ep": 65},
                              f"f{f}r2": {"a": 3, "b": 7, "ep": 52}}}, 53000)
         for f in range(4)]
books_upd = [book_text_v3(f, {f: {f"f{f}r2": {"a": 3, "b": 7, "ep": 66},
                                  f"f{f}r3": {"a": 4, "b": 11, "ep": 66}}}, 53100)
             for f in range(4)]
pads = [pad_text(80, 1), pad_text(96, 2)]
facts = [fact_text(i, C.FACT_WORDS[i], "C", 53000, C.FACT_DESC[i]) for i in range(24)]
noises = [distractor_text(1), distractor_text(99)]

check("table cross-family < 0.75",
      mx([(tabs[i], tabs[j]) for i in range(4) for j in range(i + 1, 4)]) < 0.75,
      mx([(tabs[i], tabs[j]) for i in range(4) for j in range(i + 1, 4)]))
check("table same-fam update > 0.75",
      min(sim(tabs[i], tabs_upd[i]) for i in range(4)) > 0.75,
      min(sim(tabs[i], tabs_upd[i]) for i in range(4)))
check("book cross-family < 0.75",
      mx([(books[i], books[j]) for i in range(4) for j in range(i + 1, 4)]) < 0.75,
      mx([(books[i], books[j]) for i in range(4) for j in range(i + 1, 4)]))
check("book update > 0.75", min(sim(books[i], books_upd[i]) for i in range(4)) > 0.75,
      min(sim(books[i], books_upd[i]) for i in range(4)))
check("book vs tables < 0.75", mx([(b, t) for b in books for t in tabs]) < 0.75,
      mx([(b, t) for b in books for t in tabs]))
check("book vs facts < 0.75", mx([(b, f) for b in books for f in facts]) < 0.75,
      mx([(b, f) for b in books for f in facts]))
check("book vs noise < 0.75", mx([(b, n) for b in books for n in noises]) < 0.75,
      mx([(b, n) for b in books for n in noises]))
check("pad update > 0.75 (in-place rewrite)", sim(pads[0], pads[1]) > 0.75,
      sim(pads[0], pads[1]))
check("pad vs tables < 0.75", mx([(p, t) for p in pads for t in tabs]) < 0.75,
      mx([(p, t) for p in pads for t in tabs]))
check("pad vs facts < 0.75", mx([(p, f) for p in pads for f in facts]) < 0.75,
      mx([(p, f) for p in pads for f in facts]))
check("pad vs book < 0.75", mx([(p, b) for p in pads for b in books]) < 0.75,
      mx([(p, b) for p in pads for b in books]))
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

print()
if fails:
    print(f"{len(fails)} FAILURES: {fails}")
    sys.exit(1)
print(f"ALL CALIBRATION CONSTRAINTS PASS (tables {max(len(t) for t in tabs)} chars max, "
      f"book {max(len(b) for b in books)}, facts {max(len(f) for f in facts)})")
