"""Logon resume hook for an overnight run (registered under HKCU ...Run).

Reads `<repo>/resume_config.json`: {"run_dir": ..., "duration_h": ...}.
No-op once final_report.md exists; otherwise relaunches the supervisor, which
re-checks the fresh-heartbeat guard before spawning anything. The worker's
absolute deadline lives in deadline.json, so remaining time survives reboots.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flyloop import config as C  # noqa: E402

CFG = os.path.join(C.ROOT, "resume_config.json")


def main():
    if not os.path.exists(CFG):
        return
    with open(CFG, encoding="utf-8") as f:
        cfg = json.load(f)
    run_dir = cfg["run_dir"]
    if os.path.exists(os.path.join(run_dir, "final_report.md")):
        return
    subprocess.Popen(
        [C.PYTHON, "-m", "flyloop.supervisor", "--run-dir", run_dir,
         "--duration-h", str(cfg.get("duration_h", 5))],
        cwd=C.ROOT, creationflags=(0x08000000 | 0x00000008) if sys.platform == "win32" else 0,  # NO_WINDOW | DETACHED
        close_fds=True)


if __name__ == "__main__":
    main()
