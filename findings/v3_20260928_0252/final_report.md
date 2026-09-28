# flyloop v3 status — 2026-09-28 12:53:03

- cycle **48326**，elapsed **10.00 h** / 10 h，memory **FULL http**，end: STOP file，RAM avail 16.5 GB
- run_status: **OK**
- quotas (need N150/V75/R75/s100): {'NEW': 135, 'VARIANT': 71, 'RECALL': 78, 'shocks': 80}
- write parity (FULL book vs EPI pads): {'charged': 44074, 'drained': 44074, 'pending': 0, 'pending_events': 0}
- memory entries: {'FULL': 10472, 'EPI': 10516}

## arms (rolling err100)
- **FULL**: puzzle err100=0.0 factA=0.08 factB=0.12 seqA=0.73 seqB=0.75 | probes=24163 discoveries=284 book_test=301 stale=232 cold=80 | episodes={'NEW': 135, 'VARIANT': 71, 'RECALL': 78} | writes=10472 (fact 1646, pairs 3290, book 284, pads 0, noise 3332) | readback fails fact=0 book=0 table=0
- **EPI**: puzzle err100=0.0 factA=0.08 factB=0.12 seqA=0.75 seqB=0.72 | probes=24163 discoveries=0 book_test=0 stale=163 cold=103 | episodes={'NEW': 135, 'VARIANT': 71, 'RECALL': 78} | writes=10516 (fact 1646, pairs 3334, book 0, pads 284, noise 3332) | readback fails fact=0 book=0 table=0

## FULL bins (1k cycles)

## FULL insights (284)
- c43244 fam=2 ep=54 rule `y=(11x+1) mod 13`
- c43528 fam=0 ep=87 rule `y=(1x+2) mod 13`
- c43594 fam=1 ep=67 rule `y=(1x+0) mod 13`
- c43742 fam=3 ep=46 rule `y=(4x+6) mod 13`
- c44036 fam=2 ep=55 rule `y=(6x+8) mod 13`
- c44040 fam=0 ep=88 rule `y=(3x+1) mod 13`
- c44250 fam=1 ep=68 rule `y=(2x+2) mod 13`
- c44552 fam=0 ep=89 rule `y=(2x+3) mod 13`
- c44694 fam=3 ep=47 rule `y=(3x+9) mod 13`
- c44844 fam=2 ep=56 rule `y=(2x+9) mod 13`
- c44890 fam=1 ep=69 rule `y=(4x+0) mod 13`
- c45040 fam=0 ep=90 rule `y=(1x+11) mod 13`
- c45536 fam=0 ep=91 rule `y=(2x+3) mod 13`
- c45546 fam=1 ep=70 rule `y=(8x+7) mod 13`
- c45628 fam=2 ep=57 rule `y=(6x+8) mod 13`
- c45646 fam=3 ep=48 rule `y=(12x+10) mod 13`
- c46048 fam=0 ep=92 rule `y=(12x+12) mod 13`
- c46194 fam=1 ep=71 rule `y=(4x+9) mod 13`
- c46436 fam=2 ep=58 rule `y=(2x+9) mod 13`
- c46528 fam=0 ep=93 rule `y=(1x+11) mod 13`
- c46590 fam=3 ep=49 rule `y=(10x+8) mod 13`
- c46842 fam=1 ep=72 rule `y=(10x+12) mod 13`
- c47048 fam=0 ep=94 rule `y=(11x+0) mod 13`
- c47244 fam=2 ep=59 rule `y=(12x+11) mod 13`
- c47490 fam=1 ep=73 rule `y=(1x+4) mod 13`
- c47542 fam=3 ep=50 rule `y=(8x+4) mod 13`
- c47544 fam=0 ep=95 rule `y=(9x+3) mod 13`
- c48036 fam=2 ep=60 rule `y=(6x+8) mod 13`
- c48040 fam=0 ep=96 rule `y=(11x+10) mod 13`
- c48146 fam=1 ep=74 rule `y=(7x+6) mod 13`

- world expectation: {'fact_rotations': 1836, 'puz_rotations': 280, 'episodes': {'NEW': 135, 'VARIANT': 71, 'RECALL': 78}, 'seq_shifts': 96, 'shocks': 80}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | V3-P01 (PRIMARY): Full arm RECALL error in the first 20 probes lower than Episodic, paired |  |
| FL-P002 | run | **REGISTERED** | V3-P02 (PRIMARY): Full arm recovery latency (first correct probe) shorter than Episodic on |  |
| FL-P003 | run | **REGISTERED** | V3-P03: the Full advantage survives at every recurrence gap 2/3/4/5 (point estimate of dE  |  |
| FL-P004 | run | **REGISTERED** | V3-P04 (NC1): |dE| on VARIANT clearly smaller than on RECALL — the Full advantage is recur |  |
| FL-P005 | run | **REGISTERED** | V3-P05: stale intrusion rate SIR(Full) <= 1.5 x SIR(Episodic) — remembering more must not  |  |
| FL-P006 | run | **REGISTERED** | V3-P06: useful-insight rate (discoveries whose rule later pays off on a recurrence) above  |  |
| FL-P007 | run | **REGISTERED** | V3-P07: Full degrades slower than Episodic from noise phase A (1x) to phase C (4x), on REC |  |
| FL-P008 | run | **REGISTERED** | V3-P08 (NC2): fact lane shows no regression under the v3 policy: phase-C err100 <= 2x phas |  |

