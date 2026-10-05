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
        pass  # POSIX node: no sleep to hold
    except Exception:
        pass


def port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def ram_avail_gb():
    import os
    return round(os.sysconf('SC_AVPHYS_PAGES') * os.sysconf('SC_PAGE_SIZE') / 2**30, 1)


def spawn_service(port: int, db_path: str):
    subprocess.Popen(
        [C.PYTHONW, "mcp_v3.py", "--http", "--port", str(port), "--db", db_path],
        cwd=C.SANDBOX_MEM_DIR, close_fds=True)
    tlog(f"[service] spawned sandbox flymemory on port {port} db={db_path}")


def ensure_service(port: int, db_path: str, timeout=90):
    if port_open(C.MEM_HOST, port):
        tlog(f"[service] already up on {port}")
        return
    spawn_service(port, db_path)
    t0 = time.time()
    while time.time() - t0 < timeout:
        if port_open(C.MEM_HOST, port):
            tlog("[service] port is up")
            return
        time.sleep(3)
    tlog("[service] WARNING: port still down; worker will degrade to local mirror")


def service_ports():
    """(port, db_name, tag) per arm. FLYLOOP_PORTS (comma list aligned with
    FLYLOOP_ARMS) overrides the legacy trio -- the count MUST match the arm
    list or extra arms connect-timeout at worker start (V10c smoke)."""
    ports_env = os.environ.get("FLYLOOP_PORTS", "")
    if ports_env:
        arms = [a for a in os.environ.get("FLYLOOP_ARMS", "").split(",") if a]
        ports = [p for p in ports_env.split(",") if p]
        return [(int(port), f"mem_{(arms[i] if i < len(arms) else f'arm{i}')}.pkl",
                 (arms[i] if i < len(arms) else f"arm{i}"))
                for i, port in enumerate(ports)]
    return [(C.MEM_PORT, "mem_FULL.pkl", "FULL"),
            (C.MEM_PORT_MATCHED, "mem_MATCHED.pkl", "MATCHED"),
            (C.MEM_PORT_EPI, "mem_EPI.pkl", "EPI")]


def ensure_services(run_dir):
    """One store per memory arm (v4)."""
    for port, dbf, _tag in service_ports():
        ensure_service(port, os.path.join(run_dir, dbf))


def finalize(run_dir, duration_h):
    r = subprocess.run(
        [C.PYTHON, "-m", "flyloop.worker", "--run-dir", run_dir,
         "--duration-h", str(duration_h), "--finalize"],
        cwd=C.ROOT,  capture_output=True, text=True, timeout=600)
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

    ensure_services(run_dir)

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
        # worker output MUST be captured: with no redirect under
        # CREATE_NO_WINDOW the child's stderr is an invalid handle and a
        # startup traceback vanishes (V10c smoke lost ~40min to this).
        wlog = open(os.path.join(run_dir, "worker.log"), "a", encoding="utf-8")
        proc = subprocess.Popen(
            [C.PYTHON, "-m", "flyloop.worker", "--run-dir", run_dir,
             "--duration-h", str(args.duration_h)],
            cwd=C.ROOT,  close_fds=True,
            stdout=wlog, stderr=wlog)
        stop_written = os.path.exists(stop_path)
        start_ts = time.time()
        duration_s = args.duration_h * 3600
        quarters_done = 0
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
                # quarter-mark diagnostics (operator directive 10-02):
                # at 25/50/75% of the horizon, run the run-health checks
                # and surface the result -- catches dead machinery at the
                # quarter mark instead of at adjudication.
                frac = (time.time() - start_ts) / max(duration_s, 1)
                for q in (0.25, 0.5, 0.75):
                    if frac >= q and quarters_done < int(q * 4):
                        quarters_done += 1
                        rdiag = subprocess.run(
                            [sys.executable, os.path.join(
                                C.ROOT, "tests", "diagnose.py"),
                             "--run-dir", run_dir],
                            cwd=C.ROOT, capture_output=True, text=True,
                             )
                        tlog(f"[diag {int(q*100)}%] rc={rdiag.returncode} "
                             + " | ".join(l for l in
                                          (rdiag.stdout or "").splitlines()
                                          if l.startswith(("FAIL", "WARN")))
                             + (" PASS" if rdiag.returncode == 0 else ""))
                        with open(os.path.join(run_dir, "diag.md"), "a",
                                  encoding="utf-8") as df:
                            df.write(f"## {int(q*100)}% "
                                     f"({time.strftime('%H:%M')})\n\n"
                                     + (rdiag.stdout or "") + "\n")
                for port, dbf, tag in service_ports():
                    if not port_open(C.MEM_HOST, port):
                        tlog(f"[service] {tag} down mid-run; respawning (idempotent)")
                        spawn_service(port, os.path.join(run_dir, dbf))
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
                        capture_output=True)
    except Exception:
        pass
    tlog("[supervisor] done")


if __name__ == "__main__":
    main()
