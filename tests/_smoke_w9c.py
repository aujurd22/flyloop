"""W9C smoke: real supervisor, FULL-RES single arm, 600-cycle horizon."""
import json, os, socket, subprocess, sys, time
sys.path.insert(0, r"D:\djr82\flyloop")
from flyloop import config as C

def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

run_dir = os.path.join(C.ROOT, "runs", "_smoke_w9c")
os.makedirs(run_dir, exist_ok=True)
envs = {
    "FLYLOOP_PORT": str(free_port()),
    "FLYLOOP_PORT_MATCHED": str(free_port()),
    "FLYLOOP_PORT_EPI": str(free_port()),
    "FLYLOOP_NOISE_EPS": "0.15",
    "FLYLOOP_ARMS": "FULL-RES",
    "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_PREDSET": "V4",
    "FLYLOOP_WAVE_AMP": "4",
    "FLYLOOP_MAX_CYCLES": "1500",
    "FLYLOOP_PACING_MS": "1",
}
with open(os.path.join(C.ROOT, "resume_config.json"), "w") as f:
    json.dump({"run_dir": run_dir, "duration_h": 0.35}, f)
lines = ["import os, sys"]
for k, v in envs.items():
    lines.append(f"os.environ[{k!r}]={v!r}")
lines.append(f"os.chdir(r'{C.ROOT}')")
lines.append(f"sys.argv = ['supervisor', '--run-dir', r'{run_dir}', '--duration-h', '0.15']")
lines.append("from flyloop.supervisor import main")
lines.append("main()")
lp = os.path.join(C.ROOT, "_smokew9c_launch.py")
open(lp, "w", encoding="utf-8").write("\n".join(lines))
logf = open(os.path.join(run_dir, 'launcher.log'), 'w')
p = subprocess.Popen([C.PYTHON, lp], cwd=C.ROOT, creationflags=0x08000000,
                     stdout=logf, stderr=logf)
print('smoke supervisor pid', p.pid, '->', run_dir)
