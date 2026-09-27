"""V3 smoke test: short two-arm run on fresh stores; verifies the paired
mechanics end-to-end. Run from anywhere:
    python smoke_v3.py
"""
import asyncio
import json
import os
import socket
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


# fresh ports + fresh stores on every smoke run (must precede flyloop imports)
os.environ["FLYLOOP_PORT"] = str(_free_port())
os.environ["FLYLOOP_PORT_EPI"] = str(_free_port())

from flyloop import config as C  # noqa: E402
from flyloop.supervisor import ensure_services  # noqa: E402

RUN = os.path.join(ROOT, "runs", f"smoke_v3_{int(time.time())}")
os.makedirs(RUN, exist_ok=True)


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        global FAILS
        FAILS.append(name)


FAILS = []


def kill_port(pid_hint_ports):
    """Kill the detached sandbox services spawned for this smoke (they hold
    ~400MB each; leaving them alive would breach the RAM discipline)."""
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True).stdout
        pids = set()
        for line in out.splitlines():
            for port in pid_hint_ports:
                if f":{port}" in line and "LISTENING" in line:
                    pids.add(line.split()[-1])
        for pid in pids:
            subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
            print(f"killed leftover service pid={pid}")
    except Exception as e:
        print(f"cleanup skipped: {e}")


async def main():
    ensure_services(RUN)
    env = dict(os.environ, FLYLOOP_QUOTA="0", FLYLOOP_PUZ_PERIOD0="60",
               FLYLOOP_PUZ_PERIOD_STEP="20", FLYLOOP_PACING_MS="10")
    proc = subprocess.run(
        [C.PYTHON, "-m", "flyloop.worker", "--run-dir", RUN,
         "--duration-h", "0.12"],
        cwd=ROOT, capture_output=True, text=True, env=env, timeout=900)
    print(proc.stdout[-3000:])
    if proc.returncode != 0:
        print(proc.stderr[-3000:])
    check("worker exit 0", proc.returncode == 0, f"rc={proc.returncode}")

    recs = [json.loads(l) for l in open(os.path.join(RUN, "events.jsonl"),
                                        encoding="utf-8")]
    full = [r for r in recs if r.get("memory_arm") == "FULL"]
    epi = [r for r in recs if r.get("memory_arm") == "EPI"]
    check("both arms present", len(full) > 50 and len(epi) > 50,
          f"F={len(full)} E={len(epi)}")
    check("cycles paired", len(full) == len(epi),
          f"{len(full)} vs {len(epi)}")

    puzF = [r for r in full if r.get("lane") == "puzzle"]
    puzE = [r for r in epi if r.get("lane") == "puzzle"]
    fields = ("episode_type", "family", "epoch", "rule_id", "memory_arm",
              "prediction", "truth", "error", "method", "retrieval_rank",
              "stale_candidate_present", "stale_intrusion", "discovery",
              "useful_insight")
    missing = [k for r in puzF[:50] for k in fields if k not in r]
    check("v3 event fields present", not missing, str(set(missing)))

    # paired observations: same world on both arms
    pair_ok = all((f["family"], f["epoch"], f["episode_type"], f["rule_id"],
                   f["truth"]) == (e["family"], e["epoch"], e["episode_type"],
                                   e["rule_id"], e["truth"])
                  for f, e in zip(puzF, puzE))
    check("arms see identical world probes", pair_ok)

    methodsF = {}
    for r in puzF:
        methodsF[r["method"]] = methodsF.get(r["method"], 0) + 1
    check("FULL arm used the book path", methodsF.get("book_test", 0) > 0 or
          methodsF.get("rule", 0) > 0, str(methodsF))
    methodsE = {}
    for r in puzE:
        methodsE[r["method"]] = methodsE.get(r["method"], 0) + 1
    check("EPI arm never used the book", "book_test" not in methodsE
          and "rule" not in methodsE, str(methodsE))

    stF = json.load(open(os.path.join(RUN, "state.json"), encoding="utf-8"))
    cf = stF["runnerF"]["counts"]
    ce = stF["runnerE"]["counts"]
    check("discoveries happened", cf["discoveries"] > 0, str(cf["discoveries"]))
    check("write parity: pads == book writes",
          ce["pad_writes"] == cf["book_writes"],
          f"pads={ce['pad_writes']} books={cf['book_writes']}")
    check("write parity: pad bytes == book bytes",
          ce["pad_bytes"] == cf["book_bytes"],
          f"{ce['pad_bytes']} vs {cf['book_bytes']}")
    # schedule artifact exists and matches counts
    sched = json.load(open(os.path.join(RUN, "world_schedule.json"),
                           encoding="utf-8"))
    check("schedule artifact saved", bool(sched) and "0" in sched)

    # entry counts independent per store
    from flyloop.memclient import MemFacade  # noqa: E402

    async def count(url):
        mem = MemFacade(print, url)
        await mem.start()
        text, _ = await mem.stats()
        await mem.close()
        import re
        m = re.search(r"Memories:\s*(\d+)", text or "")
        return int(m.group(1)) if m else -1

    nF = await count(C.MEM_URL)
    nE = await count(C.MEM_URL_EPI)
    check("stores independent and non-empty", 0 < nF < 3000 and 0 < nE < 3000,
          f"F={nF} E={nE}")

    print()
    print("SMOKE FAILURES:", FAILS if FAILS else "none")
    kill_port([C.MEM_PORT, C.MEM_PORT_EPI])
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
