#!/bin/bash
# Cloud launch for the selflearner + M6-second-realization (westd box).
# Usage: bash cloud_launch.sh   (as root, from /root)
set -e
export FLYLOOP_PYTHON=/usr/bin/python3

echo "=== [1/3] selflearner overnight (60 rounds, effort=low)"
mkdir -p /root/autodl-tmp/selflearner
# expects /root/autodl-tmp/sl_env.tar uploaded; extract into place
if [ -f /root/autodl-tmp/sl_env.tar ]; then
  mkdir -p /root/autodl-tmp/mathlib4
  tar -xf /root/autodl-tmp/sl_env.tar -C /root/autodl-tmp
  echo "env extracted"
fi
cd /root/autodl-tmp/selflearner || { git clone https://github.com/aujurd22/selflearner.git /root/autodl-tmp/selflearner; cd /root/autodl-tmp/selflearner; }
ln -sf /root/autodl-tmp/mathlib4 /root/autodl-tmp/selflearner/mathlib4
ln -sf /root/autodl-tmp/mathlib.db /root/autodl-tmp/selflearner/mathlib.db
ln -sf /root/autodl-tmp/vectors.npz /root/autodl-tmp/selflearner/vectors.npz
pip install -q sentence-transformers 2>&1 | tail -1 || true

echo "=== [2/3] flyloop M6 second realization (RUNSEED=20261006)"
mkdir -p /root/autodl-tmp/flyloop
cd /root/autodl-tmp/flyloop
if [ ! -d flyloop ]; then
  git clone https://github.com/aujurd22/flyloop.git .
fi
git fetch origin && git reset --hard origin/master -q

echo "=== [3/3] launch (detached)"
cd /root/autodl-tmp/flyloop
env FLYLOOP_COMPOSITE=1 FLYLOOP_BOOK_CAP=2 FLYLOOP_NOISE_EPS=0.25 \
  FLYLOOP_MATCH_MIN_FRAC=0.6 FLYLOOP_PREDSET=V4 FLYLOOP_ARMS=FULL-RES \
  FLYLOOP_MAX_CYCLES=30000 FLYLOOP_RUNSEED=20261006 \
  FLYLOOP_PORTS=53241,53242,53243,53244 \
  setsid nohup $FLYLOOP_PYTHON -m flyloop.supervisor \
  --run-dir runs/m6_m5_base_s2 --duration-h 8.0 \
  > m6_m5_base_s2.log 2>&1 < /dev/null &
env FLYLOOP_COMPOSITE=1 FLYLOOP_BOOK_CAP=2 FLYLOOP_NOISE_EPS=0.25 \
  FLYLOOP_MATCH_MIN_FRAC=0.6 FLYLOOP_PREDSET=V4 FLYLOOP_ARMS=FULL-RES \
  FLYLOOP_MAX_CYCLES=30000 FLYLOOP_RUNSEED=20261006 \
  FLYLOOP_DELTA_RETRIEVE=1 FLYLOOP_PORTS=53251,53252,53253,53254 \
  setsid nohup $FLYLOOP_PYTHON -m flyloop.supervisor \
  --run-dir runs/m6_delta_s2 --duration-h 8.0 \
  > m6_delta_s2.log 2>&1 < /dev/null &
sleep 45
tail -2 m6_m5_base_s2.log m6_delta_s2.log
echo LAUNCH_DONE
