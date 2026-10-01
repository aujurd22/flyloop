"""One-shot patch: FULL-RES arm plumbing in cycle.py (W9C / M5)."""
p = 'flyloop/cycle.py'
s = open(p, encoding='utf-8').read()
n = 0

old = ('if self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT"):\n'
       '            # RSI-0 G2 perrule mode')
new = ('if self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT", "FULL-RES"):\n'
       '            # RSI-0 G2 perrule mode')
assert old in s
s = s.replace(old, new, 1)
n += 1

old = 'stale_present = bool(cands) if self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT") else ' + chr(92)
new = ('stale_present = bool(cands) if self.arm in ("FULL", "FULL-RAW", '
       '"FULL-ADAPT", "FULL-RES") else ' + chr(92))
assert old in s
s = s.replace(old, new, 1)
n += 1

old = ('if (self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT") and '
       'd["consec"] >= disc_gate')
new = ('if (self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT", "FULL-RES") and '
       'd["consec"] >= disc_gate')
assert old in s
s = s.replace(old, new, 1)
n += 1

old = ('        y, method, n_ver, ab, aux = reasoner.predict_puzzle_v4(' + chr(10)
       + '            entries, fam, epoch, xp, obs, cands=cands, '
         'epi_cands=epi_cands,' + chr(10)
       + '            min_frac=adj_min_frac,' + chr(10)
       + '            epi_tol=0 if self.arm == "MATCHED-EXACT" else None)')
new = ('        res_map = None' + chr(10)
       + '        if self.arm == "FULL-RES" and cands:' + chr(10)
       + '            res_map = {}' + chr(10)
       + '            for rid_c, *_ in cands[:C.BOOK_TEST_K]:' + chr(10)
       + '                try:' + chr(10)
       + '                    rb_res, _ = await self.mem.state_lookup(' + chr(10)
       + '                        reasoner.res_state_key(fam, rid_c))' + chr(10)
       + '                    got = reasoner.parse_res_entry(rb_res or "")' + chr(10)
       + '                    if got:' + chr(10)
       + '                        res_map[rid_c] = got' + chr(10)
       + '                except Exception:' + chr(10)
       + '                    pass' + chr(10)
       + '        y, method, n_ver, ab, aux = reasoner.predict_puzzle_v4(' + chr(10)
       + '            entries, fam, epoch, xp, obs, cands=cands, '
         'epi_cands=epi_cands,' + chr(10)
       + '            min_frac=adj_min_frac,' + chr(10)
       + '            epi_tol=0 if self.arm == "MATCHED-EXACT" else None,'
         + chr(10)
       + '            res_map=res_map)')
assert old in s
s = s.replace(old, new, 1)
n += 1

open(p, 'w', encoding='utf-8').write(s)
print('cycle part1 patches:', n)
