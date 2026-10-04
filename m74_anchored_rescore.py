"""M7.4-1: anchored re-score of the 59 derived-candidate NEW probe-1 answers.

Reconstructs each probe via world.puz_probe under the run's config, then
scores three predictors:
  raw      a_d*xp + b_d            (what the run did)
  anchored y1 + a_d*(xp - x1)      (cancels any b error / wave)
plus direct comparison of dp vs the episode's true (a, b) -- separates
slope errors from intercept errors.
"""
import json, os, re, sys
os.environ['FLYLOOP_PORTS'] = '0'
os.environ['FLYLOOP_NOISE_EPS'] = '0.25'
os.environ['FLYLOOP_MATCH_MIN_FRAC'] = '0.6'
os.environ['FLYLOOP_PREDSET'] = 'V4'
os.environ['FLYLOOP_COMPOSITE'] = '1'
os.environ['FLYLOOP_BOOK_CAP'] = '2'
os.environ['FLYLOOP_MAX_CYCLES'] = '30000'
os.chdir(r'D:\djr82\flyloop')
sys.path.insert(0, r'D:\djr82\flyloop')
from flyloop import world

RUN = r'D:\djr82\flyloop\runs\m73_retest_20261004_2055'
p = world.C.PUZ_P
n = {'matched': 0, 'raw_ok': 0, 'anch_ok': 0, 'slope_ok': 0,
     'full_rule_ok': 0, 'mismatch': 0}
by_fam = {}
with open(os.path.join(RUN, 'events.jsonl'), encoding='utf-8') as f:
    for line in f:
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get('lane') != 'puzzle' or r.get('episode_type') != 'NEW' \
                or r.get('probe_idx') != 1:
            continue
        note = next((t for t in r.get('notes', []) if t.startswith('m73:')
                     and 'flag=1' in t), None)
        if note is None:
            continue
        fam, c = r['family'], r['c']
        m = re.search(r'dp=f\d+r\d+,(\d+),(\d+),(\d+)', note)
        a_d, b_d = int(m.group(1)), int(m.group(2))
        (x1, y1), xp, truth = world.puz_probe(fam, c)
        if truth != r['truth']:
            n['mismatch'] += 1
            continue
        n['matched'] += 1
        a_t, b_t = world.puz_rule(fam, c)
        raw_ok = (a_d * xp + b_d) % p == truth
        anch_ok = (y1 + a_d * ((xp - x1) % p)) % p == truth
        slope_ok = a_d == a_t
        full_ok = (a_d == a_t and b_d == b_t)
        n['raw_ok'] += raw_ok
        n['anch_ok'] += anch_ok
        n['slope_ok'] += slope_ok
        n['full_rule_ok'] += full_ok
        d = by_fam.setdefault(fam, [0, 0, 0, 0])
        d[0] += anch_ok; d[1] += slope_ok; d[2] += full_ok; d[3] += 1

print('reconstructed:', n['matched'], ' truth-mismatch:', n['mismatch'])
print(f"raw  a*xp+b   correct : {n['raw_ok']}/{n['matched']}")
print(f"anch y1+a(xp-x1) correct: {n['anch_ok']}/{n['matched']}")
print(f"dp slope == true slope  : {n['slope_ok']}/{n['matched']}")
print(f"dp (a,b) == true (a,b)  : {n['full_rule_ok']}/{n['matched']}")
for fam in sorted(by_fam):
    a, s, fl, tot = by_fam[fam]
    print(f'  fam {fam}: anch {a}/{tot} slope_ok {s}/{tot} full {fl}/{tot}')
