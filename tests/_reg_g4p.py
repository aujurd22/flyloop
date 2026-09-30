import json

lin = json.load(open('runs/rsi0_lineage.json', encoding='utf-8'))
gens = lin['generations']
gens[:] = [g for g in gens if g.get('gen') != 5]
gens.append({
    'gen': 5,
    'run': 'rsi0_g4p_20260930_2335',
    'config': {'MATCH_MIN_FRAC': 'adaptive', 'BOOK_CAP': 5,
               'NOISE_EPS': 0.25, 'RUN_SEED': 20260930},
    'FULL_E20': 2.581,
    'note': "TRUE replication of G3 (independent realizations, same "
            "schedule): E20 2.581, paired vs g0 parent +0.163 "
            "CI[-0.976,+1.380] n.s. G3's -0.347 gain is WITHIN REALIZATION "
            "NOISE -- acceptance downgraded to single-realization. "
            "Structured-memory advantage replicates strongly (ADAPT 2.581 "
            "vs MATCHED 5.186 vs EPI 5.372). Improvement menu inside this "
            "world is within realization noise; next accepted mutation "
            "needs a new axis (V9 abstraction-loss world)."
})
for g in gens:
    if g.get('gen') == 3 and 'G4prime' not in g['note']:
        g['note'] = (g['note'] + ' | G4prime REPLICATION: n.s. (+0.163 '
                     'CI[-0.976,+1.380]) -- effect within realization '
                     'noise; acceptance downgraded to single-realization '
                     'evidence.')
json.dump(lin, open('runs/rsi0_lineage.json', 'w', encoding='utf-8'),
          indent=1)
print('lineage gens:', [g['gen'] for g in gens])
