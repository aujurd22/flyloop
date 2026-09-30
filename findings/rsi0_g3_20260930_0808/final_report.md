# flyloop v4 status — 2026-09-30 10:09:18

- cycle **7078**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: STOP file，RAM avail 9.5 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 113, 'VARIANT': 49, 'RECALL': 58, 'shocks': 11}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 23506, 'charged_MATCHED': 23436, 'drained': 46942, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL-ADAPT': 2322, 'MATCHED': 2726, 'EPISODIC': 2891}

## arms (rolling err100)
- **FULL-ADAPT**: puzzle err100=0.14 factA=0.08 factB=0.12 seqA=0.88 seqB=0.82 | probes=3539 discoveries=157 book_test=308 stale=153 cold=0 | episodes={'NEW': 113, 'VARIANT': 49, 'RECALL': 58} | writes=2322 (fact 253, pairs 1070, book 157, pads 0, noise 578) | readback fails fact=0 book=0 table=0
- **MATCHED**: puzzle err100=0.34 factA=0.08 factB=0.12 seqA=0.79 seqB=0.86 | probes=3539 discoveries=0 book_test=0 stale=41 cold=0 | episodes={'NEW': 113, 'VARIANT': 49, 'RECALL': 58} | writes=2726 (fact 253, pairs 1416, book 0, pads 0, noise 578) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.34 factA=0.08 factB=0.12 seqA=0.81 seqB=0.82 | probes=3539 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 113, 'VARIANT': 49, 'RECALL': 58} | writes=2891 (fact 253, pairs 1424, book 0, pads 372, noise 578) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (157)
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
- c6096 fam=0 ep=44 rule `y=(1x+7) mod 13`
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
- c6782 fam=3 ep=56 rule `y=(10x+1) mod 13`
- c6802 fam=1 ep=52 rule `y=(4x+10) mod 13`
- c6804 fam=2 ep=54 rule `y=(4x+11) mod 13`
- c6816 fam=0 ep=50 rule `y=(9x+10) mod 13`
- c6934 fam=3 ep=57 rule `y=(12x+0) mod 13`
- c6980 fam=2 ep=55 rule `y=(6x+4) mod 13`

- world expectation: {'fact_rotations': 259, 'puz_rotations': 39, 'episodes': {'NEW': 113, 'VARIANT': 49, 'RECALL': 58}, 'seq_shifts': 14, 'shocks': 11}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | RSI0-G1-P01 (accept M1 iff): FULL E20 on discovered-recurrence RECALL episodes < 2.347 (g0 |  |
| FL-P002 | run | **REGISTERED** | RSI0-G1-P02 (mechanism): the no-candidate share of probe-1 failures shrinks vs g0's 15/31  |  |
| FL-P003 | run | **REGISTERED** | RSI0-G1-P03 (no-harm): probe-1 recovery stays >= g0's 38.8% |  |

