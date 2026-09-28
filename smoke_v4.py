"""V4 smoke test: short three-arm run on fresh stores; verifies the paired
mechanics end-to-end (three-way parity, epi_test/book_test paths, discovery-
failure variation). Run from anywhere: python smoke_v4.py
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
os.environ["FLYLOOP_PORT_MATCHED"] = str(_free_port())
os.environ["FLYLOOP_PORT_EPI"] = str(_free_port())

from flyloop import config as C  # noqa: E402
from flyloop.supervisor import ensure_services  # noqa: E402

RUN = os.path.join(ROOT, "runs", f"smoke_v4_{int(time.time())}")
os.makedirs(RUN, exist_ok=True)
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        FAILS.append(name)


def kill_ports(ports):
    """Kill the detached sandbox services spawned for this smoke (RAM
    discipline); DBs are persisted on every write."""
    script = os.path.join(RUN, "_kill.ps1")
    with open(script, "w", encoding="utf-8") as f:
        f.write("$ports = %s\n" % ports)
        f.write("$conns = Get-NetTCPConnection -State Listen -ErrorAction "
                "SilentlyContinue | Where-Object { $ports -contains $_.LocalPort }\n")
        f.write("foreach ($c in $conns) { $p = Get-Process -Id "
                "$c.OwningProcess -ErrorAction SilentlyContinue; "
                "if ($p -and $p.ProcessName -like 'python*') { "
                "Stop-Process -Id $p.Id -Force } }\n")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                    "-File", script], capture_output=True)


async def main():
    ensure_services(RUN)
    env = dict(os.environ, FLYLOOP_QUOTA="0", FLYLOOP_PUZ_PERIOD0="24",
               FLYLOOP_PUZ_PERIOD_STEP="6", FLYLOOP_PACING_MS="5")
    proc = subprocess.run(
        [C.PYTHON, "-m", "flyloop.worker", "--run-dir", RUN,
         "--duration-h", "0.15"],
        cwd=ROOT, capture_output=True, text=True, env=env, timeout=1200)
    if proc.returncode != 0:
        print(proc.stdout[-3000:])
        print(proc.stderr[-3000:])
    check("worker exit 0", proc.returncode == 0, f"rc={proc.returncode}")

    recs = [json.loads(l) for l in open(os.path.join(RUN, "events.jsonl"),
                                        encoding="utf-8")]
    by_arm = {arm: [r for r in recs if r.get("memory_arm") == arm]
              for arm in ("FULL", "MATCHED", "EPISODIC")}
    ns = {a: len(v) for a, v in by_arm.items()}
    check("three arms present", all(v > 100 for v in ns.values()), str(ns))
    check("cycles triple-paired", ns["FULL"] == ns["MATCHED"] == ns["EPISODIC"], str(ns))

    puz = {a: [r for r in v if r.get("lane") == "puzzle"] for a, v in by_arm.items()}
    fields = ("episode_type", "family", "epoch", "rule_id", "memory_arm",
              "probe_idx", "prediction", "truth", "error", "method",
              "stale_intrusion", "discovery", "reactivation", "insight_kind")
    missing = [k for r in puz["FULL"][:50] for k in fields if k not in r]
    check("v4 event fields present", not missing, str(set(missing)))

    pair_ok = all((f["family"], f["epoch"], f["episode_type"], f["rule_id"],
                   f["truth"]) == (m["family"], m["epoch"], m["episode_type"],
                                   m["rule_id"], m["truth"]) ==
                  (e["family"], e["epoch"], e["episode_type"], e["rule_id"],
                   e["truth"])
                  for f, m, e in zip(puz["FULL"], puz["MATCHED"], puz["EPISODIC"]))
    check("arms see identical world probes", pair_ok)

    meth = {a: {} for a in puz}
    for a, rows in puz.items():
        for r in rows:
            meth[a][r["method"]] = meth[a].get(r["method"], 0) + 1
    check("FULL used book path", meth["FULL"].get("book_test", 0) > 0
          or meth["FULL"].get("rule", 0) > 0, str(meth["FULL"]))
    check("MATCHED used epi path", meth["MATCHED"].get("epi_test", 0) > 0,
          str(meth["MATCHED"]))
    check("EPISODIC never matched", "book_test" not in meth["EPISODIC"]
          and "epi_test" not in meth["EPISODIC"] and "rule" not in meth["EPISODIC"],
          str(meth["EPISODIC"]))
    check("probe-1 book_test fires (pre-fold)",
          any(r["probe_idx"] == 1 and r["method"] == "book_test"
              and r["error"] == 0 for r in puz["FULL"]))

    st = json.load(open(os.path.join(RUN, "state.json"), encoding="utf-8"))
    cf = st["runners"]["FULL"]["counts"]
    cm = st["runners"]["MATCHED"]["counts"]
    ce = st["runners"]["EPISODIC"]["counts"]
    check("discoveries happened", cf["discoveries"] > 0, str(cf["discoveries"]))
    # discovery-failure variation: DISTINCT rules abstracted (DISCOVERY kind
    # only) < distinct rules born (NEW + VARIANT episodes — every one births
    # a fresh rule)
    disc_rids = set()
    for line in open(os.path.join(RUN, "events.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        if r.get("memory_arm") == "FULL":
            for note in r.get("notes", []):
                if note.startswith("DISCOVERY"):
                    disc_rids.add(note.split("rid=")[1].split(" ")[0])
    born = cf["episodes"]["NEW"] + cf["episodes"]["VARIANT"]
    check("discovery-failure variation present",
          len(disc_rids) < born,
          f"distinct discovered rules={len(disc_rids)} vs born (NEW+VARIANT)={born}")
    check("archive writes happened", cm["epireg_writes"] > 0,
          str(cm["epireg_writes"]))
    owed = cf["book_bytes"] + cm["epireg_bytes"]
    check("three-way byte parity", ce["pad_bytes"] == owed,
          f"pads={ce['pad_bytes']} owed={owed}")
    check("pad events == book+archive events",
          ce["pad_writes"] == cf["book_writes"] + cm["epireg_writes"],
          f"{ce['pad_writes']} vs {cf['book_writes']}+{cm['epireg_writes']}")

    sched = json.load(open(os.path.join(RUN, "world_schedule.json"),
                           encoding="utf-8"))
    check("schedule artifact saved", bool(sched) and "0" in sched)
    led = [json.loads(l) for l in open(os.path.join(RUN, "ledger.jsonl"),
                                       encoding="utf-8")]
    check("V4 predictions pre-registered",
          sum(1 for r in led if r["claim"].startswith("V4-P")) == 8)

    print()
    print("SMOKE FAILURES:", FAILS if FAILS else "none")
    kill_ports([C.MEM_PORT, C.MEM_PORT_MATCHED, C.MEM_PORT_EPI])
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
