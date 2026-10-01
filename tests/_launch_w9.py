"""V9 W9A wave sweep launcher: one flyloop line per WAVE_AMP value.

Usage: python tests/_launch_w9.py 0 6        (first pair)
       python tests/_launch_w9.py 2 4        (second pair, after first ends)

Arms FULL/MATCHED/EPISODIC, fixed policy, eps=0.15, 2h. World shift
control class (V9_DESIGN.md) -- never counted as self-improvement.
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


WAVES = [int(w) for w in sys.argv[1:]] or [0, 6]
ts = time.strftime("%Y%m%d_%H%M")

for W in WAVES:
    run_dir = os.path.join(C.ROOT, "runs", f"w9w{W}_{ts}")
    os.makedirs(run_dir, exist_ok=True)
    envs = {
        "FLYLOOP_PORT": str(free_port()),
        "FLYLOOP_PORT_MATCHED": str(free_port()),
        "FLYLOOP_PORT_EPI": str(free_port()),
        "FLYLOOP_NOISE_EPS": "0.15",
        "FLYLOOP_ARMS": "FULL,MATCHED,EPISODIC",
        "FLYLOOP_MATCH_MIN_FRAC": "0.6",
        "FLYLOOP_PREDSET": "V4",
        "FLYLOOP_WAVE_AMP": str(W),
    }
    # Preflight gate (W=0 uses the default seed regime; wave runs are world
    # shifts, not replications, so no FLYLOOP_REPLICATE_OF is declared).
    pf = subprocess.run([sys.executable, "-m", "tests.preflight",
                         "--arms", envs["FLYLOOP_ARMS"], "--mode", "single"],
                        cwd=C.ROOT, env={**os.environ, **envs},
                        capture_output=True, text=True)
    if pf.returncode != 0:
        print(pf.stdout, pf.stderr)
        print(f"PREFLIGHT FAILED for W={W} -- launch aborted")
        sys.exit(1)
    print(f"[W={W}] preflight ok")

    with open(os.path.join(C.ROOT, "resume_config.json"), "w") as f:
        json.dump({"run_dir": run_dir, "duration_h": 2.0}, f)
    lines = ["import os, sys"]
    for k, v in envs.items():
        lines.append(f"os.environ[{k!r}]={v!r}")
    lines.append(f"os.chdir(r'{C.ROOT}')")
    lines.append(f"sys.argv = ['supervisor', '--run-dir', r'{run_dir}', "
                 f"'--duration-h', '2.0']")
    lines.append("from flyloop.supervisor import main")
    lines.append("main()")
    lp = os.path.join(C.ROOT, f"_w9w{W}_launch.py")
    with open(lp, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    p = subprocess.Popen([C.PYTHON, lp], cwd=C.ROOT,
                         creationflags=0x08000000, close_fds=True)
    print(f"[W={W}] supervisor pid {p.pid} -> {run_dir}")
