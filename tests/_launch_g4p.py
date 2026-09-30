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


# --- G4prime: TRUE replication of G3 (adaptive read policy) ---
# G4 was retracted: same-config re-runs replay the parent bit-for-bit without
# a run seed. This launch carries FLYLOOP_RUNSEED (fresh realizations, same
# schedule) and FLYLOOP_REPLICATE_OF (preflight #5 enforces the seed).
ts = time.strftime("%Y%m%d_%H%M")
g4p_dir = os.path.join(C.ROOT, "runs", f"rsi0_g4p_{ts}")
os.makedirs(g4p_dir, exist_ok=True)

envs = {
    "FLYLOOP_PORT": str(free_port()),
    "FLYLOOP_PORT_MATCHED": str(free_port()),
    "FLYLOOP_PORT_EPI": str(free_port()),
    "FLYLOOP_NOISE_EPS": "0.25",
    "FLYLOOP_ARMS": "FULL-ADAPT,MATCHED,EPISODIC",
    "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_PREDSET": "RSI0",
    "FLYLOOP_RUNSEED": "20260930",
    "FLYLOOP_REPLICATE_OF": "rsi0_g3_20260930_0808",
}

# Preflight gate (abort before burning the run)
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
    json.dump({"run_dir": g4p_dir, "duration_h": 2.0}, f)
print("resume hook [g4p] ->", g4p_dir)
lines = ["import os, sys"]
for k, v in envs.items():
    lines.append(f"os.environ[{k!r}]={v!r}")
lines.append(f"os.chdir(r'{C.ROOT}')")
lines.append(f"sys.argv = ['supervisor', '--run-dir', r'{g4p_dir}', "
             f"'--duration-h', '2.0']")
lines.append("from flyloop.supervisor import main")
lines.append("main()")
lp = os.path.join(C.ROOT, "_g4p_launch.py")
with open(lp, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
p = subprocess.Popen([C.PYTHON, lp], cwd=C.ROOT,
                     creationflags=0x08000000, close_fds=True)
print(f"[g4p] supervisor pid {p.pid}, RUNSEED=20260930")
