# flyloop v4 status — 2026-09-30 12:45:49

- cycle **5517**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: STOP file，RAM avail 12.0 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 88, 'VARIANT': 40, 'RECALL': 49, 'shocks': 9}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 20634, 'charged_MATCHED': 18774, 'drained': 39408, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 1595, 'MATCHED': 1828, 'EPISODIC': 1977}

## arms (rolling err100)
- **FULL**: puzzle err100=0.2 factA=0.04 factB=0.04 seqA=0.81 seqB=0.84 | probes=2758 discoveries=140 book_test=187 stale=44 cold=0 | episodes={'NEW': 88, 'VARIANT': 40, 'RECALL': 49} | writes=1595 (fact 198, pairs 649, book 140, pads 0, noise 392) | readback fails fact=0 book=0 table=0
- **MATCHED**: puzzle err100=0.28 factA=0.04 factB=0.04 seqA=0.79 seqB=0.8 | probes=2758 discoveries=0 book_test=0 stale=30 cold=0 | episodes={'NEW': 88, 'VARIANT': 40, 'RECALL': 49} | writes=1828 (fact 198, pairs 850, book 0, pads 0, noise 392) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.3 factA=0.04 factB=0.04 seqA=0.86 seqB=0.85 | probes=2758 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 88, 'VARIANT': 40, 'RECALL': 49} | writes=1977 (fact 198, pairs 859, book 0, pads 312, noise 392) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (140)
- c4426 fam=1 ep=34 rule `y=(12x+1) mod 13`
- c4450 fam=1 ep=35 rule `y=(4x+10) mod 13`
- c4470 fam=3 ep=38 rule `y=(2x+1) mod 13`
- c4476 fam=2 ep=32 rule `y=(8x+10) mod 13`
- c4496 fam=0 ep=33 rule `y=(1x+6) mod 13`
- c4604 fam=2 ep=33 rule `y=(9x+11) mod 13`
- c4608 fam=0 ep=34 rule `y=(2x+5) mod 13`
- c4662 fam=3 ep=41 rule `y=(5x+8) mod 13`
- c4710 fam=3 ep=42 rule `y=(2x+1) mod 13`
- c4714 fam=1 ep=36 rule `y=(12x+10) mod 13`
- c4766 fam=3 ep=43 rule `y=(1x+3) mod 13`
- c4808 fam=0 ep=35 rule `y=(6x+11) mod 13`
- c4836 fam=2 ep=34 rule `y=(9x+0) mod 13`
- c4892 fam=2 ep=35 rule `y=(11x+10) mod 13`
- c4978 fam=1 ep=38 rule `y=(11x+10) mod 13`
- c4980 fam=2 ep=37 rule `y=(8x+10) mod 13`
- c5026 fam=1 ep=39 rule `y=(1x+4) mod 13`
- c5044 fam=2 ep=38 rule `y=(9x+11) mod 13`
- c5108 fam=2 ep=39 rule `y=(7x+0) mod 13`
- c5122 fam=1 ep=40 rule `y=(3x+11) mod 13`
- c5166 fam=3 ep=45 rule `y=(5x+8) mod 13`
- c5208 fam=0 ep=37 rule `y=(4x+3) mod 13`
- c5250 fam=1 ep=41 rule `y=(1x+4) mod 13`
- c5268 fam=2 ep=40 rule `y=(5x+10) mod 13`
- c5364 fam=2 ep=41 rule `y=(10x+7) mod 13`
- c5376 fam=0 ep=39 rule `y=(3x+8) mod 13`
- c5378 fam=1 ep=43 rule `y=(1x+4) mod 13`
- c5478 fam=3 ep=46 rule `y=(6x+0) mod 13`
- c5504 fam=0 ep=40 rule `y=(11x+7) mod 13`
- c5506 fam=1 ep=44 rule `y=(1x+4) mod 13`

- world expectation: {'fact_rotations': 198, 'puz_rotations': 30, 'episodes': {'NEW': 88, 'VARIANT': 40, 'RECALL': 49}, 'seq_shifts': 11, 'shocks': 9}
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

