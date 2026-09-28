# flyloop v4 status — 2026-09-29 04:42:36

- cycle **9529**，elapsed **2.00 h** / 2 h，memory **FULL http**，end: deadline reached，RAM avail 12.1 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 154, 'VARIANT': 69, 'RECALL': 79, 'shocks': 15}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 36785, 'charged_MATCHED': 20874, 'drained': 0, 'pending': 57659, 'pending_events': 429}
- memory entries: {'FULL-RAW': 3487, 'MATCHED-VER': 3821}

## arms (rolling err100)
- **FULL-RAW**: puzzle err100=0.2 factA=0.12 factB=0.2 seqA=0.74 seqB=0.8 | probes=4764 discoveries=241 book_test=125 stale=187 cold=0 | episodes={'NEW': 154, 'VARIANT': 69, 'RECALL': 79} | writes=3487 (fact 340, pairs 1478, book 241, pads 0, noise 1068) | readback fails fact=0 book=0 table=0
- **MATCHED-VER**: puzzle err100=0.24 factA=0.12 factB=0.2 seqA=0.74 seqB=0.75 | probes=4764 discoveries=0 book_test=0 stale=42 cold=0 | episodes={'NEW': 154, 'VARIANT': 69, 'RECALL': 79} | writes=3821 (fact 340, pairs 1865, book 0, pads 0, noise 1068) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (241)
- c8368 fam=0 ep=63 rule `y=(12x+8) mod 13`
- c8438 fam=3 ep=67 rule `y=(8x+10) mod 13`
- c8502 fam=3 ep=68 rule `y=(4x+7) mod 13`
- c8592 fam=0 ep=64 rule `y=(12x+9) mod 13`
- c8626 fam=1 ep=68 rule `y=(8x+5) mod 13`
- c8642 fam=1 ep=69 rule `y=(6x+11) mod 13`
- c8676 fam=2 ep=64 rule `y=(4x+10) mod 13`
- c8742 fam=3 ep=70 rule `y=(12x+5) mod 13`
- c8754 fam=1 ep=70 rule `y=(10x+0) mod 13`
- c8768 fam=0 ep=65 rule `y=(1x+12) mod 13`
- c8862 fam=3 ep=71 rule `y=(2x+3) mod 13`
- c8864 fam=0 ep=66 rule `y=(12x+11) mod 13`
- c8950 fam=3 ep=72 rule `y=(1x+10) mod 13`
- c8992 fam=0 ep=67 rule `y=(12x+8) mod 13`
- c8998 fam=3 ep=73 rule `y=(6x+9) mod 13`
- c9034 fam=1 ep=73 rule `y=(5x+5) mod 13`
- c9064 fam=0 ep=68 rule `y=(11x+9) mod 13`
- c9076 fam=2 ep=66 rule `y=(1x+9) mod 13`
- c9114 fam=1 ep=74 rule `y=(4x+11) mod 13`
- c9142 fam=3 ep=74 rule `y=(2x+4) mod 13`
- c9204 fam=2 ep=67 rule `y=(2x+11) mod 13`
- c9216 fam=0 ep=70 rule `y=(12x+2) mod 13`
- c9226 fam=1 ep=76 rule `y=(6x+7) mod 13`
- c9284 fam=2 ep=68 rule `y=(3x+1) mod 13`
- c9286 fam=3 ep=75 rule `y=(12x+5) mod 13`
- c9414 fam=3 ep=77 rule `y=(12x+11) mod 13`
- c9432 fam=0 ep=72 rule `y=(12x+1) mod 13`
- c9498 fam=1 ep=77 rule `y=(2x+12) mod 13`
- c9508 fam=2 ep=70 rule `y=(5x+11) mod 13`
- c9522 fam=1 ep=78 rule `y=(9x+6) mod 13`

- world expectation: {'fact_rotations': 355, 'puz_rotations': 54, 'episodes': {'NEW': 154, 'VARIANT': 69, 'RECALL': 79}, 'seq_shifts': 19, 'shocks': 15}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | V7-P01 (support dominance): |dE20(F - F-RAW)| < |dE20(M - M-VER)| under eps=0.25 -- suppor |  |
| FL-P002 | run | **REGISTERED** | V7-P02: unverified full-support rule writes hurt -- dE20(F-RAW vs F) > 0 (poisoned rules c |  |
| FL-P003 | run | **REGISTERED** | V7-P03: verified sparse archive helps -- dE20(M-VER vs M) <= 0 |  |
| FL-P004 | run | **REGISTERED** | V7-P04: SIR(F-RAW) > SIR(F) -- poisoned rules intrude more (absolute counts reported, floo |  |
| FL-P005 | run | **REGISTERED** | V7-P05: interaction sign -- the write-verification effect is larger at full support than a |  |

