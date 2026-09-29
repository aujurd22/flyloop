# flyloop v4 status — 2026-09-30 05:11:22

- cycle **6970**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: STOP file，RAM avail 9.5 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 112, 'VARIANT': 49, 'RECALL': 58, 'shocks': 11}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 40412, 'charged_MATCHED': 0, 'drained': 40412, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL-ADAPT': 2588, 'FULL': 2592, 'EPISODIC': 3161}

## arms (rolling err100)
- **FULL-ADAPT**: puzzle err100=0.34 factA=0.04 factB=0.08 seqA=0.75 seqB=0.71 | probes=3485 discoveries=136 book_test=291 stale=159 cold=0 | episodes={'NEW': 112, 'VARIANT': 49, 'RECALL': 58} | writes=2588 (fact 248, pairs 1383, book 136, pads 0, noise 557) | readback fails fact=0 book=0 table=0
- **FULL**: puzzle err100=0.32 factA=0.04 factB=0.08 seqA=0.72 seqB=0.73 | probes=3485 discoveries=135 book_test=189 stale=72 cold=0 | episodes={'NEW': 112, 'VARIANT': 49, 'RECALL': 58} | writes=2592 (fact 248, pairs 1388, book 135, pads 0, noise 557) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.46 factA=0.04 factB=0.08 seqA=0.74 seqB=0.77 | probes=3485 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 112, 'VARIANT': 49, 'RECALL': 58} | writes=3161 (fact 248, pairs 1821, book 0, pads 271, noise 557) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (136)
- c5376 fam=0 ep=39 rule `y=(3x+8) mod 13`
- c5378 fam=1 ep=43 rule `y=(1x+4) mod 13`
- c5478 fam=3 ep=46 rule `y=(6x+0) mod 13`
- c5504 fam=0 ep=40 rule `y=(11x+7) mod 13`
- c5526 fam=3 ep=47 rule `y=(9x+10) mod 13`
- c5530 fam=1 ep=44 rule `y=(1x+4) mod 13`
- c5556 fam=2 ep=42 rule `y=(5x+12) mod 13`
- c5638 fam=3 ep=48 rule `y=(7x+10) mod 13`
- c5666 fam=1 ep=45 rule `y=(11x+2) mod 13`
- c5702 fam=3 ep=49 rule `y=(8x+11) mod 13`
- c5704 fam=0 ep=42 rule `y=(11x+10) mod 13`
- c5772 fam=2 ep=43 rule `y=(4x+7) mod 13`
- c5808 fam=0 ep=43 rule `y=(3x+5) mod 13`
- c6018 fam=1 ep=47 rule `y=(8x+9) mod 13`
- c6166 fam=3 ep=51 rule `y=(4x+6) mod 13`
- c6188 fam=2 ep=45 rule `y=(4x+11) mod 13`
- c6200 fam=0 ep=44 rule `y=(1x+7) mod 13`
- c6258 fam=1 ep=49 rule `y=(10x+10) mod 13`
- c6310 fam=3 ep=52 rule `y=(2x+10) mod 13`
- c6382 fam=3 ep=53 rule `y=(12x+6) mod 13`
- c6404 fam=2 ep=49 rule `y=(8x+1) mod 13`
- c6438 fam=3 ep=55 rule `y=(4x+6) mod 13`
- c6560 fam=0 ep=48 rule `y=(2x+0) mod 13`
- c6564 fam=2 ep=51 rule `y=(8x+1) mod 13`
- c6714 fam=1 ep=51 rule `y=(5x+7) mod 13`
- c6768 fam=0 ep=49 rule `y=(1x+7) mod 13`
- c6804 fam=2 ep=54 rule `y=(4x+11) mod 13`
- c6816 fam=0 ep=50 rule `y=(9x+10) mod 13`
- c6838 fam=3 ep=56 rule `y=(10x+1) mod 13`
- c6934 fam=3 ep=57 rule `y=(12x+0) mod 13`

- world expectation: {'fact_rotations': 254, 'puz_rotations': 38, 'episodes': {'NEW': 112, 'VARIANT': 49, 'RECALL': 58}, 'seq_shifts': 13, 'shocks': 11}
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

