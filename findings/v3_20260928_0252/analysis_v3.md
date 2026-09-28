# V3 analysis — D:\djr82\flyloop\runs\v3_20260928_0252 — 2026-09-28 13:33:13
run_status: OK
episodes observed (paired log): {'VARIANT': 71, 'NEW': 135, 'RECALL': 78}
P1 dE20 (EPI-FULL) on RECALL: n=78 mean=0.641 CI=[0.513,0.769] perm_p=0.0
P2 dLatency (EPI-FULL) on RECALL: n=78 mean=0.551 CI=[0.423,0.679] perm_p=0.0
P3 gap buckets (gap, n, dE): [(2, 24, 0.625), (3, 17, 0.7058823529411765), (4, 17, 0.47058823529411764), (5, 20, 0.75)] -> all favor FULL: True
P4 |dE| VARIANT=0.014 (n=71) vs RECALL=0.641 (n=78) -> variant_smaller=True
P5 SIR FULL=0.0408 (232, 5680) vs EPI=0.0287 (163, 5680) -> ratio=1.4233128834355828
P6 UIR=0.712 vs permutation null 95th pct=0.693
P7 phases: {'A': {'mult': 1, 'n_recall': 47, 'dE': 0.7021276595744681, 'full_first20_err': 0.08465458663646659, 'epi_first20_err': 0.09456398640996602}, 'B': {'mult': 2, 'n_recall': 31, 'dE': 0.5483870967741935, 'full_first20_err': 0.08286778398510242, 'epi_first20_err': 0.09078212290502793}, 'C': {'mult': 4, 'n_recall': 0, 'dE': None, 'full_first20_err': None, 'epi_first20_err': None}}
P8 fact lane: {'FULL': {'A': {'phaseA': 0.0696, 'phaseC': None}, 'B': {'phaseA': 0.06813333333333334, 'phaseC': None}}, 'EPI': {'A': {'phaseA': 0.0696, 'phaseC': None}, 'B': {'phaseA': 0.06813333333333334, 'phaseC': None}}}
