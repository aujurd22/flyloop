# flyloop v4 status — 2026-09-28 20:49:24

- cycle **7159**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: deadline reached，RAM avail 12.9 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 114, 'VARIANT': 50, 'RECALL': 58, 'shocks': 11}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 23390, 'charged_MATCHED': 23663, 'drained': 47053, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 2384, 'MATCHED': 2753, 'EPISODIC': 2919}

## arms (rolling err100)
- **FULL**: puzzle err100=0.08 factA=0.12 factB=0.12 seqA=0.78 seqB=0.76 | probes=3579 discoveries=156 book_test=151 stale=53 cold=0 | episodes={'NEW': 114, 'VARIANT': 50, 'RECALL': 58} | writes=2384 (fact 257, pairs 1113, book 156, pads 0, noise 594) | readback fails fact=0 book=0 table=0
- **MATCHED**: puzzle err100=0.24 factA=0.12 factB=0.12 seqA=0.71 seqB=0.77 | probes=3579 discoveries=0 book_test=0 stale=28 cold=0 | episodes={'NEW': 114, 'VARIANT': 50, 'RECALL': 58} | writes=2753 (fact 257, pairs 1421, book 0, pads 0, noise 594) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.24 factA=0.12 factB=0.12 seqA=0.73 seqB=0.72 | probes=3579 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 114, 'VARIANT': 50, 'RECALL': 58} | writes=2919 (fact 257, pairs 1431, book 0, pads 373, noise 594) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (156)
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
- c6876 fam=2 ep=54 rule `y=(4x+11) mod 13`
- c6934 fam=3 ep=57 rule `y=(12x+0) mod 13`
- c6980 fam=2 ep=55 rule `y=(6x+4) mod 13`
- c7098 fam=1 ep=54 rule `y=(2x+2) mod 13`
- c7136 fam=0 ep=51 rule `y=(10x+9) mod 13`
- c7156 fam=2 ep=56 rule `y=(11x+3) mod 13`

- world expectation: {'fact_rotations': 263, 'puz_rotations': 40, 'episodes': {'NEW': 114, 'VARIANT': 50, 'RECALL': 58}, 'seq_shifts': 14, 'shocks': 11}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | V4-P01 (primary, the V3-P06 fix): recurrences of DISCOVERED rules show a larger F-vs-E ben |  |
| FL-P002 | run | **REGISTERED** | V4-P02 (primary, disentanglement): on recurrences of discovered rules E20 orders F <= M <= |  |
| FL-P003 | run | **REGISTERED** | V4-P03: on recurrences of UNDISCOVERED rules MATCHED beats FULL (dE20 M-F < 0) — the raw-p |  |
| FL-P004 | run | **REGISTERED** | V4-P04: probe-1 recovery exists — FULL book_test fires at probe 1 on RECALL episodes of di |  |
| FL-P005 | run | **REGISTERED** | V4-P05: stale intrusion rate SIR(FULL) <= 1.5 x SIR(EPISODIC) in the three-arm world |  |
| FL-P006 | run | **REGISTERED** | V4-P06 (NC1): VARIANT and NEW contrasts ~ 0 for F-E (|mean dE20| < 0.05) — the advantage s |  |
| FL-P007 | run | **REGISTERED** | V4-P07: quota-gated phase C is reached and the F-E advantage persists there (point estimat |  |
| FL-P008 | run | **REGISTERED** | V4-P08 (NC2): fact lane shows no regression in any arm (phase-C err <= 2x phase-A err and  |  |

