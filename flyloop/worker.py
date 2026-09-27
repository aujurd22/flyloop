"""Overnight worker: runs the 7-step loop for `duration` hours (v2).

Robustness contract (unchanged from v1): every cycle try/except; N consecutive
failures trip a circuit breaker -> checkpoint -> exit(3); checkpoint every 50
cycles / 120s; heartbeat 15s; STATUS 60s; periodic reports; service-down ->
local mirror with auto-switch-back; RAM red line; deadline in deadline.json.

v2 additions: dual seq streams A/B, fact A/B arms, quota-stop rules
(DESIGN_V2 §8: events are bought by statistics, not by wall clock).
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
from .cycle import CycleRunner


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
        self.poetA_path = os.path.join(self.run_dir, "poetA.pt")
        self.poetB_path = os.path.join(self.run_dir, "poetB.pt")
        self.ledger_path = os.path.join(self.run_dir, "ledger.jsonl")
        self.stop_path = os.path.join(self.run_dir, "STOP")
        self.hb_path = os.path.join(self.run_dir, "heartbeat.json")
        self.dl_path = os.path.join(self.run_dir, "deadline.json")
        self.duration_h = duration_h
        self.max_cycles = max_cycles
        self.cycle = 0
        self.fails = 0

    # ------------------------------------------------------------------
    def _load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self, det, runner, poets, wall_start):
        _atomic_json(self.state_path, {
            "cycle": self.cycle, "wall_start": wall_start,
            "det": det.to_dict(), "runner": runner.to_dict(),
            "poetA_updates": poets["A"].updates, "poetB_updates": poets["B"].updates,
            "ts": time.strftime("%Y-%m-%d %H:%M:%S")})
        for tag, p in poets.items():
            p.save(self.poetA_path if tag == "A" else self.poetB_path)

    def _heartbeat(self, mem_mode):
        _atomic_json(self.hb_path, {
            "cycle": self.cycle, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "fails": self.fails, "mem_mode": mem_mode,
            "ram_gb": ram_avail_gb()})

    # -- v2 registered predictions (registered before the first cycle) --------
    def _pre_register(self):
        cmax = self.max_cycles
        r = self.ledger.register
        r("V2-P01: cold rate (puzzle) <= 5% after truncation fix",
          cmax, "run", "band: >15% => NEGATIVE (audit implementation first)")
        r("V2-P02: rule entries survive active in their own compartment: >=90% of "
          "discoveries readable back as flags",
          cmax, "run", "")
        r("V2-P03: fact B arm (state_lookup) error <= half of fact A arm (recall) error",
          cmax, "run", "")
        r("V2-P04: write-readback failures on sampled fact writes <= 2%",
          cmax, "run", "")
        r("V2-P05: no invariant violations observed (I1 active-unique via state_history)",
          cmax, "run", "")
        r("V2-P06: seq stream B (regime marker) rolling err < 0.68 (oracle 0.639)",
          cmax, "run", "")
        r("V2-P07: seq stream A replicates v1 stall: err >= 0.70 for >= 90% of 1k-bins",
          cmax, "run", "")
        r("V2-P08: signature CONFIRMED ratio in [0.4, 0.9] (no overflow)",
          cmax, "run", "")
        r("V2-P09: >=40000 cycles in 5h (speed target), 0 breaker trips",
          cmax, "run", "")
        r("V2-P10: memory entries <= 40000 at end",
          cmax, "run", "")
        log("[ledger] pre-registered 10 v2 run-level predictions")

    def _seq_bin_stats(self, metrics, lane, cycle, bin_size=1000):
        d = metrics.err.get(lane, {})
        bins, cur, acc = [], 0, []
        for c in sorted(d):
            b = c // bin_size
            while len(bins) <= b:
                bins.append([])
            bins[b].append(d[c])
        return [sum(v) / len(v) for v in bins if v]

    def _adjudicate(self, det, runner, entries_count, metrics):
        led = self.ledger
        ct = runner.counts
        # P01 cold rate
        puz_n = sum(1 for _ in [0])  # placeholder; computed from counters below
        cold = ct.get("trunc_fail", 0)
        puz_total = ct.get("pair_writes", 0) + 1  # approximations guarded below
        # use probe count = fact writes + pair writes is wrong; use events-derived
        probes = ct.get("_puz_probes", 0)
        if probes:
            rate = cold / probes
            led.set_status("V2-P01", "CONFIRMED" if rate <= 0.05 else
                           ("PARTIAL" if rate <= 0.15 else "REFUTED"),
                           f"cold={cold}/{probes}={rate:.3f}")
        # P02 rule survival (readback failures)
        rb = ct.get("readback_fail", 0)
        disc = ct.get("discoveries", 0)
        if disc:
            ok_frac = 1 - rb / max(disc, 1)
            led.set_status("V2-P02", "CONFIRMED" if ok_frac >= 0.9 else
                           ("PARTIAL" if ok_frac >= 0.7 else "REFUTED"),
                           f"readback_fail={rb}/{disc}")
        # P03 A/B arm
        a_n, b_n = ct.get("factA_n", 0), ct.get("factB_n", 0)
        a_h, b_h = ct.get("factA_hit", 0), ct.get("factB_hit", 0)
        if a_n and b_n:
            ea = sum(metrics.err.get("factA", {}).values()) / max(len(metrics.err.get("factA", {})), 1)
            eb = sum(metrics.err.get("factB", {}).values()) / max(len(metrics.err.get("factB", {})), 1)
            led.set_status("V2-P03", "CONFIRMED" if eb <= ea / 2 else
                           ("PARTIAL" if eb < ea else "REFUTED"),
                           f"errA={ea:.3f} errB={eb:.3f} hitA={a_h}/{a_n} hitB={b_h}/{b_n}")
        # P04 readback rate
        fw = max(ct.get("fact_writes", 0) // 20, 1)
        led.set_status("V2-P04", "CONFIRMED" if rb <= 0.02 * fw else "REFUTED",
                       f"readback_fail={rb}, sampled_writes={fw}")
        # P06/P07 streams
        bins_b = self._seq_bin_stats(metrics, "seqB", self.cycle)
        bins_a = self._seq_bin_stats(metrics, "seqA", self.cycle)
        if bins_b:
            last10 = bins_b[-10:]
            mb = sum(last10) / len(last10)
            led.set_status("V2-P06", "CONFIRMED" if mb < 0.68 else
                           ("PARTIAL" if mb < 0.75 else "REFUTED"),
                           f"seqB last10k-bin mean={mb:.3f} (bins={len(bins_b)})")
        if bins_a:
            frac_ge70 = sum(1 for v in bins_a if v >= 0.70) / len(bins_a)
            led.set_status("V2-P07", "CONFIRMED" if frac_ge70 >= 0.9 else "REFUTED",
                           f"bins>=0.70: {frac_ge70:.2f} ({len(bins_a)} bins)")
        # P08 signature ratio
        sigs = [i for i in led.items if i["kind"] == "signature"
                and i["status"] in ("CONFIRMED", "REFUTED")]
        if sigs:
            conf = sum(1 for i in sigs if i["status"] == "CONFIRMED")
            frac = conf / len(sigs)
            led.set_status("V2-P08", "CONFIRMED" if 0.4 <= frac <= 0.9 else "REFUTED",
                           f"{conf}/{len(sigs)} = {frac:.2f}")
        # P09/P10 run-level
        led.set_status("V2-P09", "CONFIRMED" if self.cycle >= 40000 and self.fails == 0
                       else "REFUTED", f"cycles={self.cycle} fails_trail={self.fails}")
        if entries_count is not None:
            led.set_status("V2-P10", "CONFIRMED" if entries_count <= 40000 else "REFUTED",
                           f"entries={entries_count}")
        led.save()

    async def _mem_entries_count(self, mem):
        text, mode = await mem.stats()
        m = re.search(r"Memories:\s*(\d+)", text or "")
        return (int(m.group(1)) if m else None), mode

    # ------------------------------------------------------------------
    async def run(self):
        self._mem = None
        try:
            from .supervisor import keep_awake
            keep_awake()
        except Exception:
            pass
        try:
            await self._run()
        finally:
            if self._mem is not None:
                await self._mem.close()

    async def _run(self):
        st = self._load_state()
        self.cycle = st.get("cycle", 0)
        if os.path.exists(self.dl_path):
            with open(self.dl_path, encoding="utf-8") as f:
                dl = json.load(f)
            wall_start, deadline = dl["wall_start"], dl["deadline"]
        else:
            wall_start = time.time()
            deadline = wall_start + self.duration_h * 3600
            _atomic_json(self.dl_path, {"wall_start": wall_start, "deadline": deadline})

        metrics = Metrics()
        metrics.load_events(load_events(self.events_path))
        self.ledger = Ledger(self.ledger_path)
        det = InsightDetector(metrics, self.ledger, log)
        det.load_dict(st.get("det", {}))

        mem = MemFacade(log)
        self._mem = mem
        await mem.start()
        try:
            await mem.recall("FLFACT warmup", compartment=C.COMPARTMENT_FACT)
        except Exception as e:
            log(f"[mem] warmup skipped: {e}")

        poets = {"A": PoetLeg("A", C.SEQ_V, C.SEQ_CTX + 1, C.SEQ_V, log),
                 "B": PoetLeg("B", C.SEQ_V + C.SEQ_N_REGIMES, C.SEQ_CTX + 2, C.SEQ_V, log)}
        for tag, path in (("A", self.poetA_path), ("B", self.poetB_path)):
            if os.path.exists(path):
                try:
                    poets[tag].load(path)
                    log(f"[poet{tag}] resumed (updates={poets[tag].updates})")
                except Exception as e:
                    log(f"[poet{tag}] load failed ({e}); starting fresh")
        runner = CycleRunner(mem, poets, det, self.ledger, log)
        runner.load_dict(st.get("runner", {}))
        metrics.puz_probes = 0

        if not self.ledger.items:
            self._pre_register()

        last_hb = last_ckpt = last_status = last_report = last_probe = time.time()
        report_n = len([f for f in os.listdir(os.path.join(self.run_dir, "reports"))
                        if f.startswith("report_")])
        end = "unknown"
        log(f"[worker] v2 start at cycle {self.cycle}, deadline "
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
            # quota-stop (v2): events bought by statistics, not wall clock.
            # Disabled when the operator books the full window (QUOTA_ENABLED).
            if (C.QUOTA_ENABLED and
                    runner.counts.get("discoveries", 0) >= C.QUOTA_DISCOVERIES and
                    det.shock_seen() >= C.QUOTA_SHOCKS):
                end = "quota satisfied"
                break
            try:
                rec = await runner.run_cycle(c)
                self.cycle = c
                self.fails = 0
                with open(self.events_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                metrics.add(c, "seqA", rec.get("seqA_err"))
                metrics.add(c, "seqB", rec.get("seqB_err"))
                metrics.add(c, "factA", rec.get("factA_err"))
                metrics.add(c, "factB", rec.get("factB_err"))
                metrics.add(c, "puzzle", rec.get("puz_err"))
                if "puz_err" in rec:
                    runner.counts["_puz_probes"] = runner.counts.get("_puz_probes", 0) + 1
                det.on_cycle(c, rec)
                if rec.get("dt_ms", 9999) < C.SPEED_PACING_MS:
                    await asyncio.sleep((C.SPEED_PACING_MS - rec["dt_ms"]) / 1000.0)
            except Exception as e:
                self.fails += 1
                log(f"[c{c}] cycle FAILED ({self.fails}): "
                    f"{type(e).__name__}: {str(e)[:200]}")
                with open(self.events_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"c": c, "error": f"{type(e).__name__}: {str(e)[:150]}",
                                        "t": time.strftime("%H:%M:%S")}) + "\n")
                if self.fails >= C.CONSECUTIVE_FAIL_LIMIT:
                    self._save(det, runner, poets, wall_start)
                    log("circuit breaker OPEN -> checkpoint saved, exit(3)")
                    sys.exit(3)

            now = time.time()
            if now - last_hb > C.HEARTBEAT_EVERY_S:
                self._heartbeat(mem.mode)
                last_hb = now
            if now - last_ckpt > C.CHECKPOINT_EVERY_S or c % C.CHECKPOINT_EVERY_CYCLES == 0:
                self._save(det, runner, poets, wall_start)
                last_ckpt = now
            if now - last_status > C.STATUS_EVERY_S:
                snap = reports.build_snapshot(
                    self.cycle, wall_start, self.duration_h, self.max_cycles,
                    metrics, det, runner, self.ledger, mem.mode, None,
                    poets, end="running", ram_gb=ram_avail_gb())
                reports.write_status(self.run_dir, reports.render(snap))
                last_status = now
            if now - last_report > C.REPORT_EVERY_S:
                extra = reports.scan_events(self.run_dir)
                snap = reports.build_snapshot(
                    self.cycle, wall_start, self.duration_h, self.max_cycles,
                    metrics, det, runner, self.ledger, mem.mode, None,
                    poets, end="running", ram_gb=ram_avail_gb())
                snap.update(puz_methods=extra["puz_methods"], hits=extra["hits"],
                            drifts_seen=extra["drifts_seen"],
                            binned={l: reports._binned(metrics, l, self.cycle)
                                    for l in ("seqA", "seqB", "factA", "factB", "puzzle")})
                reports.write_hourly(self.run_dir, reports.render(snap, detail=True),
                                     report_n + 1)
                report_n += 1
                last_report = now
            if mem.mode == "local" and now - last_probe > 30:
                await mem.probe()
                last_probe = now
            await asyncio.sleep(0)

        # ---------------- graceful end ----------------
        log(f"[worker] ending: {end} at cycle {self.cycle}")
        self._save(det, runner, poets, wall_start)
        entries, _ = await self._mem_entries_count(mem)
        self._adjudicate(det, runner, entries, metrics)
        extra = reports.scan_events(self.run_dir)
        snap = reports.build_snapshot(
            self.cycle, wall_start, self.duration_h, self.max_cycles,
            metrics, det, runner, self.ledger, mem.mode,
            f"entries={entries}", poets, end=end, ram_gb=ram_avail_gb())
        snap.update(puz_methods=extra["puz_methods"], hits=extra["hits"],
                    drifts_seen=extra["drifts_seen"],
                    binned={l: reports._binned(metrics, l, self.cycle)
                            for l in ("seqA", "seqB", "factA", "factB", "puzzle")})
        reports.write_status(self.run_dir, reports.render(snap))
        reports.write_final(self.run_dir, reports.render(snap, detail=True), end)
        log(f"[worker] final report written; entries={entries}; bye")

    # ------------------------------------------------------------------
    async def finalize(self):
        """Rebuild everything from disk and write the final report (no cycles)."""
        st = self._load_state()
        self.cycle = st.get("cycle", 0)
        metrics = Metrics()
        metrics.load_events(load_events(self.events_path))
        self.ledger = Ledger(self.ledger_path)
        det = InsightDetector(metrics, self.ledger, log)
        det.load_dict(st.get("det", {}))
        runner = CycleRunner(None, None, det, self.ledger, log)
        runner.load_dict(st.get("runner", {}))
        with open(self.dl_path, encoding="utf-8") as f:
            dl = json.load(f)
        mem = MemFacade(log)
        await mem.start()
        entries, _ = await self._mem_entries_count(mem)
        self._adjudicate(det, runner, entries, metrics)
        extra = reports.scan_events(self.run_dir)
        snap = reports.build_snapshot(
            self.cycle, dl["wall_start"], self.duration_h, self.max_cycles,
            metrics, det, runner, self.ledger, mem.mode,
            f"entries={entries}", None, end="finalized-after-crash",
            ram_gb=ram_avail_gb())
        snap.update(puz_methods=extra["puz_methods"], hits=extra["hits"],
                    drifts_seen=extra["drifts_seen"],
                    binned={l: reports._binned(metrics, l, self.cycle)
                            for l in ("seqA", "seqB", "factA", "factB", "puzzle")})
        reports.write_status(self.run_dir, reports.render(snap))
        reports.write_final(self.run_dir, reports.render(snap, detail=True), "finalized")
        log(f"[worker] finalized from disk at cycle {self.cycle}")


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
