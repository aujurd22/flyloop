# flyloop v4 status — 2026-09-30 12:45:49

- cycle **5490**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: STOP file，RAM avail 12.3 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 87, 'VARIANT': 40, 'RECALL': 49, 'shocks': 9}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 18294, 'charged_MATCHED': 18782, 'drained': 37076, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL-ADAPT': 1758, 'MATCHED': 2072, 'EPISODIC': 2209}

## arms (rolling err100)
- **FULL-ADAPT**: puzzle err100=0.12 factA=0.04 factB=0.04 seqA=0.74 seqB=0.77 | probes=2745 discoveries=124 book_test=250 stale=123 cold=0 | episodes={'NEW': 87, 'VARIANT': 40, 'RECALL': 49} | writes=1758 (fact 197, pairs 831, book 124, pads 0, noise 390) | readback fails fact=0 book=0 table=0
- **MATCHED**: puzzle err100=0.2 factA=0.04 factB=0.04 seqA=0.76 seqB=0.73 | probes=2745 discoveries=0 book_test=0 stale=31 cold=0 | episodes={'NEW': 87, 'VARIANT': 40, 'RECALL': 49} | writes=2072 (fact 197, pairs 1097, book 0, pads 0, noise 390) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.22 factA=0.04 factB=0.04 seqA=0.8 seqB=0.8 | probes=2745 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 87, 'VARIANT': 40, 'RECALL': 49} | writes=2209 (fact 197, pairs 1110, book 0, pads 296, noise 390) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (124)
- c4198 fam=3 ep=35 rule `y=(1x+4) mod 13`
- c4216 fam=0 ep=32 rule `y=(12x+4) mod 13`
- c4252 fam=2 ep=31 rule `y=(9x+8) mod 13`
- c4326 fam=3 ep=36 rule `y=(5x+6) mod 13`
- c4398 fam=3 ep=37 rule `y=(1x+4) mod 13`
- c4470 fam=3 ep=38 rule `y=(2x+1) mod 13`
- c4474 fam=1 ep=35 rule `y=(4x+10) mod 13`
- c4476 fam=2 ep=32 rule `y=(8x+10) mod 13`
- c4496 fam=0 ep=33 rule `y=(1x+6) mod 13`
- c4604 fam=2 ep=33 rule `y=(9x+11) mod 13`
- c4608 fam=0 ep=34 rule `y=(2x+5) mod 13`
- c4714 fam=1 ep=36 rule `y=(12x+10) mod 13`
- c4806 fam=3 ep=43 rule `y=(1x+3) mod 13`
- c4808 fam=0 ep=35 rule `y=(6x+11) mod 13`
- c4836 fam=2 ep=34 rule `y=(9x+0) mod 13`
- c4892 fam=2 ep=35 rule `y=(11x+10) mod 13`
- c4978 fam=1 ep=38 rule `y=(11x+10) mod 13`
- c4980 fam=2 ep=37 rule `y=(8x+10) mod 13`
- c5026 fam=1 ep=39 rule `y=(1x+4) mod 13`
- c5036 fam=2 ep=38 rule `y=(9x+11) mod 13`
- c5138 fam=1 ep=40 rule `y=(3x+11) mod 13`
- c5148 fam=2 ep=39 rule `y=(7x+0) mod 13`
- c5208 fam=0 ep=37 rule `y=(4x+3) mod 13`
- c5258 fam=1 ep=41 rule `y=(1x+4) mod 13`
- c5260 fam=2 ep=40 rule `y=(5x+10) mod 13`
- c5278 fam=3 ep=45 rule `y=(5x+8) mod 13`
- c5372 fam=2 ep=41 rule `y=(10x+7) mod 13`
- c5376 fam=0 ep=39 rule `y=(3x+8) mod 13`
- c5378 fam=1 ep=43 rule `y=(1x+4) mod 13`
- c5478 fam=3 ep=46 rule `y=(6x+0) mod 13`

- world expectation: {'fact_rotations': 197, 'puz_rotations': 29, 'episodes': {'NEW': 88, 'VARIANT': 40, 'RECALL': 49}, 'seq_shifts': 10, 'shocks': 9}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | RSI0-G1-P01 (accept M1 iff): FULL E20 on discovered-recurrence RECALL episodes < 2.347 (g0 |  |
| FL-P002 | run | **REGISTERED** | RSI0-G1-P02 (mechanism): the no-candidate share of probe-1 failures shrinks vs g0's 15/31  |  |
| FL-P003 | run | **REGISTERED** | RSI0-G1-P03 (no-harm): probe-1 recovery stays >= g0's 38.8% |  |

