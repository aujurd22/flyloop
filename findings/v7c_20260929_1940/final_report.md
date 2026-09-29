# flyloop v4 status — 2026-09-29 22:11:17

- cycle **6839**，elapsed **2.50 h** / 2 h，memory **FULL http**，end: deadline reached，RAM avail 8.7 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 110, 'VARIANT': 48, 'RECALL': 58, 'shocks': 11}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 48083, 'charged_MATCHED': 0, 'drained': 48083, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 2261, 'FULL-RAW': 2313, 'EPISODIC': 2739}

## arms (rolling err100)
- **FULL**: puzzle err100=0.28 factA=0.08 factB=0.0 seqA=0.76 seqB=0.83 | probes=3419 discoveries=150 book_test=145 stale=50 cold=0 | episodes={'NEW': 110, 'VARIANT': 48, 'RECALL': 58} | writes=2261 (fact 244, pairs 1073, book 150, pads 0, noise 530) | readback fails fact=0 book=0 table=0
- **FULL-RAW**: puzzle err100=0.36 factA=0.08 factB=0.0 seqA=0.78 seqB=0.84 | probes=3419 discoveries=171 book_test=88 stale=157 cold=0 | episodes={'NEW': 110, 'VARIANT': 48, 'RECALL': 58} | writes=2313 (fact 244, pairs 1104, book 171, pads 0, noise 530) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.36 factA=0.08 factB=0.0 seqA=0.79 seqB=0.83 | probes=3419 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 110, 'VARIANT': 48, 'RECALL': 58} | writes=2739 (fact 244, pairs 1380, book 0, pads 321, noise 530) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (150)
- c5504 fam=0 ep=40 rule `y=(11x+7) mod 13`
- c5526 fam=3 ep=47 rule `y=(9x+10) mod 13`
- c5554 fam=1 ep=44 rule `y=(1x+4) mod 13`
- c5556 fam=2 ep=42 rule `y=(5x+12) mod 13`
- c5638 fam=3 ep=48 rule `y=(7x+10) mod 13`
- c5648 fam=0 ep=42 rule `y=(11x+10) mod 13`
- c5666 fam=1 ep=45 rule `y=(11x+2) mod 13`
- c5676 fam=2 ep=43 rule `y=(4x+7) mod 13`
- c5702 fam=3 ep=49 rule `y=(8x+11) mod 13`
- c5784 fam=0 ep=43 rule `y=(3x+5) mod 13`
- c5910 fam=3 ep=51 rule `y=(4x+6) mod 13`
- c5988 fam=2 ep=44 rule `y=(2x+5) mod 13`
- c6018 fam=1 ep=47 rule `y=(8x+9) mod 13`
- c6104 fam=0 ep=44 rule `y=(1x+7) mod 13`
- c6148 fam=2 ep=45 rule `y=(4x+11) mod 13`
- c6218 fam=1 ep=48 rule `y=(1x+0) mod 13`
- c6258 fam=1 ep=49 rule `y=(10x+10) mod 13`
- c6292 fam=2 ep=47 rule `y=(6x+11) mod 13`
- c6294 fam=3 ep=52 rule `y=(2x+10) mod 13`
- c6372 fam=2 ep=49 rule `y=(8x+1) mod 13`
- c6382 fam=3 ep=53 rule `y=(10x+1) mod 13`
- c6438 fam=3 ep=55 rule `y=(4x+6) mod 13`
- c6548 fam=2 ep=51 rule `y=(8x+1) mod 13`
- c6560 fam=0 ep=48 rule `y=(2x+0) mod 13`
- c6714 fam=1 ep=51 rule `y=(5x+7) mod 13`
- c6768 fam=0 ep=49 rule `y=(1x+7) mod 13`
- c6772 fam=2 ep=53 rule `y=(1x+12) mod 13`
- c6816 fam=0 ep=50 rule `y=(9x+10) mod 13`
- c6818 fam=1 ep=52 rule `y=(4x+10) mod 13`
- c6838 fam=3 ep=56 rule `y=(10x+1) mod 13`

- world expectation: {'fact_rotations': 248, 'puz_rotations': 38, 'episodes': {'NEW': 110, 'VARIANT': 48, 'RECALL': 58}, 'seq_shifts': 13, 'shocks': 11}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | V7C-P01: the write-depth sign resolves — dE20(F-RAW - F) on RECALL episodes with cluster-b |  |

