"""M7.6 audit: at each derivation firing in the M7.5 variant runs, was the
derived (a,b) the world's true composed value?

For every m73-traced NEW probe-1 event (runs m75_ep_s0/s7):
  - reconstruct the probe/world from the deterministic schedule (SEED)
  - true rule      = world.puz_rule(fam, c)
  - world composition (COMPOSITE_FAM only) = ep[i-2] (+/-) ep[i-1]
  - compare dp vs both.
Verdict classes per fam-2 event: dp==true (formula+input right), dp==composed
but != true (schedule degeneracy: composed != actual, happens when i<2 or
fallback draws), dp!=either (input misaligned).
"""
import json, os, sys, collections
os.environ.update({
    "FLYLOOP_NOISE_EPS": "0.25", "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_PREDSET": "V4", "FLYLOOP_COMPOSITE": "1",
    "FLYLOOP_BOOK_CAP": "2", "FLYLOOP_MAX_CYCLES": "30000",
})
os.chdir(r"D:\djr82\flyloop")
sys.path.insert(0, r"D:\djr82\flyloop")
from flyloop import world

C = world.C
CFAM = C.COMPOSITE_FAM
p = C.PUZ_P

def predecessor_params(fam, c, i):
    """Walk cycles back to find episodes i-1 and i-2 of this family."""
    out = {}
    c2 = c - 1
    while c2 > 0 and len(out) < 2:
        ep = world.puz_episode(fam, c2)
        if ep["i"] in (i - 1, i - 2) and ep["i"] not in out:
            out[ep["i"]] = (ep["a"], ep["b"])
        c2 -= 1
    return out

for run in ["m75_ep_s0", "m75_ep_s7"]:
    path = rf"D:\djr82\mbn\m75_results\flycloud\runs\{run}\events.jsonl"
    cls = collections.Counter()
    fam2_detail = []
    for line in open(path, encoding="utf-8"):
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get("lane") != "puzzle" or r.get("episode_type") != "NEW" \
                or r.get("probe_idx") != 1:
            continue
        note = next((t for t in r.get("notes", [])
                     if t.startswith("m73:")), None)
        if note is None:
            continue
        import re
        m = re.search(r"dp=f\d+r\d+,(\d+),(\d+),(\d+)", note)
        a_d, b_d, ep_d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        fam, c, epoch = r["family"], r["c"], r["epoch"]
        if ep_d != epoch:
            cls["stale_dp"] += 1
            continue
        a_t, b_t = world.puz_rule(fam, c)
        dp_true = (a_d == a_t and b_d == b_t)
        if fam != CFAM:
            cls["noncomposite_poison"] += (0 if dp_true else 1)
            continue
        ep = world.puz_episode(fam, c)
        preds = predecessor_params(fam, c, ep["i"])
        if (ep["i"] - 1) in preds and (ep["i"] - 2) in preds:
            a1, b1 = preds[ep["i"] - 1]
            a2, b2 = preds[ep["i"] - 2]
            comp = ((a2 + a1) % p, (b2 - b1) % p)
        else:
            comp = None
        dp_comp = (comp is not None and (a_d, b_d) == comp)
        if dp_true:
            k = "dp==true"
        elif dp_comp and comp != (a_t, b_t):
            k = "dp==composed_but_composed!=true"
        elif dp_comp:
            k = "dp==composed==true(should be dp_true)"
        else:
            k = "dp!=either(input misaligned)"
        cls[k] += 1
        if len(fam2_detail) < 5:
            fam2_detail.append(
                f"c={c} dp={(a_d, b_d)} true={(a_t, b_t)} comp={comp} -> {k}")
    print(f"=== {run}")
    for k, v in sorted(cls.items()):
        print(f"  {k}: {v}")
    for s in fam2_detail:
        print("   ", s)
