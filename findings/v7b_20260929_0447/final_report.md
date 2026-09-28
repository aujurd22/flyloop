# flyloop v4 status — 2026-09-29 06:47:28

- cycle **5728**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: deadline reached，RAM avail 12.0 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 91, 'VARIANT': 42, 'RECALL': 50, 'shocks': 9}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 14270, 'charged_MATCHED': 19423, 'drained': 33693, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 6582, 'MATCHED': 3211, 'EPISODIC': 7128}

## arms (rolling err100)
- **FULL**: puzzle err100=0.64 factA=0.04 factB=0.08 seqA=0.83 seqB=0.83 | probes=2864 discoveries=97 book_test=55 stale=900 cold=0 | episodes={'NEW': 91, 'VARIANT': 42, 'RECALL': 50} | writes=3100 (fact 205, pairs 2169, book 97, pads 0, noise 413) | readback fails fact=0 book=0 table=0
- **MATCHED**: puzzle err100=0.7 factA=0.04 factB=0.08 seqA=0.77 seqB=0.8 | probes=2864 discoveries=0 book_test=0 stale=85 cold=0 | episodes={'NEW': 91, 'VARIANT': 42, 'RECALL': 50} | writes=3211 (fact 205, pairs 2199, book 0, pads 0, noise 413) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.68 factA=0.04 factB=0.08 seqA=0.77 seqB=0.76 | probes=2864 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 91, 'VARIANT': 42, 'RECALL': 50} | writes=3312 (fact 205, pairs 2203, book 0, pads 275, noise 413) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (97)
- c4044 fam=2 ep=29 rule `y=(8x+6) mod 13`
- c4090 fam=1 ep=33 rule `y=(10x+10) mod 13`
- c4180 fam=2 ep=31 rule `y=(2x+6) mod 13`
- c4206 fam=3 ep=35 rule `y=(0x+1) mod 13`
- c4296 fam=0 ep=32 rule `y=(6x+3) mod 13`
- c4422 fam=3 ep=37 rule `y=(2x+0) mod 13`
- c4474 fam=1 ep=35 rule `y=(2x+8) mod 13`
- c4476 fam=2 ep=32 rule `y=(8x+10) mod 13`
- c4478 fam=3 ep=38 rule `y=(1x+3) mod 13`
- c4480 fam=0 ep=33 rule `y=(0x+3) mod 13`
- c4524 fam=2 ep=33 rule `y=(10x+3) mod 13`
- c4672 fam=0 ep=34 rule `y=(10x+12) mod 13`
- c4682 fam=1 ep=36 rule `y=(12x+11) mod 13`
- c4710 fam=3 ep=42 rule `y=(2x+2) mod 13`
- c4814 fam=3 ep=43 rule `y=(0x+0) mod 13`
- c4824 fam=0 ep=35 rule `y=(7x+9) mod 13`
- c4876 fam=2 ep=35 rule `y=(2x+3) mod 13`
- c4978 fam=1 ep=38 rule `y=(8x+6) mod 13`
- c5036 fam=2 ep=38 rule `y=(9x+12) mod 13`
- c5122 fam=1 ep=40 rule `y=(8x+2) mod 13`
- c5184 fam=0 ep=37 rule `y=(5x+12) mod 13`
- c5266 fam=1 ep=41 rule `y=(2x+5) mod 13`
- c5294 fam=3 ep=45 rule `y=(0x+0) mod 13`
- c5296 fam=0 ep=38 rule `y=(12x+3) mod 13`
- c5338 fam=1 ep=43 rule `y=(7x+1) mod 13`
- c5340 fam=2 ep=41 rule `y=(2x+10) mod 13`
- c5448 fam=0 ep=39 rule `y=(4x+8) mod 13`
- c5500 fam=2 ep=42 rule `y=(5x+0) mod 13`
- c5658 fam=1 ep=45 rule `y=(12x+9) mod 13`
- c5724 fam=2 ep=43 rule `y=(5x+7) mod 13`

- world expectation: {'fact_rotations': 208, 'puz_rotations': 32, 'episodes': {'NEW': 91, 'VARIANT': 42, 'RECALL': 50}, 'seq_shifts': 11, 'shocks': 9}
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

