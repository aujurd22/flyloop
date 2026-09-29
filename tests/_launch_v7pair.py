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


def free_port():
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


ts = time.strftime("%Y%m%d_%H%M")
# G2 relaunch (fixed: min_frac param, index desync guard, force_new perrule)
g2_dir = os.path.join(C.ROOT, "runs", f"rsi0_g2_{ts}")
os.makedirs(g2_dir, exist_ok=True)
launch("g2", g2_dir, {
    "FLYLOOP_PORT": str(free_port()),
    "FLYLOOP_PORT_MATCHED": str(free_port()),
    "FLYLOOP_PORT_EPI": str(free_port()),
    "FLYLOOP_NOISE_EPS": "0.25",
    "FLYLOOP_ARMS": "FULL,MATCHED,EPISODIC",
    "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_BOOK_CAP": "13",
    "FLYLOOP_BOOK_MODE": "perrule",
    "FLYLOOP_PREDSET": "RSI0G2",
}, 2.5)

# V7C relaunch (write-depth sign resolution, exact matcher, eps=0.25)
v7c_dir = os.path.join(C.ROOT, "runs", f"v7c_{ts}")
os.makedirs(v7c_dir, exist_ok=True)
launch("v7c", v7c_dir, {
    "FLYLOOP_PORT": str(free_port()),
    "FLYLOOP_PORT_MATCHED": str(free_port()),
    "FLYLOOP_PORT_EPI": str(free_port()),
    "FLYLOOP_NOISE_EPS": "0.25",
    "FLYLOOP_ARMS": "FULL,FULL-RAW,EPISODIC",
    "FLYLOOP_PREDSET": "V7C",
}, 2.5)
