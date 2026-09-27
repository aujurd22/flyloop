# flyloop status — 2026-09-27 11:43:43

- cycle **55173** / 120000，elapsed **10.00 h** / 10 h，memory mode **http**，poet device **cuda** (updates=27586)
- end condition: STOP file，RAM avail 15.8 GB

## rolling error (window=100)
- **seq**: n=55173, err100=0.81
- **fact**: n=27587, err100=0.08
- **puzzle**: n=27586, err100=0.3

## counts
- writes=20977 (fact 1931, pairs 13989, noise 2758), rejected-dedup=0, recalls=55173
- rule discoveries = **115**
- puzzle prediction methods: {'cold': 7310, 'guess': 210, 'fit': 19951, 'rule': 115}
- recall hit: fact 27518/27587, puzzle 0/0
- flymemory: `entries=20977`

## drift response
- total drift events observed: 2450, events seen in log: 2450
- **fact**: 2122/2122 recovered, median 0 cycles
- **seq**: 100/109 recovered, median 0 cycles
- **puzzle**: 199/206 recovered, median 0 cycles

## error by 1000-cycle bins
- seq: 0k:0.746 | 1k:0.781 | 2k:0.775 | 3k:0.759 | 4k:0.721 | 5k:0.759 | 6k:0.745 | 7k:0.749 | 8k:0.761 | 9k:0.742 | 10k:0.748 | 11k:0.788 | 12k:0.746 | 13k:0.729 | 14k:0.763 | 15k:0.737 | 16k:0.713 | 17k:0.747 | 18k:0.718 | 19k:0.72 | 20k:0.755 | 21k:0.721 | 22k:0.745 | 23k:0.771 | 24k:0.764 | 25k:0.75 | 26k:0.794 | 27k:0.762 | 28k:0.701 | 29k:0.789 | 30k:0.737 | 31k:0.722 | 32k:0.797 | 33k:0.731 | 34k:0.749 | 35k:0.793 | 36k:0.718 | 37k:0.735 | 38k:0.76 | 39k:0.763 | 40k:0.719 | 41k:0.763 | 42k:0.737 | 43k:0.718 | 44k:0.761 | 45k:0.725 | 46k:0.725 | 47k:0.758 | 48k:0.728 | 49k:0.713 | 50k:0.783 | 51k:0.725 | 52k:0.73 | 53k:0.752 | 54k:0.729 | 55k:0.873
- fact: 0k:0.14 | 1k:0.108 | 2k:0.07 | 3k:0.066 | 4k:0.062 | 5k:0.072 | 6k:0.066 | 7k:0.066 | 8k:0.076 | 9k:0.064 | 10k:0.068 | 11k:0.074 | 12k:0.066 | 13k:0.066 | 14k:0.082 | 15k:0.06 | 16k:0.066 | 17k:0.072 | 18k:0.066 | 19k:0.068 | 20k:0.078 | 21k:0.062 | 22k:0.064 | 23k:0.072 | 24k:0.074 | 25k:0.064 | 26k:0.07 | 27k:0.062 | 28k:0.074 | 29k:0.07 | 30k:0.068 | 31k:0.07 | 32k:0.064 | 33k:0.062 | 34k:0.066 | 35k:0.068 | 36k:0.066 | 37k:0.064 | 38k:0.07 | 39k:0.068 | 40k:0.078 | 41k:0.07 | 42k:0.064 | 43k:0.064 | 44k:0.078 | 45k:0.058 | 46k:0.06 | 47k:0.072 | 48k:0.074 | 49k:0.074 | 50k:0.064 | 51k:0.064 | 52k:0.06 | 53k:0.074 | 54k:0.056 | 55k:0.103
- puzzle: 0k:0.052 | 1k:0.12 | 2k:0.118 | 3k:0.128 | 4k:0.12 | 5k:0.204 | 6k:0.214 | 7k:0.288 | 8k:0.256 | 9k:0.26 | 10k:0.236 | 11k:0.296 | 12k:0.338 | 13k:0.326 | 14k:0.34 | 15k:0.348 | 16k:0.29 | 17k:0.36 | 18k:0.306 | 19k:0.29 | 20k:0.31 | 21k:0.338 | 22k:0.252 | 23k:0.22 | 24k:0.226 | 25k:0.256 | 26k:0.222 | 27k:0.24 | 28k:0.23 | 29k:0.248 | 30k:0.2 | 31k:0.246 | 32k:0.284 | 33k:0.266 | 34k:0.188 | 35k:0.258 | 36k:0.262 | 37k:0.252 | 38k:0.268 | 39k:0.274 | 40k:0.29 | 41k:0.264 | 42k:0.266 | 43k:0.312 | 44k:0.348 | 45k:0.336 | 46k:0.34 | 47k:0.398 | 48k:0.388 | 49k:0.364 | 50k:0.322 | 51k:0.348 | 52k:0.34 | 53k:0.368 | 54k:0.332 | 55k:0.337

## insights (115)
- c40840 fam=0 ep=51 rule `y=(10x+3) mod 13` evidence=[]
- c40852 fam=2 ep=34 rule `y=(4x+7) mod 13` evidence=[]
- c41640 fam=0 ep=52 rule `y=(10x+4) mod 13` evidence=[]
- c42044 fam=2 ep=35 rule `y=(11x+4) mod 13` evidence=[]
- c42440 fam=0 ep=53 rule `y=(9x+2) mod 13` evidence=[]
- c43244 fam=2 ep=36 rule `y=(10x+7) mod 13` evidence=[]
- c43296 fam=0 ep=54 rule `y=(6x+10) mod 13` evidence=[]
- c44040 fam=0 ep=55 rule `y=(3x+4) mod 13` evidence=[]
- c44484 fam=2 ep=37 rule `y=(3x+8) mod 13` evidence=[]
- c44888 fam=0 ep=56 rule `y=(11x+9) mod 13` evidence=[]
- c45640 fam=0 ep=57 rule `y=(6x+4) mod 13` evidence=[]
- c45644 fam=2 ep=38 rule `y=(8x+0) mod 13` evidence=[]
- c46776 fam=0 ep=58 rule `y=(8x+7) mod 13` evidence=[]
- c46844 fam=2 ep=39 rule `y=(1x+2) mod 13` evidence=[]
- c47264 fam=0 ep=59 rule `y=(1x+10) mod 13` evidence=[]
- c48048 fam=0 ep=60 rule `y=(5x+1) mod 13` evidence=[]
- c48052 fam=2 ep=40 rule `y=(6x+4) mod 13` evidence=[]
- c48848 fam=0 ep=61 rule `y=(8x+11) mod 13` evidence=[]
- c49580 fam=2 ep=41 rule `y=(5x+3) mod 13` evidence=[]
- c49704 fam=0 ep=62 rule `y=(12x+12) mod 13` evidence=[]
- c50444 fam=2 ep=42 rule `y=(4x+11) mod 13` evidence=[]
- c50592 fam=0 ep=63 rule `y=(5x+9) mod 13` evidence=[]
- c51288 fam=0 ep=64 rule `y=(11x+8) mod 13` evidence=[]
- c51644 fam=2 ep=43 rule `y=(5x+5) mod 13` evidence=[]
- c52040 fam=0 ep=65 rule `y=(6x+0) mod 13` evidence=[]
- c52844 fam=2 ep=44 rule `y=(7x+0) mod 13` evidence=[]
- c52864 fam=0 ep=66 rule `y=(7x+1) mod 13` evidence=[]
- c53640 fam=0 ep=67 rule `y=(9x+0) mod 13` evidence=[]
- c54044 fam=2 ep=45 rule `y=(8x+1) mod 13` evidence=[]
- c54440 fam=0 ep=68 rule `y=(9x+8) mod 13` evidence=[]

- world drift expectation: {'fact_rotations': 2097, 'puz_rotations': 207, 'seq_shifts': 110, 'shocks': 36}
## prediction ledger
| id | kind | status | claim | evidence |
|---|---|---|---|---|
| FL-P001 | run | **REFUTED** | P1: >=70% of fact-lane drift events spike: post_max rolling err >= max(pre+0.10, 0.25) | 0/2122 spiked, frac=0.00 |
| FL-P002 | run | **CONFIRMED** | P2: distinct rule discoveries (family x epoch) >= 8 over the run | discoveries=115 |
| FL-P003 | run | **REFUTED** | P3: >=60% of adjudicated restructuring-signature entries are CONFIRMED | 37/115 confirmed |
| FL-P004 | run | **CONFIRMED** | P4: >=70% of seq regime shifts recover (rolling err <= pre+0.05) within 200 cycles | 97/109 recovered<=200c |
| FL-P005 | run | **CONFIRMED** | P5: sandbox memory ends with 2000 <= entries <= 40000 | entries=20977 |
| FL-P006 | signature | **CONFIRMED** | fam2 ep0 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.364 post=0.000 ratio=363636363.64 |
| FL-P007 | signature | **CONFIRMED** | fam0 ep0 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.286 post=0.000 ratio=285714285.71 |
| FL-P008 | signature | **CONFIRMED** | fam0 ep1 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P009 | signature | **CONFIRMED** | fam2 ep1 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P010 | signature | **CONFIRMED** | fam0 ep2 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P011 | signature | **CONFIRMED** | fam2 ep2 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.229 post=0.000 ratio=228571428.57 |
| FL-P012 | signature | **CONFIRMED** | fam0 ep3 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.229 post=0.033 ratio=6.86 |
| FL-P013 | signature | **REFUTED** | fam0 ep4 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.057 post=0.167 ratio=0.34 |
| FL-P014 | signature | **CONFIRMED** | fam2 ep3 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.143 post=0.000 ratio=142857142.86 |
| FL-P015 | signature | **CONFIRMED** | fam0 ep5 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.086 post=0.000 ratio=85714285.71 |
| FL-P016 | signature | **REFUTED** | fam2 ep4 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.200 post=0.200 ratio=1.00 |
| FL-P017 | signature | **CONFIRMED** | fam0 ep6 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.171 post=0.067 ratio=2.57 |
| FL-P018 | signature | **CONFIRMED** | fam0 ep7 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.143 post=0.033 ratio=4.29 |
| FL-P019 | signature | **CONFIRMED** | fam2 ep5 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.371 post=0.000 ratio=371428571.43 |
| FL-P020 | signature | **REFUTED** | fam0 ep8 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.143 post=0.267 ratio=0.54 |
| FL-P021 | signature | **REFUTED** | fam2 ep6 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.229 post=0.333 ratio=0.69 |
| FL-P022 | signature | **REFUTED** | fam0 ep9 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.171 post=0.433 ratio=0.40 |
| FL-P023 | signature | **REFUTED** | fam0 ep10 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.486 post=0.400 ratio=1.21 |
| FL-P024 | signature | **REFUTED** | fam2 ep7 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.257 post=0.300 ratio=0.86 |
| FL-P025 | signature | **CONFIRMED** | fam0 ep11 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.033 ratio=4.29 |
| FL-P026 | signature | **CONFIRMED** | fam0 ep12 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.100 ratio=1.71 |
| FL-P027 | signature | **CONFIRMED** | fam2 ep8 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.171 post=0.100 ratio=1.71 |
| FL-P028 | signature | **REFUTED** | fam0 ep13 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.400 ratio=0.71 |
| FL-P029 | signature | **REFUTED** | fam2 ep9 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d] | pre=0.171 post=0.433 ratio=0.40 |
| FL-P030 | signature | **REFUTED** | fam0 ep14 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.267 ratio=1.39 |
| FL-P031 | signature | **CONFIRMED** | fam2 ep10 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.167 ratio=1.89 |
| FL-P032 | signature | **REFUTED** | fam0 ep15 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.300 ratio=0.48 |
| FL-P033 | signature | **REFUTED** | fam0 ep16 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.367 ratio=1.01 |
| FL-P034 | signature | **REFUTED** | fam2 ep11 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.200 post=0.233 ratio=0.86 |
| FL-P035 | signature | **REFUTED** | fam0 ep17 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.333 ratio=0.94 |
| FL-P036 | signature | **REFUTED** | fam0 ep18 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.467 ratio=0.61 |
| FL-P037 | signature | **REFUTED** | fam2 ep12 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.257 post=0.500 ratio=0.51 |
| FL-P038 | signature | **REFUTED** | fam0 ep19 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.367 ratio=0.78 |
| FL-P039 | signature | **REFUTED** | fam2 ep13 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.333 ratio=1.03 |
| FL-P040 | signature | **REFUTED** | fam0 ep20 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.233 ratio=1.22 |
| FL-P041 | signature | **CONFIRMED** | fam0 ep21 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.100 ratio=2.86 |
| FL-P042 | signature | **REFUTED** | fam2 ep14 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.167 ratio=1.37 |
| FL-P043 | signature | **REFUTED** | fam0 ep22 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.267 ratio=1.07 |
| FL-P044 | signature | **CONFIRMED** | fam2 ep15 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.133 ratio=2.79 |
| FL-P045 | signature | **REFUTED** | fam0 ep23 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.433 ratio=0.40 |
| FL-P046 | signature | **REFUTED** | fam2 ep16 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.367 ratio=0.78 |
| FL-P047 | signature | **REFUTED** | fam0 ep24 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.367 ratio=0.62 |
| FL-P048 | signature | **REFUTED** | fam0 ep25 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.433 ratio=0.86 |
| FL-P049 | signature | **REFUTED** | fam2 ep17 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.233 ratio=1.35 |
| FL-P050 | signature | **REFUTED** | fam0 ep26 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.267 ratio=1.18 |
| FL-P051 | signature | **REFUTED** | fam0 ep27 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.333 ratio=0.51 |
| FL-P052 | signature | **REFUTED** | fam2 ep18 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.367 ratio=0.39 |
| FL-P053 | signature | **CONFIRMED** | fam0 ep28 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.100 ratio=2.29 |
| FL-P054 | signature | **REFUTED** | fam2 ep19 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.167 ratio=0.86 |
| FL-P055 | signature | **CONFIRMED** | fam0 ep29 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.257 post=0.100 ratio=2.57 |
| FL-P056 | signature | **REFUTED** | fam0 ep30 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.200 ratio=1.43 |
| FL-P057 | signature | **REFUTED** | fam2 ep20 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.233 ratio=0.98 |
| FL-P058 | signature | **REFUTED** | fam0 ep31 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.267 ratio=0.54 |
| FL-P059 | signature | **REFUTED** | fam2 ep21 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.400 post=0.267 ratio=1.50 |
| FL-P060 | signature | **REFUTED** | fam0 ep32 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.114 post=0.267 ratio=0.43 |
| FL-P061 | signature | **REFUTED** | fam0 ep33 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.133 ratio=1.07 |
| FL-P062 | signature | **REFUTED** | fam2 ep22 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.167 ratio=0.86 |
| FL-P063 | signature | **REFUTED** | fam0 ep34 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.400 post=0.267 ratio=1.50 |
| FL-P064 | signature | **REFUTED** | fam2 ep23 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.333 ratio=0.51 |
| FL-P065 | signature | **CONFIRMED** | fam0 ep35 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.000 ratio=285714285.71 |
| FL-P066 | signature | **CONFIRMED** | fam2 ep24 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.100 ratio=3.43 |
| FL-P067 | signature | **REFUTED** | fam0 ep36 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.267 ratio=0.64 |
| FL-P068 | signature | **CONFIRMED** | fam0 ep37 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.429 post=0.033 ratio=12.86 |
| FL-P069 | signature | **CONFIRMED** | fam2 ep25 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.067 ratio=2.57 |
| FL-P070 | signature | **REFUTED** | fam0 ep38 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.267 ratio=1.29 |
| FL-P071 | signature | **CONFIRMED** | fam0 ep39 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.000 ratio=314285714.29 |
| FL-P072 | signature | **CONFIRMED** | fam2 ep26 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.033 ratio=8.57 |
| FL-P073 | signature | **REFUTED** | fam0 ep40 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.233 ratio=1.59 |
| FL-P074 | signature | **CONFIRMED** | fam2 ep27 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.200 post=0.000 ratio=200000000.00 |
| FL-P075 | signature | **REFUTED** | fam0 ep41 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.333 ratio=1.03 |
| FL-P076 | signature | **REFUTED** | fam2 ep28 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.200 ratio=1.43 |
| FL-P077 | signature | **REFUTED** | fam0 ep42 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.200 post=0.200 ratio=1.00 |
| FL-P078 | signature | **REFUTED** | fam0 ep43 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.200 post=0.267 ratio=0.75 |
| FL-P079 | signature | **CONFIRMED** | fam2 ep29 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.100 ratio=2.86 |
| FL-P080 | signature | **CONFIRMED** | fam0 ep44 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.000 ratio=57142857.14 |
| FL-P081 | signature | **CONFIRMED** | fam0 ep45 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.167 ratio=1.89 |
| FL-P082 | signature | **REFUTED** | fam2 ep30 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.333 ratio=0.69 |
| FL-P083 | signature | **REFUTED** | fam0 ep46 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.367 ratio=0.47 |
| FL-P084 | signature | **REFUTED** | fam2 ep31 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.057 post=0.200 ratio=0.29 |
| FL-P085 | signature | **REFUTED** | fam0 ep47 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.300 ratio=0.76 |
| FL-P086 | signature | **CONFIRMED** | fam2 ep32 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.000 ratio=228571428.57 |
| FL-P087 | signature | **REFUTED** | fam0 ep48 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.100 ratio=1.43 |
| FL-P088 | signature | **REFUTED** | fam0 ep49 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.367 ratio=0.86 |
| FL-P089 | signature | **CONFIRMED** | fam2 ep33 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.400 post=0.067 ratio=6.00 |
| FL-P090 | signature | **REFUTED** | fam0 ep50 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.257 post=0.367 ratio=0.70 |
| FL-P091 | signature | **CONFIRMED** | fam0 ep51 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.033 ratio=9.43 |
| FL-P092 | signature | **CONFIRMED** | fam2 ep34 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.100 ratio=2.86 |
| FL-P093 | signature | **REFUTED** | fam0 ep52 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.233 ratio=1.47 |
| FL-P094 | signature | **REFUTED** | fam2 ep35 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.267 ratio=1.07 |
| FL-P095 | signature | **REFUTED** | fam0 ep53 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.233 ratio=1.59 |
| FL-P096 | signature | **CONFIRMED** | fam2 ep36 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.100 ratio=3.43 |
| FL-P097 | signature | **REFUTED** | fam0 ep54 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.267 ratio=0.54 |
| FL-P098 | signature | **REFUTED** | fam0 ep55 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.457 post=0.300 ratio=1.52 |
| FL-P099 | signature | **REFUTED** | fam2 ep37 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.300 ratio=1.14 |
| FL-P100 | signature | **REFUTED** | fam0 ep56 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.467 ratio=0.80 |
| FL-P101 | signature | **CONFIRMED** | fam0 ep57 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.257 post=0.067 ratio=3.86 |
| FL-P102 | signature | **CONFIRMED** | fam2 ep38 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.100 ratio=2.29 |
| FL-P103 | signature | **REFUTED** | fam0 ep58 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.167 ratio=1.03 |
| FL-P104 | signature | **REFUTED** | fam2 ep39 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.143 post=0.300 ratio=0.48 |
| FL-P105 | signature | **REFUTED** | fam0 ep59 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.400 post=0.433 ratio=0.92 |
| FL-P106 | signature | **REFUTED** | fam0 ep60 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.433 ratio=0.73 |
| FL-P107 | signature | **REFUTED** | fam2 ep40 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.286 post=0.467 ratio=0.61 |
| FL-P108 | signature | **REFUTED** | fam0 ep61 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.500 ratio=0.74 |
| FL-P109 | signature | **REFUTED** | fam2 ep41 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.429 post=0.467 ratio=0.92 |
| FL-P110 | signature | **REFUTED** | fam0 ep62 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.429 post=0.333 ratio=1.29 |
| FL-P111 | signature | **REFUTED** | fam2 ep42 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.229 post=0.233 ratio=0.98 |
| FL-P112 | signature | **REFUTED** | fam0 ep63 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.343 post=0.500 ratio=0.69 |
| FL-P113 | signature | **REFUTED** | fam0 ep64 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.400 post=0.400 ratio=1.00 |
| FL-P114 | signature | **REFUTED** | fam2 ep43 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.233 ratio=1.35 |
| FL-P115 | signature | **REFUTED** | fam0 ep65 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.171 post=0.433 ratio=0.40 |
| FL-P116 | signature | **REFUTED** | fam2 ep44 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.333 ratio=0.94 |
| FL-P117 | signature | **REFUTED** | fam0 ep66 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.200 post=0.433 ratio=0.46 |
| FL-P118 | signature | **REFUTED** | fam0 ep67 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.371 post=0.300 ratio=1.24 |
| FL-P119 | signature | **REFUTED** | fam2 ep45 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.400 post=0.467 ratio=0.86 |
| FL-P120 | signature | **REFUTED** | fam0 ep68 signature: rolling puzzle err over [d+10,d+70] <= 0.6 x rolling err over [d-70,d | pre=0.314 post=0.400 ratio=0.79 |

