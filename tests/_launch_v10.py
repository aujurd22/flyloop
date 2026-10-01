"""V10 launcher: composite world (periodicity + anomaly + composition),
three standard arms -- the user-direction-3 A/B/C closed loop (V10_DESIGN).
"""
import json, os, socket, subprocess, sys, time
sys.path.insert(0, r"D:\djr82\flyloop")
from flyloop import config as C

def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]

SMOKE = os.environ.get("V10_SMOKE", "0") == "1"
ts = time.strftime("%Y%m%d_%H%M")
tag = "v10smoke" if SMOKE else "v10"
run_dir = os.path.join(C.ROOT, "runs", f"{tag}_{ts}")
os.makedirs(run_dir, exist_ok=True)
ports = [free_port() for _ in range(3)]
envs = {
    "FLYLOOP_PORTS": ",".join(str(x) for x in ports),
    "FLYLOOP_PORT": str(ports[0]),
    "FLYLOOP_PORT_MATCHED": str(ports[1]),
    "FLYLOOP_PORT_EPI": str(ports[2]),
    "FLYLOOP_NOISE_EPS": "0.25",
    "FLYLOOP_ARMS": "FULL,MATCHED,EPISODIC",
    "FLYLOOP_MATCH_MIN_FRAC": "0.6",
    "FLYLOOP_PREDSET": "V4",
    "FLYLOOP_COMPOSITE": "1",
    "FLYLOOP_MAX_CYCLES": "800" if SMOKE else "30000",
}
pf = subprocess.run([sys.executable, "-m", "tests.preflight",
                     "--arms", envs["FLYLOOP_ARMS"], "--mode", "single"],
                    cwd=C.ROOT, env={**os.environ, **envs},
                    capture_output=True, text=True)
print(pf.stdout)
if pf.returncode != 0:
    print(pf.stderr); print("PREFLIGHT FAILED"); sys.exit(1)
with open(os.path.join(C.ROOT, "resume_config.json"), "w") as f:
    json.dump({"run_dir": run_dir, "duration_h": 0.2 if SMOKE else 2.0}, f)
lines = ["import os, sys"]
for k, v in envs.items():
    lines.append(f"os.environ[{k!r}]={v!r}")
lines.append(f"os.chdir(r'{C.ROOT}')")
lines.append(f"sys.argv = ['supervisor', '--run-dir', r'{run_dir}', "
             f"'--duration-h', '{0.2 if SMOKE else 2.0}']")
lines.append("from flyloop.supervisor import main")
lines.append("main()")
lp = os.path.join(C.ROOT, f"_{tag}_launch.py")
open(lp, "w", encoding="utf-8").write("\n".join(lines))
logf = open(os.path.join(run_dir, "launcher.log"), "w")
p = subprocess.Popen([C.PYTHON, lp], cwd=C.ROOT, creationflags=0x08000000,
                     stdout=logf, stderr=logf)
print(f"[{tag}] supervisor pid {p.pid} -> {run_dir}")
