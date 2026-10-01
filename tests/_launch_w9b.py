"""W9B launcher: the tolerance-decoupling recovery test (registered in
findings/v9_w9a/FINDINGS.md).

World: W=4, eps=0.15 — bit-identical to the W9A W=4 run (default run seed,
same schedule AND same realizations). Arms: FULL (control; should replay
the W9A W=4 FULL trajectory bit-for-bit — a free determinism harness check),
MATCHED-EXACT (the W9B mutation: archive matcher at tol=0 — its stored pairs
stay exactly valid in the wave world, so it needs no band), EPISODIC.

Prediction: if the W9A plateau was matcher self-inflicted, MATCHED-EXACT
beats both the old MATCHED (~10.42) and FULL (~10.58) by a wide margin.
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, r"D:\djr82\flyloop")
from flyloop import config as C


def free_port():
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


ts = time.strftime("%Y%m%d_%H%M")
run_dir = os.path.join(C.ROOT, "runs", f"w9b_20261001_{ts.split('_')[1]}")
os.makedirs(run_dir, exist_ok=True)
envs = {
    "FLYLOOP_PORT": str(free_port()),
    "FLYLOOP_PORT_MATCHED": str(free_port()),
    "FLYLOOP_PORT_EPI": str(free_port()),
    "FLYLOOP_NOISE_EPS": "0.15",
    "FLYLOOP_ARMS": "FULL,MATCHED-EXACT,EPISODIC",
    "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_PREDSET": "V4",
    "FLYLOOP_WAVE_AMP": "4",
}
pf = subprocess.run([sys.executable, "-m", "tests.preflight",
                     "--arms", envs["FLYLOOP_ARMS"], "--mode", "single"],
                    cwd=C.ROOT, env={**os.environ, **envs},
                    capture_output=True, text=True)
print(pf.stdout)
if pf.returncode != 0:
    print(pf.stderr)
    print("PREFLIGHT FAILED -- launch aborted")
    sys.exit(1)

with open(os.path.join(C.ROOT, "resume_config.json"), "w") as f:
    json.dump({"run_dir": run_dir, "duration_h": 2.0}, f)
print("resume hook [w9b] ->", run_dir)
lines = ["import os, sys"]
for k, v in envs.items():
    lines.append(f"os.environ[{k!r}]={v!r}")
lines.append(f"os.chdir(r'{C.ROOT}')")
lines.append(f"sys.argv = ['supervisor', '--run-dir', r'{run_dir}', "
             f"'--duration-h', '2.0']")
lines.append("from flyloop.supervisor import main")
lines.append("main()")
lp = os.path.join(C.ROOT, "_w9b_launch.py")
with open(lp, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
p = subprocess.Popen([C.PYTHON, lp], cwd=C.ROOT,
                     creationflags=0x08000000, close_fds=True)
print(f"[w9b] supervisor pid {p.pid} -> {run_dir}")
