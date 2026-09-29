# flyloop v4 status — 2026-09-29 22:11:18

- cycle **6448**，elapsed **2.50 h** / 2 h，memory **FULL http**，end: deadline reached，RAM avail 8.6 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 105, 'VARIANT': 47, 'RECALL': 53, 'shocks': 10}
- three-way write parity (FULL book + MATCHED archive vs EPI pads): {'charged_FULL': 6978, 'charged_MATCHED': 21803, 'drained': 28781, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 2350, 'MATCHED': 2449, 'EPISODIC': 2609}

## arms (rolling err100)
- **FULL**: puzzle err100=0.52 factA=0.04 factB=0.04 seqA=0.62 seqB=0.59 | probes=3224 discoveries=146 book_test=189 stale=58 cold=0 | episodes={'NEW': 105, 'VARIANT': 47, 'RECALL': 53} | writes=2350 (fact 231, pairs 1248, book 146, pads 0, noise 485) | readback fails fact=0 book=0 table=0
- **MATCHED**: puzzle err100=0.54 factA=0.04 factB=0.04 seqA=0.68 seqB=0.66 | probes=3224 discoveries=0 book_test=0 stale=37 cold=0 | episodes={'NEW': 105, 'VARIANT': 47, 'RECALL': 53} | writes=2449 (fact 231, pairs 1293, book 0, pads 0, noise 485) | readback fails fact=0 book=0 table=0
- **EPISODIC**: puzzle err100=0.54 factA=0.04 factB=0.04 seqA=0.66 seqB=0.64 | probes=3224 discoveries=0 book_test=0 stale=0 cold=0 | episodes={'NEW': 105, 'VARIANT': 47, 'RECALL': 53} | writes=2609 (fact 231, pairs 1307, book 0, pads 346, noise 485) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (146)
- c5208 fam=0 ep=37 rule `y=(4x+3) mod 13`
- c5266 fam=1 ep=41 rule `y=(1x+4) mod 13`
- c5268 fam=2 ep=40 rule `y=(5x+10) mod 13`
- c5278 fam=3 ep=45 rule `y=(5x+8) mod 13`
- c5372 fam=2 ep=41 rule `y=(10x+7) mod 13`
- c5376 fam=0 ep=39 rule `y=(3x+8) mod 13`
- c5378 fam=1 ep=43 rule `y=(1x+4) mod 13`
- c5478 fam=3 ep=46 rule `y=(6x+0) mod 13`
- c5504 fam=0 ep=40 rule `y=(11x+7) mod 13`
- c5522 fam=1 ep=44 rule `y=(1x+4) mod 13`
- c5526 fam=3 ep=47 rule `y=(9x+10) mod 13`
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

- world expectation: {'fact_rotations': 234, 'puz_rotations': 35, 'episodes': {'NEW': 105, 'VARIANT': 47, 'RECALL': 53}, 'seq_shifts': 12, 'shocks': 10}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | RSI0-G2-P01 (accept iff): FULL E20 on discovered-recurrence RECALL episodes < 2.347 (g0 po |  |
| FL-P002 | run | **REGISTERED** | RSI0-G2-P02 (mechanism): rulebook_readback_fail stays < 5% of book_writes (G1's failure mo |  |
| FL-P003 | run | **REGISTERED** | RSI0-G2-P03 (coverage): probe-1 book_test hits >= 38.8% (g0 level) — the no-candidate floo |  |

