"""Overnight worker, v4: three memory arms through the identical world.

Robustness contract (v1/v2/v3, unchanged): every cycle try/except; N
consecutive failures trip a circuit breaker -> checkpoint -> exit(3);
checkpoint every 50 cycles / 120s; heartbeat 15s; STATUS 60s; periodic
reports; service-down -> local mirror with auto-switch-back; RAM red line;
deadline in deadline.json.

v4 additions (V4_DESIGN.md):
  - three arms: FULL (rule registry + book_test), MATCHED (episodic pair-table
    archive + epi_test, the SAME unique-match decision rule over raw pairs),
    EPISODIC (tables + fit only). One sandbox FlyMemory instance per arm
    (ports MEM_PORT / MEM_PORT_MATCHED / MEM_PORT_EPI).
  - three-way write parity: EPISODIC's padding writes byte-match
    FULL.book + MATCHED.archive combined (PadSync charges per source arm).
  - quota-gated noise phases (world.puz_phase on NEW-episode counts).
  - pre-registered V4-P01..P08; endpoint verdicts applied by
    experiments/analyze_v4.py (cluster bootstrap by rule lineage), not here.
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

ARMS = tuple(os.environ.get(
    "FLYLOOP_ARMS", "FULL,MATCHED,EPISODIC").split(","))
# V7 factorial runs swap arms via env (e.g. "FULL-RAW,MATCHED-VER"); every
# arm gets its OWN service instance — two arms on one store cross-contaminate
# (V7C lesson: FULL and FULL-RAW sharing a store I1-superseded each other's
# book entries, zeroing the write-depth contrast). Ports come as a comma
# list aligned with ARMS order.
_PORTS = os.environ.get(
    "FLYLOOP_PORTS", ",".join(str(p) for p in (C.MEM_PORT, C.MEM_PORT_MATCHED,
                                               C.MEM_PORT_EPI)))
MEM_URLS = {arm: f"http://{C.MEM_HOST}:{port}/mcp"
            for arm, port in zip(ARMS, _PORTS.split(","))}
PREDSET = os.environ.get("FLYLOOP_PREDSET", "V4")


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
        self._divergence_checked = False

    # ------------------------------------------------------------------
    def _load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self, dets, runners, poets, wall_start):
        _atomic_json(self.state_path, {
            "cycle": self.cycle, "wall_start": wall_start,
            "run_status": self.run_status,
            "dets": {arm: dets[arm].to_dict() for arm in ARMS},
            "runners": {arm: runners[arm].to_dict() for arm in ARMS},
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

    # -- registered predictions (registered before the first cycle) ----------
    def _pre_register(self):
        cmax = self.max_cycles
        r = self.ledger.register
        if PREDSET == "V7A":
            claims = {
                "V7-P01": "V7-P01 (support dominance): |dE20(F - F-RAW)| < "
                          "|dE20(M - M-VER)| under eps=0.25 -- support size "
                          "explains more of the advantage than write "
                          "verification (cluster CIs; cross-run pairing with "
                          "V5B as the verified/raw reference cells)",
                "V7-P02": "V7-P02: unverified full-support rule writes hurt -- "
                          "dE20(F-RAW vs F) > 0 (poisoned rules covering all x)",
                "V7-P03": "V7-P03: verified sparse archive helps -- "
                          "dE20(M-VER vs M) <= 0",
                "V7-P04": "V7-P04: SIR(F-RAW) > SIR(F) -- poisoned rules "
                          "intrude more (absolute counts reported, floor-gated)",
                "V7-P05": "V7-P05: interaction sign -- the write-verification "
                          "effect is larger at full support than at sparse: "
                          "(dW_full - dW_sparse) > 0",
            }
            for pid, claim in claims.items():
                r(claim, cmax, "run", "V7 Phase A factorial; cross-run pairing "
                  "with V5B; adjudication experiments/compare_v7.py")
            log("[ledger] pre-registered 5 v7 Phase A predictions")
            return
        if PREDSET == "RSI0":
            # RSI-0 G1 (RSI0_DESIGN.md §5): parent g0 + M1 (BOOK_CAP 5 -> 13).
            r("RSI0-G1-P01 (accept M1 iff): FULL E20 on discovered-recurrence "
              "RECALL episodes < 2.347 (g0 point) with cluster-bootstrap CI "
              "wholly below it", cmax, "run",
              "parent = v6t_20260928_2159; evaluator identical")
            r("RSI0-G1-P02 (mechanism): the no-candidate share of probe-1 "
              "failures shrinks vs g0's 15/31 (the floor M1 targets)",
              cmax, "run", "")
            r("RSI0-G1-P03 (no-harm): probe-1 recovery stays >= g0's 38.8%",
              cmax, "run", "")
            log("[ledger] pre-registered 3 RSI0-G1 predictions")
            return
        if PREDSET == "RSI0G2":
            # RSI-0 G2 (feasible re-encoding of M1): per-rule entries at
            # cap 13, tolerant 0.6, eps 0.25. Parent = g0 (2.347).
            r("RSI0-G2-P01 (accept iff): FULL E20 on discovered-recurrence "
              "RECALL episodes < 2.347 (g0 point) with cluster-bootstrap CI "
              "wholly below it — per-rule encoding rescues M1's intent",
              cmax, "run", "parent = v6t_20260928_2159")
            r("RSI0-G2-P02 (mechanism): rulebook_readback_fail stays < 5% of "
              "book_writes (G1's failure mode: 69% dead writes)",
              cmax, "run", "")
            r("RSI0-G2-P03 (coverage): probe-1 book_test hits >= 38.8% "
              "(g0 level) — the no-candidate floor M1 targeted shrinks",
              cmax, "run", "")
            log("[ledger] pre-registered 3 RSI0-G2 predictions")
            return
        if PREDSET == "V7C":
            # V7C: write-depth sign n-extension at the exact matcher
            # (V7A cells: dW=-0.99 CI[-2.29,+0.31], sign unresolved)
            r("V7C-P01: the write-depth sign resolves — dE20(F-RAW - F) on "
              "RECALL episodes with cluster-bootstrap CI excluding 0 "
              "(pooled post-hoc with V7A cells, same schedule/seed)",
              cmax, "run", "band: resolvable iff CI width < 1.5")
            log("[ledger] pre-registered 1 v7C prediction")
            return
        r("V4-P01 (primary, the V3-P06 fix): recurrences of DISCOVERED rules "
          "show a larger F-vs-E benefit than recurrences of UNDISCOVERED "
          "rules; cluster-bootstrap CI of the contrast excludes 0",
          cmax, "run", "requires the pilot-calibrated undiscovered fraction")
        r("V4-P02 (primary, disentanglement): on recurrences of discovered "
          "rules E20 orders F <= M <= E (both steps positive); F-M ~ 0 -> "
          "matcher-dominant, F-M > 0 -> compression adds",
          cmax, "run", "")
        r("V4-P03: on recurrences of UNDISCOVERED rules MATCHED beats FULL "
          "(dE20 M-F < 0) — the raw-pair archive wins where abstraction "
          "failed; the winning representation flips with discovery success",
          cmax, "run", "")
        r("V4-P04: probe-1 recovery exists — FULL book_test fires at probe 1 "
          "on RECALL episodes of discovered rules >= 40% (pre-fold interface)",
          cmax, "run", "")
        r("V4-P05: stale intrusion rate SIR(FULL) <= 1.5 x SIR(EPISODIC) in "
          "the three-arm world",
          cmax, "run", "")
        r("V4-P06 (NC1): VARIANT and NEW contrasts ~ 0 for F-E (|mean dE20| "
          "< 0.05) — the advantage stays recurrence-specific",
          cmax, "run", "")
        r("V4-P07: quota-gated phase C is reached and the F-E advantage "
          "persists there (point estimate > 0)",
          cmax, "run", "")
        r("V4-P08 (NC2): fact lane shows no regression in any arm "
          "(phase-C err <= 2x phase-A err and <= 0.20 absolute)",
          cmax, "run", "")
        log("[ledger] pre-registered 8 v4 predictions")

    # ------------------------------------------------------------------
    def _check_divergence(self, recs):
        """Early-run alarm (V7A lesson): two non-EPISODIC memory arms whose
        (method, error) sequences are IDENTICAL past ~600 cycles means one
        arm has lost its memory-read path -- say so LOUDLY at 10 min instead
        of burning 2 h."""
        if self._divergence_checked or self.cycle < 600:
            return
        sig = {}
        for r in recs:
            if r.get("lane") == "puzzle" and r.get("memory_arm") != "EPISODIC":
                sig.setdefault(r["memory_arm"], []).append(
                    (r.get("method"), r.get("error")))
        names = sorted(sig)
        if len(names) >= 2 and len(sig[names[0]]) >= 400:
            same = all(sig[a] == sig[names[0]] for a in names)
            if same:
                self.run_status = "ENGINEERING_INVALID:arm-divergence-failure"
                log("[PREFLIGHT-ALARM] arms produced IDENTICAL method+error "
                    f"sequences over {len(sig[names[0]])} probes -- a memory "
                    "read path is dead (V7A fingerprint). Marking run invalid.")
        self._divergence_checked = True

    # ------------------------------------------------------------------
    def _quota_state(self, runF, detF):
        ep = runF.counts["episodes"]
        return {"NEW": ep["NEW"], "VARIANT": ep["VARIANT"], "RECALL": ep["RECALL"],
                "shocks": detF.shock_seen()}

    def _quotas_met(self, runF, detF):
        q = self._quota_state(runF, detF)
        return (q["NEW"] >= C.QUOTA_NEW and q["VARIANT"] >= C.QUOTA_VARIANT
                and q["RECALL"] >= C.QUOTA_RECALL and q["shocks"] >= C.QUOTA_SHOCKS)

    def _engineering_check(self, runners, entries):
        """Tripwires that void the run as a hypothesis test (V3 §14)."""
        bad = []
        for arm, run in runners.items():
            ct = run.counts
            rb = (ct.get("fact_readback_fail", 0) + ct.get("rulebook_readback_fail", 0)
                  + ct.get("table_readback_fail", 0))
            writes = max(ct.get("fact_writes", 0) + ct.get("book_writes", 0)
                         + ct.get("pair_writes", 0) + ct.get("epireg_writes", 0), 1)
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

        metrics = {arm: Metrics() for arm in ARMS}
        for arm in ARMS:
            metrics[arm].load_events(load_events(self.events_path), arm=arm)
        self.ledger = Ledger(self.ledger_path)
        dets = {arm: InsightDetector(metrics[arm], self.ledger, log, signatures=False)
                for arm in ARMS}
        for arm in ARMS:
            dets[arm].load_dict(st.get("dets", {}).get(arm, {}))

        mems = {arm: MemFacade(log, MEM_URLS[arm]) for arm in ARMS}
        self._mems = list(mems.values())
        for arm in ARMS:
            await mems[arm].start()
        try:
            for arm in ARMS:
                await mems[arm].recall("FLFACT warmup", compartment=C.COMPARTMENT_FACT)
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
        runners = {}
        for arm in ARMS:
            runners[arm] = CycleRunner(mems[arm], poets[arm], dets[arm],
                                       self.ledger, log, arm=arm, pad_sync=pad)
            runners[arm].load_dict(st.get("runners", {}).get(arm, {}))
        if self._pre_register_needed:
            self._pre_register()

        last_hb = last_ckpt = last_status = last_report = last_probe = time.time()
        report_n = len([f for f in os.listdir(os.path.join(self.run_dir, "reports"))
                        if f.startswith("report_")])
        end = "unknown"
        log(f"[worker] v4 start at cycle {self.cycle} "
            f"(arms FULL@{C.MEM_PORT} / MATCHED@{C.MEM_PORT_MATCHED} / "
            f"EPISODIC@{C.MEM_PORT_EPI}), deadline "
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
            if C.QUOTA_ENABLED and self._quotas_met(runners[ARMS[0]], dets[ARMS[0]]):
                end = "quota satisfied"
                break
            try:
                t0 = time.perf_counter()
                recs = {}
                for arm in ARMS:
                    recs[arm] = await runners[arm].run_cycle(c)
                self.cycle = c
                self.fails = 0
                with open(self.events_path, "a", encoding="utf-8") as f:
                    for arm in ARMS:
                        f.write(json.dumps(recs[arm], ensure_ascii=False) + "\n")
                for arm in ARMS:
                    rec = recs[arm]
                    met = metrics[arm]
                    met.add(c, "seqA", rec.get("seqA_err"))
                    met.add(c, "seqB", rec.get("seqB_err"))
                    met.add(c, "factA", rec.get("factA_err"))
                    met.add(c, "factB", rec.get("factB_err"))
                    if rec.get("lane") == "puzzle":
                        met.add(c, "puzzle", rec.get("error"))
                    dets[arm].on_cycle(c, rec)
                if c == 600:
                    self._check_divergence(list(recs.values()))
                dt = (time.perf_counter() - t0) * 1000
                if dt < C.SPEED_PACING_MS * len(ARMS):
                    await asyncio.sleep((C.SPEED_PACING_MS * len(ARMS) - dt) / 1000.0)
            except Exception as e:
                self.fails += 1
                log(f"[c{c}] cycle FAILED ({self.fails}): "
                    f"{type(e).__name__}: {str(e)[:200]}")
                with open(self.events_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"c": c, "error": f"{type(e).__name__}: {str(e)[:150]}",
                                        "t": time.strftime("%H:%M:%S")}) + "\n")
                if self.fails >= C.CONSECUTIVE_FAIL_LIMIT:
                    self.run_status = "ENGINEERING_INVALID:consecutive-failures"
                    self._save(dets, runners, poets, wall_start)
                    log("circuit breaker OPEN -> checkpoint saved, exit(3)")
                    sys.exit(3)

            now = time.time()
            if now - last_hb > C.HEARTBEAT_EVERY_S:
                self._heartbeat("/".join(mems[arm].mode for arm in ARMS))
                last_hb = now
            if now - last_ckpt > C.CHECKPOINT_EVERY_S or c % C.CHECKPOINT_EVERY_CYCLES == 0:
                self._save(dets, runners, poets, wall_start)
                last_ckpt = now
            if now - last_status > C.STATUS_EVERY_S:
                snap = self._snap(c, wall_start, metrics, dets, runners, pad,
                                  mems, poets, end="running")
                reports.write_status(self.run_dir, reports.render_v4(snap))
                last_status = now
            if now - last_report > C.REPORT_EVERY_S:
                snap = self._snap(c, wall_start, metrics, dets, runners, pad,
                                  mems, poets, end="running", detail=True)
                reports.write_hourly(self.run_dir, reports.render_v4(snap, detail=True),
                                     report_n + 1)
                report_n += 1
                last_report = now
            if now - last_probe > 30:
                for arm in ARMS:
                    if mems[arm].mode == "local":
                        await mems[arm].probe()
                last_probe = now
            await asyncio.sleep(0)

        # ---------------- graceful end ----------------
        log(f"[worker] ending: {end} at cycle {self.cycle}")
        self._save(dets, runners, poets, wall_start)
        entries = {}
        for arm in ARMS:
            n, _ = await self._mem_entries_count(mems[arm])
            entries[arm] = n
        bad = self._engineering_check(runners, entries)
        if bad:
            self.run_status = "ENGINEERING_INVALID:" + ";".join(bad)[:150]
        snap = self._snap(self.cycle, wall_start, metrics, dets, runners, pad,
                          mems, poets, end=end, detail=True, entries=entries)
        reports.write_status(self.run_dir, reports.render_v4(snap))
        reports.write_final(self.run_dir, reports.render_v4(snap, detail=True), end)
        log(f"[worker] final report written; entries={entries}; "
            f"run_status={self.run_status}; bye")

    def _snap(self, c, wall_start, metrics, dets, runners, pad, mems, poets,
              end="running", detail=False, entries=None):
        snap = reports.build_snapshot(
            c, wall_start, self.duration_h, self.max_cycles,
            metrics[ARMS[0]], dets[ARMS[0]], runners[ARMS[0]], self.ledger,
            mems[ARMS[0]].mode, None, poets[ARMS[0]] if poets else None,
            end=end, ram_gb=ram_avail_gb())
        snap.update(arm_stats={
            arm: {"metrics": metrics[arm].summary(c), "counts": runners[arm].counts}
            for arm in ARMS},
            pad_parity=pad.parity(), run_status=self.run_status,
            entries=entries or {}, quotas=self._quota_state(runners[ARMS[0]], dets[ARMS[0]]),
            expected=world.expected_counts(c))
        return snap

    async def _mem_entries_count(self, mem):
        text, mode = await mem.stats()
        m = re.search(r"Memories:\s*(\d+)", text or "")
        return (int(m.group(1)) if m else None), mode

    # ------------------------------------------------------------------
    async def finalize(self):
        """Rebuild everything from disk and write the final report (no cycles).
        Endpoint verdicts come from experiments/analyze_v4.py, not here."""
        st = self._load_state()
        self.cycle = st.get("cycle", 0)
        self.run_status = st.get("run_status", "OK")
        metrics = {arm: Metrics() for arm in ARMS}
        for arm in ARMS:
            metrics[arm].load_events(load_events(self.events_path), arm=arm)
        self.ledger = Ledger(self.ledger_path)
        dets = {arm: InsightDetector(metrics[arm], self.ledger, log, signatures=False)
                for arm in ARMS}
        for arm in ARMS:
            dets[arm].load_dict(st.get("dets", {}).get(arm, {}))
        runners = {}
        for arm in ARMS:
            r = CycleRunner(None, None, dets[arm], self.ledger, log, arm=arm)
            r.load_dict(st.get("runners", {}).get(arm, {}))
            runners[arm] = r
        with open(self.dl_path, encoding="utf-8") as f:
            dl = json.load(f)
        mems = {arm: MemFacade(log, MEM_URLS[arm]) for arm in ARMS}
        for arm in ARMS:
            await mems[arm].start()
        entries = {}
        for arm in ARMS:
            n, _ = await self._mem_entries_count(mems[arm])
            entries[arm] = n
        bad = self._engineering_check(runners, entries)
        if bad and self.run_status == "OK":
            self.run_status = "ENGINEERING_INVALID:" + ";".join(bad)[:150]
        pad = PadSync()
        snap = self._snap(self.cycle, dl["wall_start"], metrics, dets, runners,
                          pad, mems, None, end="finalized-after-crash",
                          detail=True, entries=entries)
        reports.write_status(self.run_dir, reports.render_v4(snap))
        reports.write_final(self.run_dir, reports.render_v4(snap, detail=True),
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
