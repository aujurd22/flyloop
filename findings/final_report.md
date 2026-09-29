# flyloop v4 status — 2026-09-29 15:00:03

- cycle **6058**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: STOP file，RAM avail 10.7 GB
- run_status: **ENGINEERING_INVALID:FULL: readback failures 92/1437**
- quotas (need N150/V75/R75/s100): {'NEW': 94, 'VARIANT': 44, 'RECALL': 51, 'shocks': 10}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 31333, 'charged_MATCHED': 20315, 'drained': 51648, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 2029, 'MATCHED': 2283, 'EPISODIC': 2430}

## arms (rolling err100)
- **FULL**: puzzle err100=0.28 factA=0.0 factB=0.0 seqA=0.68 seqB=0.61 | probes=3029 discoveries=133 book_test=151 stale=66 cold=0 | episodes={'NEW': 94, 'VARIANT': 44, 'RECALL': 51} | writes=2123 (fact 216, pairs 1088, book 133, pads 0, noise 446) | readback fails fact=0 book=92 table=0
- **MATCHED**: puzzle err100=0.34 factA=0.0 factB=0.0 seqA=0.68 seqB=0.63 | probes=3029 discoveries=0 book_test=0 stale=34 cold=0 | episodes={'NEW': 94, 'VARIANT': 44, 'RECALL': 51} | writes=2283 (fact 216, pairs 1195, book 0, pads 0, noise 446) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.34 factA=0.0 factB=0.0 seqA=0.66 seqB=0.65 | probes=3029 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 94, 'VARIANT': 44, 'RECALL': 51} | writes=2430 (fact 216, pairs 1209, book 0, pads 319, noise 446) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (133)
- c4714 fam=1 ep=36 rule `y=(12x+10) mod 13`
- c4806 fam=3 ep=43 rule `y=(1x+3) mod 13`
- c4808 fam=0 ep=35 rule `y=(6x+11) mod 13`
- c4892 fam=2 ep=35 rule `y=(11x+10) mod 13`
- c4978 fam=1 ep=38 rule `y=(11x+10) mod 13`
- c5026 fam=1 ep=39 rule `y=(1x+4) mod 13`
- c5052 fam=2 ep=38 rule `y=(9x+11) mod 13`
- c5138 fam=1 ep=40 rule `y=(3x+11) mod 13`
- c5148 fam=2 ep=39 rule `y=(7x+0) mod 13`
- c5208 fam=0 ep=37 rule `y=(4x+3) mod 13`
- c5268 fam=2 ep=40 rule `y=(5x+10) mod 13`
- c5274 fam=1 ep=41 rule `y=(1x+4) mod 13`
- c5278 fam=3 ep=45 rule `y=(5x+8) mod 13`
- c5372 fam=2 ep=41 rule `y=(10x+7) mod 13`
- c5376 fam=0 ep=39 rule `y=(3x+8) mod 13`
- c5418 fam=1 ep=43 rule `y=(1x+4) mod 13`
- c5478 fam=3 ep=46 rule `y=(6x+0) mod 13`
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

- world expectation: {'fact_rotations': 218, 'puz_rotations': 34, 'episodes': {'NEW': 94, 'VARIANT': 44, 'RECALL': 51}, 'seq_shifts': 12, 'shocks': 10}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | RSI0-G1-P01 (accept M1 iff): FULL E20 on discovered-recurrence RECALL episodes < 2.347 (g0 |  |
| FL-P002 | run | **REGISTERED** | RSI0-G1-P02 (mechanism): the no-candidate share of probe-1 failures shrinks vs g0's 15/31  |  |
| FL-P003 | run | **REGISTERED** | RSI0-G1-P03 (no-harm): probe-1 recovery stays >= g0's 38.8% |  |

