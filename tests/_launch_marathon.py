import json
import os
import subprocess
import sys
import time

sys.path.insert(0, r"D:\djr82\flyloop")
from flyloop import config as C


def free_ports(n):
    import socket
    ports = []
    for _ in range(n):
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            ports.append(s.getsockname()[1])
    return ports


def launch(tag, run_dir, ports, envs, duration_h, max_cycles):
    with open(os.path.join(C.ROOT, "resume_config.json"), "w") as f:
        json.dump({"run_dir": run_dir, "duration_h": duration_h}, f)
    print(f"resume hook [{tag}] ->", run_dir)
    all_env = {
        "FLYLOOP_PORT": str(ports[0]),
        "FLYLOOP_PORT_MATCHED": str(ports[1]),
        "FLYLOOP_PORT_EPI": str(ports[2]),
        "FLYLOOP_MARATHON": "1",
        "FLYLOOP_MAX_CYCLES": str(max_cycles),
    }
    all_env.update(envs)
    lines = ["import os, sys"]
    for k, v in all_env.items():
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
DURATION = 12.5
MAX_CYCLES = 30000
COMMON = {"FLYLOOP_MATCH_MIN_FRAC": "0.6", "FLYLOOP_BOOK_CAP": "5",
          "FLYLOOP_BOOK_MODE": "single", "FLYLOOP_PREDSET": "V4"}

# Run A: Frozen — fixed policy, no adaptation
ports_a = free_ports(3)
launch("frozen", os.path.join(C.ROOT, "runs", f"marathon_frozen_{ts}"),
       ports_a, {**COMMON, "FLYLOOP_ARMS": "FULL,EPISODIC"}, DURATION, MAX_CYCLES)

# Run B: Adaptive — adaptive read policy inherited from G3
ports_b = free_ports(3)
launch("adaptive", os.path.join(C.ROOT, "runs", f"marathon_adaptive_{ts}"),
       ports_b, {**COMMON, "FLYLOOP_ARMS": "FULL-ADAPT,EPISODIC"}, DURATION, MAX_CYCLES)

# Run C: RSI-Loop — same as B but the selector can propose mutations at era boundaries
ports_c = free_ports(3)
launch("rsi", os.path.join(C.ROOT, "runs", f"marathon_rsi_{ts}"),
       ports_c, {**COMMON, "FLYLOOP_ARMS": "FULL-ADAPT,EPISODIC"}, DURATION, MAX_CYCLES)
