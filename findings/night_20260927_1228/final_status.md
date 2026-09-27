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

