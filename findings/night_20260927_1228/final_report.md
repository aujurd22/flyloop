# flyloop status — 2026-09-27 17:26:08

- cycle **46134**，elapsed **5.00 h** / 5 h，memory **http**，poets A:cuda(u=92268), B:cuda(u=92268)
- end condition: deadline reached，RAM avail 7.1 GB

## rolling error (window=100)
- **seqA**: n=46134, err100=0.8
- **seqB**: n=46134, err100=0.76
- **factA**: n=11534, err100=0.12
- **puzzle**: n=23067, err100=0.0
- **factB**: n=11533, err100=0.12

## counts
- writes=9140 (fact 1609, pairs 3224, rules None, noise 2306), rejected=0, recalls=69201
- rule discoveries = **177**，cold=None，readback_fail=0
- puzzle prediction methods: {'cold': 186, 'guess': 190, 'fit': 17069, 'fit_stale': 139, 'book': 5483}
- recall hit: factA 11519/11534, factB 11524/11533, puzzle 0/0
- flymemory: `entries=9140`

## drift response
- total drift events observed: 2077 (shocks seen 61/60), events in log: 2077
- **fact**: 1801/1801 recovered, median 0 cycles
- **seq**: 90/91 recovered, median 0 cycles
- **puzzle**: 172/172 recovered, median 0 cycles

## error by 1000-cycle bins
- seqA: 0k:0.773 | 1k:0.8 | 2k:0.792 | 3k:0.756 | 4k:0.753 | 5k:0.808 | 6k:0.738 | 7k:0.773 | 8k:0.772 | 9k:0.768 | 10k:0.746 | 11k:0.793 | 12k:0.756 | 13k:0.747 | 14k:0.791 | 15k:0.78 | 16k:0.75 | 17k:0.806 | 18k:0.728 | 19k:0.741 | 20k:0.769 | 21k:0.775 | 22k:0.774 | 23k:0.781 | 24k:0.769 | 25k:0.782 | 26k:0.825 | 27k:0.742 | 28k:0.756 | 29k:0.79 | 30k:0.743 | 31k:0.753 | 32k:0.808 | 33k:0.774 | 34k:0.758 | 35k:0.815 | 36k:0.757 | 37k:0.785 | 38k:0.761 | 39k:0.787 | 40k:0.757 | 41k:0.758 | 42k:0.786 | 43k:0.763 | 44k:0.799 | 45k:0.758 | 46k:0.836
- seqB: 0k:0.786 | 1k:0.792 | 2k:0.81 | 3k:0.762 | 4k:0.76 | 5k:0.79 | 6k:0.742 | 7k:0.752 | 8k:0.763 | 9k:0.78 | 10k:0.739 | 11k:0.795 | 12k:0.766 | 13k:0.757 | 14k:0.802 | 15k:0.752 | 16k:0.734 | 17k:0.802 | 18k:0.73 | 19k:0.737 | 20k:0.765 | 21k:0.775 | 22k:0.774 | 23k:0.769 | 24k:0.756 | 25k:0.792 | 26k:0.83 | 27k:0.747 | 28k:0.749 | 29k:0.775 | 30k:0.758 | 31k:0.745 | 32k:0.829 | 33k:0.771 | 34k:0.771 | 35k:0.797 | 36k:0.742 | 37k:0.786 | 38k:0.76 | 39k:0.788 | 40k:0.756 | 41k:0.781 | 42k:0.767 | 43k:0.766 | 44k:0.79 | 45k:0.768 | 46k:0.799
- factA: 0k:0.108 | 1k:0.076 | 2k:0.072 | 3k:0.056 | 4k:0.064 | 5k:0.072 | 6k:0.084 | 7k:0.052 | 8k:0.092 | 9k:0.052 | 10k:0.076 | 11k:0.076 | 12k:0.076 | 13k:0.068 | 14k:0.088 | 15k:0.044 | 16k:0.056 | 17k:0.064 | 18k:0.076 | 19k:0.048 | 20k:0.072 | 21k:0.072 | 22k:0.068 | 23k:0.084 | 24k:0.092 | 25k:0.044 | 26k:0.088 | 27k:0.076 | 28k:0.064 | 29k:0.068 | 30k:0.076 | 31k:0.068 | 32k:0.068 | 33k:0.056 | 34k:0.06 | 35k:0.076 | 36k:0.076 | 37k:0.064 | 38k:0.104 | 39k:0.068 | 40k:0.072 | 41k:0.056 | 42k:0.068 | 43k:0.056 | 44k:0.076 | 45k:0.072 | 46k:0.088
- factB: 0k:0.088 | 1k:0.064 | 2k:0.072 | 3k:0.072 | 4k:0.06 | 5k:0.076 | 6k:0.052 | 7k:0.08 | 8k:0.06 | 9k:0.08 | 10k:0.06 | 11k:0.076 | 12k:0.06 | 13k:0.064 | 14k:0.08 | 15k:0.08 | 16k:0.072 | 17k:0.084 | 18k:0.06 | 19k:0.084 | 20k:0.088 | 21k:0.052 | 22k:0.06 | 23k:0.064 | 24k:0.06 | 25k:0.084 | 26k:0.056 | 27k:0.052 | 28k:0.084 | 29k:0.072 | 30k:0.064 | 31k:0.072 | 32k:0.06 | 33k:0.072 | 34k:0.068 | 35k:0.064 | 36k:0.06 | 37k:0.06 | 38k:0.04 | 39k:0.064 | 40k:0.084 | 41k:0.088 | 42k:0.064 | 43k:0.076 | 44k:0.084 | 45k:0.048 | 46k:0.121
- puzzle: 0k:0.02 | 1k:0.016 | 2k:0.018 | 3k:0.014 | 4k:0.014 | 5k:0.012 | 6k:0.014 | 7k:0.018 | 8k:0.018 | 9k:0.012 | 10k:0.012 | 11k:0.014 | 12k:0.018 | 13k:0.014 | 14k:0.016 | 15k:0.018 | 16k:0.016 | 17k:0.014 | 18k:0.03 | 19k:0.02 | 20k:0.014 | 21k:0.028 | 22k:0.014 | 23k:0.014 | 24k:0.024 | 25k:0.02 | 26k:0.014 | 27k:0.014 | 28k:0.03 | 29k:0.03 | 30k:0.016 | 31k:0.026 | 32k:0.042 | 33k:0.026 | 34k:0.022 | 35k:0.028 | 36k:0.026 | 37k:0.022 | 38k:0.034 | 39k:0.026 | 40k:0.046 | 41k:0.008 | 42k:0.026 | 43k:0.018 | 44k:0.042 | 45k:0.014 | 46k:0.03

## A/B arms (cumulative)
- fact recall arm: hit 11519/11534 | state_lookup arm: hit 11524/11533

## insights (177)
- c38500 fam=2 ep=32 rule `y=(2x+2) mod 13`
- c38576 fam=0 ep=48 rule `y=(12x+2) mod 13`
- c39098 fam=1 ep=39 rule `y=(5x+7) mod 13`
- c39304 fam=0 ep=49 rule `y=(3x+3) mod 13`
- c39326 fam=3 ep=28 rule `y=(12x+9) mod 13`
- c39700 fam=2 ep=33 rule `y=(8x+9) mod 13`
- c40098 fam=1 ep=40 rule `y=(3x+10) mod 13`
- c40192 fam=0 ep=50 rule `y=(3x+10) mod 13`
- c40702 fam=3 ep=29 rule `y=(4x+10) mod 13`
- c40840 fam=0 ep=51 rule `y=(10x+3) mod 13`
- c40908 fam=2 ep=34 rule `y=(4x+7) mod 13`
- c41098 fam=1 ep=41 rule `y=(12x+9) mod 13`
- c41640 fam=0 ep=52 rule `y=(10x+4) mod 13`
- c42098 fam=1 ep=42 rule `y=(11x+2) mod 13`
- c42100 fam=2 ep=35 rule `y=(11x+4) mod 13`
- c42150 fam=3 ep=30 rule `y=(2x+10) mod 13`
- c42496 fam=0 ep=53 rule `y=(9x+2) mod 13`
- c43098 fam=1 ep=43 rule `y=(3x+6) mod 13`
- c43296 fam=0 ep=54 rule `y=(6x+10) mod 13`
- c43300 fam=2 ep=36 rule `y=(10x+7) mod 13`
- c43502 fam=3 ep=31 rule `y=(7x+8) mod 13`
- c44090 fam=1 ep=44 rule `y=(11x+7) mod 13`
- c44096 fam=0 ep=55 rule `y=(3x+4) mod 13`
- c44500 fam=2 ep=37 rule `y=(3x+8) mod 13`
- c44928 fam=0 ep=56 rule `y=(11x+9) mod 13`
- c44958 fam=3 ep=32 rule `y=(1x+4) mod 13`
- c45098 fam=1 ep=45 rule `y=(12x+10) mod 13`
- c45640 fam=0 ep=57 rule `y=(6x+4) mod 13`
- c45708 fam=2 ep=38 rule `y=(8x+0) mod 13`
- c46098 fam=1 ep=46 rule `y=(3x+3) mod 13`

- world drift expectation: {'fact_rotations': 1751, 'puz_rotations': 173, 'seq_shifts': 92, 'shocks': 61}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REGISTERED** | V2-P01: cold rate (puzzle) <= 5% after truncation fix |  |
| FL-P002 | run | **REGISTERED** | V2-P02: rule entries survive active in their own compartment: >=90% of discoveries readabl |  |
| FL-P003 | run | **REGISTERED** | V2-P03: fact B arm (state_lookup) error <= half of fact A arm (recall) error |  |
| FL-P004 | run | **REGISTERED** | V2-P04: write-readback failures on sampled fact writes <= 2% |  |
| FL-P005 | run | **REGISTERED** | V2-P05: no invariant violations observed (I1 active-unique via state_history) |  |
| FL-P006 | run | **REGISTERED** | V2-P06: seq stream B (regime marker) rolling err < 0.68 (oracle 0.639) |  |
| FL-P007 | run | **REGISTERED** | V2-P07: seq stream A replicates v1 stall: err >= 0.70 for >= 90% of 1k-bins |  |
| FL-P008 | run | **REGISTERED** | V2-P08: signature CONFIRMED ratio in [0.4, 0.9] (no overflow) |  |
| FL-P009 | run | **REGISTERED** | V2-P09: >=40000 cycles in 5h (speed target), 0 breaker trips |  |
| FL-P010 | run | **REGISTERED** | V2-P10: memory entries <= 40000 at end |  |
| FL-P011 | signature | **PARTIAL** | fam1 ep0 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P012 | signature | **PARTIAL** | fam2 ep0 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P013 | signature | **PARTIAL** | fam3 ep0 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P014 | signature | **PARTIAL** | fam0 ep0 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P015 | signature | **PARTIAL** | fam0 ep1 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P016 | signature | **PARTIAL** | fam1 ep1 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P017 | signature | **PARTIAL** | fam2 ep1 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P018 | signature | **PARTIAL** | fam3 ep1 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P019 | signature | **CONFIRMED** | fam0 ep2 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P020 | signature | **CONFIRMED** | fam1 ep2 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P021 | signature | **PARTIAL** | fam2 ep2 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P022 | signature | **PARTIAL** | fam0 ep3 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P023 | signature | **PARTIAL** | fam3 ep2 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P024 | signature | **PARTIAL** | fam1 ep3 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P025 | signature | **PARTIAL** | fam0 ep4 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P026 | signature | **PARTIAL** | fam2 ep3 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P027 | signature | **CONFIRMED** | fam0 ep5 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.114 post=0.000 ratio=114285714.29 |
| FL-P028 | signature | **PARTIAL** | fam1 ep4 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P029 | signature | **PARTIAL** | fam3 ep3 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P030 | signature | **PARTIAL** | fam0 ep6 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P031 | signature | **PARTIAL** | fam2 ep4 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P032 | signature | **PARTIAL** | fam1 ep5 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P033 | signature | **PARTIAL** | fam0 ep7 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P034 | signature | **PARTIAL** | fam3 ep4 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P035 | signature | **PARTIAL** | fam1 ep6 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P036 | signature | **PARTIAL** | fam2 ep5 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P037 | signature | **PARTIAL** | fam0 ep8 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P038 | signature | **PARTIAL** | fam1 ep7 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P039 | signature | **PARTIAL** | fam3 ep5 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P040 | signature | **PARTIAL** | fam0 ep9 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P041 | signature | **PARTIAL** | fam2 ep6 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P042 | signature | **PARTIAL** | fam0 ep10 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P043 | signature | **PARTIAL** | fam1 ep8 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P044 | signature | **PARTIAL** | fam2 ep7 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P045 | signature | **PARTIAL** | fam3 ep6 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P046 | signature | **PARTIAL** | fam0 ep11 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P047 | signature | **PARTIAL** | fam1 ep9 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P048 | signature | **PARTIAL** | fam2 ep8 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P049 | signature | **PARTIAL** | fam0 ep12 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P050 | signature | **PARTIAL** | fam3 ep7 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P051 | signature | **PARTIAL** | fam1 ep10 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P052 | signature | **PARTIAL** | fam0 ep13 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P053 | signature | **PARTIAL** | fam2 ep9 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P054 | signature | **PARTIAL** | fam1 ep11 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P055 | signature | **CONFIRMED** | fam0 ep14 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.114 post=0.000 ratio=114285714.29 |
| FL-P056 | signature | **PARTIAL** | fam3 ep8 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P057 | signature | **PARTIAL** | fam0 ep15 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P058 | signature | **PARTIAL** | fam1 ep12 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P059 | signature | **PARTIAL** | fam2 ep10 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P060 | signature | **PARTIAL** | fam3 ep9 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.0 post=0.0 |
| FL-P061 | signature | **PARTIAL** | fam0 ep16 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P062 | signature | **PARTIAL** | fam1 ep13 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P063 | signature | **PARTIAL** | fam2 ep11 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P064 | signature | **PARTIAL** | fam0 ep17 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P065 | signature | **PARTIAL** | fam1 ep14 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P066 | signature | **PARTIAL** | fam3 ep10 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P067 | signature | **PARTIAL** | fam0 ep18 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P068 | signature | **PARTIAL** | fam2 ep12 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P069 | signature | **PARTIAL** | fam1 ep15 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P070 | signature | **PARTIAL** | fam0 ep19 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P071 | signature | **CONFIRMED** | fam3 ep11 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P072 | signature | **CONFIRMED** | fam2 ep13 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P073 | signature | **PARTIAL** | fam0 ep20 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P074 | signature | **PARTIAL** | fam1 ep16 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P075 | signature | **PARTIAL** | fam0 ep21 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P076 | signature | **PARTIAL** | fam2 ep14 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P077 | signature | **PARTIAL** | fam3 ep12 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P078 | signature | **PARTIAL** | fam1 ep17 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P079 | signature | **CONFIRMED** | fam0 ep22 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P080 | signature | **PARTIAL** | fam2 ep15 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P081 | signature | **PARTIAL** | fam1 ep18 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P082 | signature | **PARTIAL** | fam3 ep13 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P083 | signature | **CONFIRMED** | fam0 ep23 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.000 ratio=171428571.43 |
| FL-P084 | signature | **PARTIAL** | fam1 ep19 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P085 | signature | **PARTIAL** | fam0 ep24 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P086 | signature | **PARTIAL** | fam2 ep16 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P087 | signature | **CONFIRMED** | fam3 ep14 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P088 | signature | **PARTIAL** | fam0 ep25 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P089 | signature | **PARTIAL** | fam1 ep20 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P090 | signature | **PARTIAL** | fam2 ep17 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P091 | signature | **CONFIRMED** | fam0 ep26 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P092 | signature | **CONFIRMED** | fam1 ep21 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P093 | signature | **CONFIRMED** | fam3 ep15 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P094 | signature | **CONFIRMED** | fam2 ep18 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P095 | signature | **CONFIRMED** | fam0 ep27 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P096 | signature | **PARTIAL** | fam1 ep22 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P097 | signature | **CONFIRMED** | fam3 ep16 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P098 | signature | **PARTIAL** | fam0 ep28 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P099 | signature | **PARTIAL** | fam2 ep19 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P100 | signature | **PARTIAL** | fam1 ep23 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P101 | signature | **PARTIAL** | fam0 ep29 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P102 | signature | **PARTIAL** | fam3 ep17 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P103 | signature | **CONFIRMED** | fam1 ep24 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.033 ratio=2.57 |
| FL-P104 | signature | **CONFIRMED** | fam2 ep20 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.033 ratio=2.57 |
| FL-P105 | signature | **CONFIRMED** | fam0 ep30 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P106 | signature | **PARTIAL** | fam0 ep31 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P107 | signature | **PARTIAL** | fam1 ep25 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P108 | signature | **PARTIAL** | fam2 ep21 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P109 | signature | **PARTIAL** | fam3 ep18 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P110 | signature | **CONFIRMED** | fam0 ep32 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P111 | signature | **PARTIAL** | fam1 ep26 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P112 | signature | **PARTIAL** | fam0 ep33 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P113 | signature | **PARTIAL** | fam2 ep22 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P114 | signature | **PARTIAL** | fam3 ep19 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P115 | signature | **PARTIAL** | fam1 ep27 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P116 | signature | **PARTIAL** | fam0 ep34 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P117 | signature | **CONFIRMED** | fam2 ep23 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P118 | signature | **CONFIRMED** | fam1 ep28 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P119 | signature | **CONFIRMED** | fam3 ep20 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P120 | signature | **CONFIRMED** | fam0 ep35 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P121 | signature | **CONFIRMED** | fam2 ep24 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P122 | signature | **CONFIRMED** | fam0 ep36 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P123 | signature | **CONFIRMED** | fam1 ep29 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P124 | signature | **CONFIRMED** | fam3 ep21 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.067 ratio=2.57 |
| FL-P125 | signature | **PARTIAL** | fam0 ep37 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P126 | signature | **PARTIAL** | fam1 ep30 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P127 | signature | **PARTIAL** | fam2 ep25 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P128 | signature | **CONFIRMED** | fam0 ep38 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P129 | signature | **PARTIAL** | fam3 ep22 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P130 | signature | **PARTIAL** | fam1 ep31 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P131 | signature | **CONFIRMED** | fam2 ep26 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P132 | signature | **CONFIRMED** | fam0 ep39 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.000 ratio=171428571.43 |
| FL-P133 | signature | **CONFIRMED** | fam1 ep32 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P134 | signature | **CONFIRMED** | fam0 ep40 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.114 post=0.000 ratio=114285714.29 |
| FL-P135 | signature | **CONFIRMED** | fam3 ep23 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.067 ratio=2.14 |
| FL-P136 | signature | **PARTIAL** | fam2 ep27 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P137 | signature | **CONFIRMED** | fam0 ep41 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P138 | signature | **PARTIAL** | fam1 ep33 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P139 | signature | **CONFIRMED** | fam0 ep42 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.114 post=0.000 ratio=114285714.29 |
| FL-P140 | signature | **CONFIRMED** | fam2 ep28 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P141 | signature | **CONFIRMED** | fam3 ep24 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P142 | signature | **PARTIAL** | fam1 ep34 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P143 | signature | **CONFIRMED** | fam0 ep43 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P144 | signature | **PARTIAL** | fam2 ep29 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P145 | signature | **CONFIRMED** | fam1 ep35 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P146 | signature | **CONFIRMED** | fam3 ep25 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P147 | signature | **CONFIRMED** | fam0 ep44 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.114 post=0.000 ratio=114285714.29 |
| FL-P148 | signature | **CONFIRMED** | fam0 ep45 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P149 | signature | **CONFIRMED** | fam1 ep36 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P150 | signature | **CONFIRMED** | fam2 ep30 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P151 | signature | **CONFIRMED** | fam3 ep26 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P152 | signature | **CONFIRMED** | fam0 ep46 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P153 | signature | **PARTIAL** | fam1 ep37 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P154 | signature | **PARTIAL** | fam2 ep31 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P155 | signature | **CONFIRMED** | fam0 ep47 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P156 | signature | **CONFIRMED** | fam3 ep27 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P157 | signature | **PARTIAL** | fam1 ep38 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P158 | signature | **REFUTED** | fam2 ep32 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.200 ratio=0.29 |
| FL-P159 | signature | **CONFIRMED** | fam0 ep48 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.000 ratio=171428571.43 |
| FL-P160 | signature | **PARTIAL** | fam1 ep39 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P161 | signature | **CONFIRMED** | fam0 ep49 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P162 | signature | **CONFIRMED** | fam3 ep28 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P163 | signature | **PARTIAL** | fam2 ep33 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P164 | signature | **REFUTED** | fam1 ep40 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.086 post=0.267 ratio=0.32 |
| FL-P165 | signature | **CONFIRMED** | fam0 ep50 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.000 ratio=171428571.43 |
| FL-P166 | signature | **PARTIAL** | fam3 ep29 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P167 | signature | **CONFIRMED** | fam0 ep51 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.033 ratio=4.29 |
| FL-P168 | signature | **CONFIRMED** | fam2 ep34 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P169 | signature | **PARTIAL** | fam1 ep41 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P170 | signature | **CONFIRMED** | fam0 ep52 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P171 | signature | **REFUTED** | fam1 ep42 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.100 ratio=0.29 |
| FL-P172 | signature | **REFUTED** | fam2 ep35 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.067 ratio=0.43 |
| FL-P173 | signature | **CONFIRMED** | fam3 ep30 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P174 | signature | **PARTIAL** | fam0 ep53 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P175 | signature | **PARTIAL** | fam1 ep43 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P176 | signature | **PARTIAL** | fam0 ep54 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P177 | signature | **PARTIAL** | fam2 ep36 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P178 | signature | **PARTIAL** | fam3 ep31 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P179 | signature | **CONFIRMED** | fam1 ep44 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P180 | signature | **CONFIRMED** | fam0 ep55 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P181 | signature | **PARTIAL** | fam2 ep37 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P182 | signature | **CONFIRMED** | fam0 ep56 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.257 post=0.000 ratio=257142857.14 |
| FL-P183 | signature | **CONFIRMED** | fam3 ep32 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.067 ratio=3.43 |
| FL-P184 | signature | **PARTIAL** | fam1 ep45 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.0 post=0.0 |
| FL-P185 | signature | **CONFIRMED** | fam0 ep57 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.114 post=0.033 ratio=3.43 |
| FL-P186 | signature | **CONFIRMED** | fam2 ep38 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.029 post=0.000 ratio=28571428.57 |
| FL-P187 | signature | **REGISTERED** | fam1 ep46 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d |  |

