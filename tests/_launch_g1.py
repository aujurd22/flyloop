import json
import os
import subprocess
import sys
import time

sys.path.insert(0, r"D:\djr82\flyloop")
from flyloop import config as C

run_dir = os.path.join(C.ROOT, "runs", "rsi0_g1_" + time.strftime("%Y%m%d_%H%M"))
os.makedirs(run_dir, exist_ok=True)
with open(os.path.join(C.ROOT, "resume_config.json"), "w") as f:
    json.dump({"run_dir": run_dir, "duration_h": 2.0}, f)
print("resume hook ->", run_dir)

# RSI-0 G1: g0 config (tolerant 0.6, eps 0.25) + M1 (BOOK_CAP 5 -> 13)
launcher = (
    "import os, sys\n"
    "os.environ['FLYLOOP_NOISE_EPS']='0.25'\n"
    "os.environ['FLYLOOP_ARMS']='FULL,MATCHED,EPISODIC'\n"
    "os.environ['FLYLOOP_MATCH_MIN_FRAC']='0.6'\n"
    "os.environ['FLYLOOP_BOOK_CAP']='13'\n"
    "os.environ['FLYLOOP_PREDSET']='RSI0'\n"
    "os.chdir(r'" + C.ROOT + "')\n"
    "sys.argv = ['supervisor', '--run-dir', r'" + run_dir + "', "
    "'--duration-h', '2']\n"
    "from flyloop.supervisor import main\n"
    "main()\n")
lp = os.path.join(C.ROOT, "_g1_launch.py")
with open(lp, "w", encoding="utf-8") as f:
    f.write(launcher)
p = subprocess.Popen([C.PYTHON, lp], cwd=C.ROOT,
                     creationflags=0x08000000, close_fds=True)
print("supervisor pid", p.pid)
