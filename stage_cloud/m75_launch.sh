#!/bin/bash
# M7.5 adjudication on the 208-core node: DERIVE_EPISODES variant, 4 arms,
# two replicates (default RUNSEED + RUNSEED=7). Baseline = m73_retest
# (same SEED schedule, ran locally with the pre-fix derivation).
export FLYLOOP_PYTHONW=/root/miniconda3/bin/python
cd /root/autodl-tmp/flycloud
COMMON="FLYLOOP_NOISE_EPS=0.25 FLYLOOP_MATCH_MIN_FRAC=0.6 FLYLOOP_PREDSET=V4 FLYLOOP_COMPOSITE=1 FLYLOOP_BOOK_CAP=2 FLYLOOP_DERIVE_EPISODES=1 FLYLOOP_MAX_CYCLES=30000"

env $COMMON FLYLOOP_PORTS=53011,53012,53013,53014 \
  FLYLOOP_PORT=53011 FLYLOOP_PORT_MATCHED=53012 FLYLOOP_PORT_EPI=53013 \
  FLYLOOP_ARMS=FULL-COMP,FULL,MATCHED,EPISODIC \
  setsid nohup /root/miniconda3/bin/python -m flyloop.supervisor \
    --run-dir /root/autodl-tmp/flycloud/runs/m75_ep_s0 --duration-h 1.0 \
    > m75_s0.log 2>&1 < /dev/null &
sleep 5
env $COMMON FLYLOOP_RUNSEED=7 FLYLOOP_PORTS=53021,53022,53023,53024 \
  FLYLOOP_PORT=53021 FLYLOOP_PORT_MATCHED=53022 FLYLOOP_PORT_EPI=53023 \
  FLYLOOP_ARMS=FULL-COMP,FULL,MATCHED,EPISODIC \
  setsid nohup /root/miniconda3/bin/python -m flyloop.supervisor \
    --run-dir /root/autodl-tmp/flycloud/runs/m75_ep_s7 --duration-h 1.0 \
    > m75_s7.log 2>&1 < /dev/null &
echo BOTH_M75_LAUNCHED
