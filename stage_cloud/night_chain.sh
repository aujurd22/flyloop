#!/bin/bash
# Night chain on the 208-core box (capped ~12 threads, nice'd -- flypoet
# owns the GPU and must not slow down):
#   1. M7.7 run (EPUSH_EARLY identification-latency lever + freshness gate),
#      4 arms, 1h, composite CAP=2 -- same schedule as m73_retest baseline.
#   2. MBNA k-WTA sweep at frac=0.1: k=0.15 and k=0.25 (k=0.05 = full,
#      already done: acc 0.2276). Tests flypoet U-curve (L9) at LLM scale.
export FLYLOOP_PYTHONW=/root/miniconda3/bin/python
cd /root/autodl-tmp/flycloud

echo "=== 1: M7.7 run"
env FLYLOOP_PORTS=53041,53042,53043,53044 \
  FLYLOOP_PORT=53041 FLYLOOP_PORT_MATCHED=53042 FLYLOOP_PORT_EPI=53043 \
  FLYLOOP_NOISE_EPS=0.25 FLYLOOP_MATCH_MIN_FRAC=0.6 FLYLOOP_PREDSET=V4 \
  FLYLOOP_COMPOSITE=1 FLYLOOP_BOOK_CAP=2 FLYLOOP_DERIVE_EPISODES=1 \
  FLYLOOP_EPUSH_EARLY=1 FLYLOOP_MAX_CYCLES=30000 \
  FLYLOOP_ARMS=FULL-COMP,FULL,MATCHED,EPISODIC \
  setsid nohup nice -n 10 /root/miniconda3/bin/python -m flyloop.supervisor \
    --run-dir /root/autodl-tmp/flycloud/runs/m77_epush_s0 --duration-h 1.0 \
    > m77_s0.log 2>&1 < /dev/null &
# wait for the run to end (worker writes DONE into supervisor log at end)
sleep 60
while pgrep -f "flyloop.supervisor.*m77_epush_s0" > /dev/null; do sleep 60; done
echo "=== 2: MBNA k-WTA sweep"
export MBNA_KFRAC=0.15 MBNA_OUT=/root/autodl-tmp/mbn/mbna_k015.json
nice -n 10 /root/miniconda3/bin/python /root/autodl-tmp/mbn/mbna_v2.py 12 \
  > /root/autodl-tmp/mbn/mbna_k015.log 2>&1
export MBNA_KFRAC=0.25 MBNA_OUT=/root/autodl-tmp/mbn/mbna_k025.json
nice -n 10 /root/miniconda3/bin/python /root/autodl-tmp/mbn/mbna_v2.py 12 \
  > /root/autodl-tmp/mbn/mbna_k025.log 2>&1
echo "=== CHAIN COMPLETE"
