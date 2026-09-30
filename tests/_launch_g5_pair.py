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


def launch(tag, run_dir, envs, duration_h):
    with open(os.path.join(C.ROOT, "resume_config.json"), "w") as f:
        json.dump({"run_dir": run_dir, "duration_h": duration_h}, f)
    print(f"resume hook [{tag}] ->", run_dir)
    lines = ["import os, sys"]
    for k, v in envs.items():
        lines.append(f"os.environ[{k!r}]={v!r}")
    lines.append(f"os.chdir(r'{C.ROOT}')")
    lines.append(f"sys.argv = ['supervisor', '--run-dir', r'{run_dir}', "
                 f"'--duration-h', '{duration_h}']")
    lines.append("from flyloop.supervisor import main")
    lines.append("main()")
    lp = os.path.join(C.ROOT, f"_{tag}_launch.py")
    with open(lp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    p = subprocess.Popen([C.PYTHON, lp], cwd=C.ROOT,
                         creationflags=0x08000000, close_fds=True)
    print(f"[{tag}] supervisor pid", p.pid)


ts = time.strftime("%Y%m%d_%H%M")
# --- G5: adaptive read policy inherited (parent = G3 accepted) ---
# The selector picks from the menu; G3 accepted adaptive, so G5 inherits it
# and tests whether the improvement persists in a fresh run.
g5_dir = os.path.join(C.ROOT, "runs", f"rsi0_g5_{ts}")
os.makedirs(g5_dir, exist_ok=True)
launch("g5", g5_dir, {
    "FLYLOOP_PORT": str(free_port()),
    "FLYLOOP_PORT_MATCHED": str(free_port()),
    "FLYLOOP_PORT_EPI": str(free_port()),
    "FLYLOOP_NOISE_EPS": "0.25",
    "FLYLOOP_ARMS": "FULL-ADAPT,MATCHED,EPISODIC",
    "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_PREDSET": "RSI0",
}, 2.0)

# --- eps=0.25 matched re-run (for dose-response curve completeness) ---
e25_dir = os.path.join(C.ROOT, "runs", f"v8_eps025_{ts}")
os.makedirs(e25_dir, exist_ok=True)
launch("e25", e25_dir, {
    "FLYLOOP_PORT": str(free_port()),
    "FLYLOOP_PORT_MATCHED": str(free_port()),
    "FLYLOOP_PORT_EPI": str(free_port()),
    "FLYLOOP_NOISE_EPS": "0.25",
    "FLYLOOP_ARMS": "FULL,MATCHED,EPISODIC",
    "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_PREDSET": "V4",
}, 2.0)
