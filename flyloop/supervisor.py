"""Overnight supervisor: keeps the sandbox service up, restarts the worker on
crash (exponential backoff), enforces the RAM red line, honors the deadline,
and guarantees a final report even after a crash (--finalize)."""
import argparse
import json
import os
import socket
import subprocess
import sys
import time

from . import config as C

CREATE_NO_WINDOW = 0x08000000
DETACHED = 0x00000008


def tlog(msg):
    line = time.strftime("[%H:%M:%S] ") + str(msg)
    print(line, flush=True)
    with open(os.path.join(C.ROOT, "supervisor.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def keep_awake():
    """Hold ES_SYSTEM_REQUIRED for this process's lifetime: blocks idle sleep
    without touching the user's power plan (released on process exit)."""
    try:
        import ctypes
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
    except Exception:
        pass


def port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def ram_avail_gb():
    import ctypes, ctypes.wintypes as w

    class M(ctypes.Structure):
        _fields_ = [("dwLength", w.DWORD), ("dwMemoryLoad", w.DWORD),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = M()
    m.dwLength = ctypes.sizeof(M)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2**30


def spawn_service():
    subprocess.Popen(
        [C.PYTHONW, "mcp_v3.py", "--http", "--port", str(C.MEM_PORT)],
        cwd=C.SANDBOX_MEM_DIR, creationflags=DETACHED | CREATE_NO_WINDOW,
        close_fds=True)
    tlog(f"[service] spawned sandbox flymemory on port {C.MEM_PORT}")


def ensure_service(timeout=90):
    if port_open(C.MEM_HOST, C.MEM_PORT):
        tlog(f"[service] already up on {C.MEM_PORT}")
        return
    spawn_service()
    t0 = time.time()
    while time.time() - t0 < timeout:
        if port_open(C.MEM_HOST, C.MEM_PORT):
            tlog("[service] port is up")
            return
        time.sleep(3)
    tlog("[service] WARNING: port still down; worker will degrade to local mirror")


def finalize(run_dir, duration_h):
    r = subprocess.run(
        [C.PYTHON, "-m", "flyloop.worker", "--run-dir", run_dir,
         "--duration-h", str(duration_h), "--finalize"],
        cwd=C.ROOT, creationflags=CREATE_NO_WINDOW,
        capture_output=True, text=True, timeout=600)
    tlog(f"[finalize] rc={r.returncode} {r.stdout[-500:]} {r.stderr[-500:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--duration-h", type=float, default=C.DURATION_H)
    args = ap.parse_args()
    run_dir = os.path.abspath(args.run_dir)
    os.makedirs(run_dir, exist_ok=True)
    stop_path = os.path.join(run_dir, "STOP")
    final_path = os.path.join(run_dir, "final_report.md")

    tlog(f"[supervisor] run_dir={run_dir} duration={args.duration_h}h "
         f"ram_avail={ram_avail_gb():.1f}GB")
    keep_awake()

    # resume guard: a fresh heartbeat means a live worker is already on the job
    hb = os.path.join(run_dir, "heartbeat.json")
    try:
        if time.time() - os.path.getmtime(hb) < 90:
            tlog("[supervisor] fresh heartbeat found; worker already alive — "
                 "resume duty exits")
            return
    except OSError:
        pass

    ensure_service()

    start = time.time()
    deadline = start + args.duration_h * 3600
    restarts = 0
    backoff = 10.0
    last_service_check = 0.0

    while True:
        now = time.time()
        if now >= deadline and not os.path.exists(stop_path):
            with open(stop_path, "w") as f:
                f.write("deadline")
            tlog("[supervisor] deadline reached -> STOP file written")

        if ram_avail_gb() < C.RAM_MIN_AVAIL_GB:
            tlog(f"[supervisor] RAM red line ({ram_avail_gb():.1f}GB < "
                 f"{C.RAM_MIN_AVAIL_GB}GB); holding restarts")
            time.sleep(60)
            continue

        tlog(f"[supervisor] starting worker (restart #{restarts})")
        proc = subprocess.Popen(
            [C.PYTHON, "-m", "flyloop.worker", "--run-dir", run_dir,
             "--duration-h", str(args.duration_h)],
            cwd=C.ROOT, creationflags=CREATE_NO_WINDOW, close_fds=True)
        stop_written = os.path.exists(stop_path)
        while proc.poll() is None:
            time.sleep(5)
            if not stop_written and time.time() >= deadline:
                with open(stop_path, "w") as f:
                    f.write("deadline")
                stop_written = True
                tlog("[supervisor] deadline during run -> STOP written")
            if stop_written and time.time() >= deadline + 240:
                tlog("[supervisor] worker missed grace period; killing")
                proc.kill()
                break
            if time.time() - last_service_check > 20:
                last_service_check = time.time()
                if not port_open(C.MEM_HOST, C.MEM_PORT):
                    tlog("[service] down mid-run; respawning (idempotent)")
                    spawn_service()
        rc = proc.returncode
        tlog(f"[supervisor] worker exited rc={rc}")

        if rc == 0:
            tlog("[supervisor] worker finished gracefully")
            break
        if time.time() >= deadline:
            tlog("[supervisor] past deadline; finalizing")
            break
        restarts += 1
        if restarts > 30:
            tlog("[supervisor] restart budget exhausted; finalizing")
            break
        tlog(f"[supervisor] backing off {backoff:.0f}s before restart")
        time.sleep(backoff)
        backoff = min(300.0, backoff * 2)

    if not os.path.exists(final_path):
        tlog("[supervisor] final report missing -> finalize from disk")
        try:
            finalize(run_dir, args.duration_h)
        except Exception as e:
            tlog(f"[finalize] failed hard: {e}")
    # self-cleanup: remove the logon resume hook (harmless no-op if absent)
    try:
        subprocess.run(["reg", "delete",
                        r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                        "/v", "flyloop_resume", "/f"],
                       creationflags=CREATE_NO_WINDOW, capture_output=True)
    except Exception:
        pass
    tlog("[supervisor] done")


if __name__ == "__main__":
    main()
