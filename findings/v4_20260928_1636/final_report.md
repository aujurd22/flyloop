# flyloop v4 status — 2026-09-28 18:32:26

- cycle **6386**，elapsed **1.92 h** / 10 h，memory **FULL http**，end: STOP file，RAM avail 11.8 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 104, 'VARIANT': 47, 'RECALL': 51, 'shocks': 10}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 27307, 'charged_MATCHED': 21606, 'drained': 48913, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 1585, 'MATCHED': 1610, 'EPISODIC': 1815}

## arms (rolling err100)
- **FULL**: puzzle err100=0.1 factA=0.08 factB=0.04 seqA=0.72 seqB=0.73 | probes=3193 discoveries=182 book_test=193 stale=44 cold=0 | episodes={'NEW': 104, 'VARIANT': 47, 'RECALL': 51} | writes=1585 (fact 230, pairs 454, book 182, pads 0, noise 479) | readback fails fact=0 book=0 table=0
- **MATCHED**: puzzle err100=0.1 factA=0.08 factB=0.04 seqA=0.72 seqB=0.81 | probes=3193 discoveries=0 book_test=0 stale=15 cold=0 | episodes={'NEW': 104, 'VARIANT': 47, 'RECALL': 51} | writes=1610 (fact 230, pairs 463, book 0, pads 0, noise 479) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.1 factA=0.08 factB=0.04 seqA=0.75 seqB=0.74 | probes=3193 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 104, 'VARIANT': 47, 'RECALL': 51} | writes=1815 (fact 230, pairs 486, book 0, pads 380, noise 479) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (182)
- c5268 fam=2 ep=40 rule `y=(5x+10) mod 13`
- c5338 fam=1 ep=43 rule `y=(1x+4) mod 13`
- c5344 fam=0 ep=39 rule `y=(3x+8) mod 13`
- c5364 fam=2 ep=41 rule `y=(10x+7) mod 13`
- c5478 fam=3 ep=46 rule `y=(6x+0) mod 13`
- c5488 fam=0 ep=40 rule `y=(11x+7) mod 13`
- c5490 fam=1 ep=44 rule `y=(1x+4) mod 13`
- c5508 fam=2 ep=42 rule `y=(5x+12) mod 13`
- c5526 fam=3 ep=47 rule `y=(9x+10) mod 13`
- c5606 fam=3 ep=48 rule `y=(7x+10) mod 13`
- c5616 fam=0 ep=42 rule `y=(11x+10) mod 13`
- c5666 fam=1 ep=45 rule `y=(11x+2) mod 13`
- c5668 fam=2 ep=43 rule `y=(4x+7) mod 13`
- c5686 fam=3 ep=49 rule `y=(8x+11) mod 13`
- c5776 fam=0 ep=43 rule `y=(3x+5) mod 13`
- c5830 fam=3 ep=50 rule `y=(6x+0) mod 13`
- c5902 fam=3 ep=51 rule `y=(4x+6) mod 13`
- c5988 fam=2 ep=44 rule `y=(2x+5) mod 13`
- c6018 fam=1 ep=47 rule `y=(8x+9) mod 13`
- c6104 fam=0 ep=44 rule `y=(1x+7) mod 13`
- c6106 fam=1 ep=48 rule `y=(1x+0) mod 13`
- c6148 fam=2 ep=45 rule `y=(4x+11) mod 13`
- c6214 fam=3 ep=52 rule `y=(2x+10) mod 13`
- c6258 fam=1 ep=49 rule `y=(10x+10) mod 13`
- c6260 fam=2 ep=47 rule `y=(6x+11) mod 13`
- c6264 fam=0 ep=45 rule `y=(2x+0) mod 13`
- c6336 fam=0 ep=46 rule `y=(1x+9) mod 13`
- c6372 fam=2 ep=49 rule `y=(8x+1) mod 13`
- c6374 fam=3 ep=53 rule `y=(10x+1) mod 13`
- c6384 fam=0 ep=47 rule `y=(3x+11) mod 13`

- world expectation: {'fact_rotations': 231, 'puz_rotations': 34, 'episodes': {'NEW': 105, 'VARIANT': 47, 'RECALL': 51}, 'seq_shifts': 12, 'shocks': 10}
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

