"""Overnight worker, v3: two memory arms through the identical world.

Robustness contract (v1/v2, unchanged): every cycle try/except; N consecutive
failures trip a circuit breaker -> checkpoint -> exit(3); checkpoint every 50
cycles / 120s; heartbeat 15s; STATUS 60s; periodic reports; service-down ->
local mirror with auto-switch-back; RAM red line; deadline in deadline.json.

v3 additions (V3_DESIGN.md):
  - FULL arm (book registry, port MEM_PORT) and EPI arm (tables only,
    port MEM_PORT_EPI) run the same cycle loop back-to-back, sharing one
    precomputed world schedule and one PadSync (byte-exact write parity).
  - quota-stop on episode statistics (NEW/VARIANT/RECALL/shocks);
  - ENGINEERING_INVALID status: an engineering failure voids the run as a
    hypothesis test without scoring it as a hypothesis negative;
  - endpoint verdicts (V3-P01..P08) are applied by experiments/analyze_v3.py,
    NOT here — the worker pre-registers and stays honest about what it cannot
    compute in-flight (paired bootstrap).
"""
import argparse
import asyncio
import json
import os
import re
import sys
import time

from . import config as C, world, reports
from .memclient import MemFacade
from .poetleg import PoetLeg
from .insight import Metrics, Ledger, InsightDetector
from .cycle import CycleRunner, PadSync

ARMS = ("FULL", "EPI")


def log(msg):
    print(time.strftime("[%H:%M:%S] ") + str(msg), flush=True)


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
    return round(m.ullAvailPhys / 2**30, 1)


def load_events(path):
    recs = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    recs.append(json.loads(line))
                except Exception:
                    pass
    return recs


def _atomic_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)


class Worker:
    def __init__(self, run_dir, duration_h, max_cycles):
        self.run_dir = os.path.abspath(run_dir)
        os.makedirs(os.path.join(self.run_dir, "reports"), exist_ok=True)
        os.makedirs(os.path.join(self.run_dir, "checkpoints"), exist_ok=True)
        self.events_path = os.path.join(self.run_dir, "events.jsonl")
        self.state_path = os.path.join(self.run_dir, "state.json")
        self.poet_paths = {arm: {"A": os.path.join(self.run_dir, f"poet{arm}_A.pt"),
                                 "B": os.path.join(self.run_dir, f"poet{arm}_B.pt")}
                           for arm in ARMS}
        self.ledger_path = os.path.join(self.run_dir, "ledger.jsonl")
        self.stop_path = os.path.join(self.run_dir, "STOP")
        self.hb_path = os.path.join(self.run_dir, "heartbeat.json")
        self.dl_path = os.path.join(self.run_dir, "deadline.json")
        self.duration_h = duration_h
        self.max_cycles = max_cycles
        self.cycle = 0
        self.fails = 0
        self.run_status = "OK"

    # ------------------------------------------------------------------
    def _load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self, detF, detE, runF, runE, poets, wall_start):
        _atomic_json(self.state_path, {
            "cycle": self.cycle, "wall_start": wall_start,
            "run_status": self.run_status,
            "detF": detF.to_dict(), "detE": detE.to_dict(),
            "runnerF": runF.to_dict(), "runnerE": runE.to_dict(),
            "poets": {arm: {tag: p.updates for tag, p in poets[arm].items()}
                      for arm in ARMS},
            "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
        for arm in ARMS:
            for tag, p in poets[arm].items():
                p.save(self.poet_paths[arm][tag])

    def _heartbeat(self, modes):
        _atomic_json(self.hb_path, {
            "cycle": self.cycle, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fails": self.fails, "mem_mode": modes,
            "run_status": self.run_status,
            "ram_gb": ram_avail_gb()})

    # -- v3 registered predictions (registered before the first cycle) --------
    def _pre_register(self):
        cmax = self.max_cycles
        r = self.ledger.register
        r("V3-P01 (PRIMARY): Full arm RECALL error in the first 20 probes lower "
          "than Episodic, paired bootstrap 95% CI of dE excludes 0",
          cmax, "run", "unit = RECALL episode; analysis: experiments/analyze_v3.py")
        r("V3-P02 (PRIMARY): Full arm recovery latency (first correct probe) "
          "shorter than Episodic on RECALL, paired CI excludes 0",
          cmax, "run", "")
        r("V3-P03: the Full advantage survives at every recurrence gap 2/3/4/5 "
          "(point estimate of dE in favor of Full in all four buckets)",
          cmax, "run", "")
        r("V3-P04 (NC1): |dE| on VARIANT clearly smaller than on RECALL — the "
          "Full advantage is recurrence reuse, not generic smartness",
          cmax, "run", "")
        r("V3-P05: stale intrusion rate SIR(Full) <= 1.5 x SIR(Episodic) — "
          "remembering more must not mean confusing past with present",
          cmax, "run", "")
        r("V3-P06: useful-insight rate (discoveries whose rule later pays off on "
          "a recurrence) above the permutation null (95th pct)",
          cmax, "run", "")
        r("V3-P07: Full degrades slower than Episodic from noise phase A (1x) "
          "to phase C (4x), on RECALL episodes and overall",
          cmax, "run", "")
        r("V3-P08 (NC2): fact lane shows no regression under the v3 policy: "
          "phase-C err100 <= 2x phase-A err100 and <= 0.20 absolute, both arms",
          cmax, "run", "")
        log("[ledger] pre-registered 8 v3 predictions")

    # ------------------------------------------------------------------
    def _quota_state(self, runF, detF):
        ep = runF.counts["episodes"]
        return {"NEW": ep["NEW"], "VARIANT": ep["VARIANT"], "RECALL": ep["RECALL"],
                "shocks": detF.shock_seen()}

    def _quotas_met(self, runF, detF):
        q = self._quota_state(runF, detF)
        return (q["NEW"] >= C.QUOTA_NEW and q["VARIANT"] >= C.QUOTA_VARIANT
                and q["RECALL"] >= C.QUOTA_RECALL and q["shocks"] >= C.QUOTA_SHOCKS)

    def _engineering_check(self, runF, runE, entries):
        """Tripwires that void the run as a hypothesis test (V3 §14)."""
        bad = []
        for arm, run in (("FULL", runF), ("EPI", runE)):
            ct = run.counts
            rb = (ct.get("fact_readback_fail", 0) + ct.get("rulebook_readback_fail", 0)
                  + ct.get("table_readback_fail", 0))
            writes = max(ct.get("fact_writes", 0) + ct.get("book_writes", 0)
                         + ct.get("pair_writes", 0), 1)
            if rb > C.MAX_READBACK_FAIL_FRAC * writes:
                bad.append(f"{arm}: readback failures {rb}/{writes}")
            n = entries.get(arm)
            if n is not None and n > C.MAX_MEM_ENTRIES:
                bad.append(f"{arm}: memory entries {n} > {C.MAX_MEM_ENTRIES}")
        return bad

    # ------------------------------------------------------------------
    async def run(self):
        self._mems = []
        try:
            from .supervisor import keep_awake
            keep_awake()
        except Exception:
            pass
        try:
            await self._run()
        finally:
            for m in self._mems:
                await m.close()

    async def _run(self):
        st = self._load_state()
        self.cycle = st.get("cycle", 0)
        self.run_status = st.get("run_status", "OK")
        if os.path.exists(self.dl_path):
            with open(self.dl_path, encoding="utf-8") as f:
                dl = json.load(f)
            wall_start, deadline = dl["wall_start"], dl["deadline"]
        else:
            wall_start = time.time()
            deadline = wall_start + self.duration_h * 3600
            _atomic_json(self.dl_path, {"wall_start": wall_start, "deadline": deadline})

        # the world schedule must exist as an artifact BEFORE the first cycle
        sched_path = os.path.join(self.run_dir, "world_schedule.json")
        if not os.path.exists(sched_path):
            _atomic_json(sched_path, world.puz_schedule())
        self._pre_register_needed = not os.path.exists(self.ledger_path)

        metricsF, metricsE = Metrics(), Metrics()
        metricsF.load_events(load_events(self.events_path), arm="FULL")
        metricsE.load_events(load_events(self.events_path), arm="EPI")
        self.ledger = Ledger(self.ledger_path)
        detF = InsightDetector(metricsF, self.ledger, log, signatures=False)
        detE = InsightDetector(metricsE, self.ledger, log, signatures=False)
        detF.load_dict(st.get("detF", {}))
        detE.load_dict(st.get("detE", {}))

        memF = MemFacade(log, C.MEM_URL)
        memE = MemFacade(log, C.MEM_URL_EPI)
        self._mems = [memF, memE]
        await memF.start()
        await memE.start()
        try:
            await memF.recall("FLFACT warmup", compartment=C.COMPARTMENT_FACT)
            await memE.recall("FLFACT warmup", compartment=C.COMPARTMENT_FACT)
        except Exception as e:
            log(f"[mem] warmup skipped: {e}")

        poets = {}
        for arm in ARMS:
            poets[arm] = {
                "A": PoetLeg(f"{arm}-A", C.SEQ_V, C.SEQ_CTX + 1, C.SEQ_V, log),
                "B": PoetLeg(f"{arm}-B", C.SEQ_V + C.SEQ_N_REGIMES, C.SEQ_CTX + 2,
                             C.SEQ_V, log)}
            for tag, path in self.poet_paths[arm].items():
                if os.path.exists(path):
                    try:
                        poets[arm][tag].load(path)
                        log(f"[poet{arm}-{tag}] resumed (updates={poets[arm][tag].updates})")
                    except Exception as e:
                        self.run_status = f"ENGINEERING_INVALID:poet-{arm}-{tag}-load"
                        log(f"[poet{arm}-{tag}] load failed ({e}); run marked invalid")

        pad = PadSync()
        runF = CycleRunner(memF, poets["FULL"], detF, self.ledger, log,
                           arm="FULL", pad_sync=pad)
        runE = CycleRunner(memE, poets["EPI"], detE, self.ledger, log,
                           arm="EPI", pad_sync=pad)
        runF.load_dict(st.get("runnerF", {}))
        runE.load_dict(st.get("runnerE", {}))
        if self._pre_register_needed:
            self._pre_register()

        last_hb = last_ckpt = last_status = last_report = last_probe = time.time()
        report_n = len([f for f in os.listdir(os.path.join(self.run_dir, "reports"))
                        if f.startswith("report_")])
        end = "unknown"
        log(f"[worker] v3 start at cycle {self.cycle} (arms FULL@{C.MEM_PORT} / "
            f"EPI@{C.MEM_PORT_EPI}), deadline "
            f"{time.strftime('%m-%d %H:%M', time.localtime(deadline))}")

        while True:
            now = time.time()
            if os.path.exists(self.stop_path):
                end = "STOP file"
                break
            if now >= deadline:
                end = "deadline reached"
                break
            c = self.cycle + 1
            if c > self.max_cycles:
                end = "max cycles"
                break
            if C.QUOTA_ENABLED and self._quotas_met(runF, detF):
                end = "quota satisfied"
                break
            try:
                t0 = time.perf_counter()
                recF = await runF.run_cycle(c)
                recE = await runE.run_cycle(c)
                self.cycle = c
                self.fails = 0
                with open(self.events_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(recF, ensure_ascii=False) + "\n")
                    f.write(json.dumps(recE, ensure_ascii=False) + "\n")
                for rec, met in ((recF, metricsF), (recE, metricsE)):
                    met.add(c, "seqA", rec.get("seqA_err"))
                    met.add(c, "seqB", rec.get("seqB_err"))
                    met.add(c, "factA", rec.get("factA_err"))
                    met.add(c, "factB", rec.get("factB_err"))
                    if rec.get("lane") == "puzzle":
                        met.add(c, "puzzle", rec.get("error"))
                detF.on_cycle(c, recF)
                detE.on_cycle(c, recE)
                dt = (time.perf_counter() - t0) * 1000
                if dt < C.SPEED_PACING_MS:
                    await asyncio.sleep((C.SPEED_PACING_MS - dt) / 1000.0)
            except Exception as e:
                self.fails += 1
                log(f"[c{c}] cycle FAILED ({self.fails}): "
                    f"{type(e).__name__}: {str(e)[:200]}")
                with open(self.events_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"c": c, "error": f"{type(e).__name__}: {str(e)[:150]}",
                                        "t": time.strftime("%H:%M:%S")}) + "\n")
                if self.fails >= C.CONSECUTIVE_FAIL_LIMIT:
                    self.run_status = "ENGINEERING_INVALID:consecutive-failures"
                    self._save(detF, detE, runF, runE, poets, wall_start)
                    log("circuit breaker OPEN -> checkpoint saved, exit(3)")
                    sys.exit(3)

            now = time.time()
            if now - last_hb > C.HEARTBEAT_EVERY_S:
                self._heartbeat(f"{memF.mode}/{memE.mode}")
                last_hb = now
            if now - last_ckpt > C.CHECKPOINT_EVERY_S or c % C.CHECKPOINT_EVERY_CYCLES == 0:
                self._save(detF, detE, runF, runE, poets, wall_start)
                last_ckpt = now
            if now - last_status > C.STATUS_EVERY_S:
                snap = self._snap(c, wall_start, metricsF, metricsE, detF, runF,
                                  runE, pad, memF, memE, poets, end="running")
                reports.write_status(self.run_dir, reports.render_v3(snap))
                last_status = now
            if now - last_report > C.REPORT_EVERY_S:
                snap = self._snap(c, wall_start, metricsF, metricsE, detF, runF,
                                  runE, pad, memF, memE, poets, end="running",
                                  detail=True)
                reports.write_hourly(self.run_dir, reports.render_v3(snap, detail=True),
                                     report_n + 1)
                report_n += 1
                last_report = now
            if memF.mode == "local" and now - last_probe > 30:
                await memF.probe()
                last_probe = now
            if memE.mode == "local" and now - last_probe > 30:
                await memE.probe()
                last_probe = now
            await asyncio.sleep(0)

        # ---------------- graceful end ----------------
        log(f"[worker] ending: {end} at cycle {self.cycle}")
        self._save(detF, detE, runF, runE, poets, wall_start)
        entries = {}
        for arm, mem in (("FULL", memF), ("EPI", memE)):
            n, _ = await self._mem_entries_count(mem)
            entries[arm] = n
        bad = self._engineering_check(runF, runE, entries)
        if bad:
            self.run_status = "ENGINEERING_INVALID:" + ";".join(bad)[:150]
        snap = self._snap(self.cycle, wall_start, metricsF, metricsE, detF, runF,
                          runE, pad, memF, memE, poets, end=end, detail=True,
                          entries=entries)
        reports.write_status(self.run_dir, reports.render_v3(snap))
        reports.write_final(self.run_dir, reports.render_v3(snap, detail=True), end)
        log(f"[worker] final report written; entries={entries}; "
            f"run_status={self.run_status}; bye")

    def _snap(self, c, wall_start, metricsF, metricsE, detF, runF, runE, pad,
              memF, memE, poets, end="running", detail=False, entries=None):
        snap = reports.build_snapshot(
            c, wall_start, self.duration_h, self.max_cycles,
            metricsF, detF, runF, self.ledger, memF.mode, None,
            poets["FULL"], end=end, ram_gb=ram_avail_gb())
        snap.update(arm_stats={
            "FULL": {"metrics": metricsF.summary(c), "counts": runF.counts},
            "EPI": {"metrics": metricsE.summary(c), "counts": runE.counts}},
            pad_parity=pad.parity(), run_status=self.run_status,
            entries=entries or {}, quotas=self._quota_state(runF, detF),
            expected=world.expected_counts(c))
        return snap

    async def _mem_entries_count(self, mem):
        text, mode = await mem.stats()
        m = re.search(r"Memories:\s*(\d+)", text or "")
        return (int(m.group(1)) if m else None), mode

    # ------------------------------------------------------------------
    async def finalize(self):
        """Rebuild everything from disk and write the final report (no cycles).
        Endpoint verdicts come from experiments/analyze_v3.py, not here."""
        st = self._load_state()
        self.cycle = st.get("cycle", 0)
        self.run_status = st.get("run_status", "OK")
        metricsF, metricsE = Metrics(), Metrics()
        metricsF.load_events(load_events(self.events_path), arm="FULL")
        metricsE.load_events(load_events(self.events_path), arm="EPI")
        self.ledger = Ledger(self.ledger_path)
        detF = InsightDetector(metricsF, self.ledger, log, signatures=False)
        detE = InsightDetector(metricsE, self.ledger, log, signatures=False)
        detF.load_dict(st.get("detF", {}))
        detE.load_dict(st.get("detE", {}))
        runF = CycleRunner(None, None, detF, self.ledger, log, arm="FULL")
        runF.load_dict(st.get("runnerF", {}))
        runE = CycleRunner(None, None, detE, self.ledger, log, arm="EPI")
        runE.load_dict(st.get("runnerE", {}))
        with open(self.dl_path, encoding="utf-8") as f:
            dl = json.load(f)
        memF = MemFacade(log, C.MEM_URL)
        memE = MemFacade(log, C.MEM_URL_EPI)
        await memF.start()
        await memE.start()
        entries = {}
        for arm, mem in (("FULL", memF), ("EPI", memE)):
            n, _ = await self._mem_entries_count(mem)
            entries[arm] = n
        bad = self._engineering_check(runF, runE, entries)
        if bad and self.run_status == "OK":
            self.run_status = "ENGINEERING_INVALID:" + ";".join(bad)[:150]
        pad = PadSync()
        snap = self._snap(self.cycle, dl["wall_start"], metricsF, metricsE, detF,
                          runF, runE, pad, memF, memE, None,
                          end="finalized-after-crash", detail=True, entries=entries)
        reports.write_status(self.run_dir, reports.render_v3(snap))
        reports.write_final(self.run_dir, reports.render_v3(snap, detail=True),
                            "finalized")
        log(f"[worker] finalized from disk at cycle {self.cycle}; "
            f"run_status={self.run_status}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--duration-h", type=float, default=C.DURATION_H)
    ap.add_argument("--max-cycles", type=int, default=C.MAX_CYCLES)
    ap.add_argument("--finalize", action="store_true")
    args = ap.parse_args()
    w = Worker(args.run_dir, args.duration_h, args.max_cycles)
    if args.finalize:
        asyncio.run(w.finalize())
    else:
        asyncio.run(w.run())


if __name__ == "__main__":
    main()
