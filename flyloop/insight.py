"""Insight leg: rolling error metrics, drift-response tracking, and the
prospective prediction ledger (REGISTERED -> CONFIRMED/REFUTED/PARTIAL),
re-implementing intuition-mechanism's registry culture for the loop.

An "insight event" here = the loop abstracts a family rule from accumulated
exemplars (rule discovery) and the error series shows the restructuring
signature (sustained drop after the abstraction enters memory).
"""
import json
import time

from . import config as C


class Metrics:
    # lane aliases for drift tracking: the world fires lane "fact"/"seq", but
    # metrics are stored per arm. Aliases pool the arms for drift statistics.
    ALIASES = {"fact": ("factA", "factB"), "seq": ("seqA",), }

    def __init__(self):
        self.err = {}  # lane -> {cycle: 0/1}

    def add(self, cycle, lane, err):
        if err is None:
            return
        self.err.setdefault(lane, {})[cycle] = int(err)

    def _lane_vals(self, lane):
        lanes = self.ALIASES.get(lane, (lane,))
        out = {}
        for ln in lanes:
            out.update(self.err.get(ln, {}))
        return out

    def rolling(self, lane, cycle, w=C.ROLL_WINDOW):
        d = self._lane_vals(lane)
        vals = [v for c, v in d.items() if cycle - w < c <= cycle]
        return sum(vals) / len(vals) if vals else None

    def window_mean(self, lane, lo, hi):
        d = self._lane_vals(lane)
        vals = [v for c, v in d.items() if lo < c <= hi]
        return sum(vals) / len(vals) if vals else None

    def summary(self, cycle):
        out = {}
        for lane, d in self.err.items():
            r = self.rolling(lane, cycle)
            out[lane] = {"n": len(d), "err100": round(r, 4) if r is not None else None}
        return out

    def load_events(self, records):
        for rec in records:
            c = rec.get("c")
            if c is None:
                continue
            for lane, keys in (("seqA", ("seqA_err", "seq_err")),
                               ("seqB", ("seqB_err",)),
                               ("factA", ("factA_err", "fact_err")),
                               ("factB", ("factB_err",)),
                               ("puzzle", ("puz_err",))):
                for k in keys:
                    if rec.get(k) is not None:
                        self.add(c, lane, rec[k])
                        break


class Ledger:
    """Prospective prediction registry (see intuition-mechanism docs/RESEARCH_PLAN.md)."""

    def __init__(self, path):
        self.path = path
        self.items = []
        if path and __import__("os").path.exists(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.items.append(json.loads(line))

    def save(self):
        if not self.path:
            return
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            for it in self.items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        __import__("os").replace(tmp, self.path)

    def register(self, claim, due_cycle, kind="run", note=""):
        eid = f"FL-P{len(self.items) + 1:03d}"
        self.items.append({"id": eid, "kind": kind, "claim": claim,
                           "status": "REGISTERED", "evidence": "",
                           "registered_cycle": None, "due_cycle": due_cycle,
                           "ts": time.strftime("%Y-%m-%d %H:%M:%S"), "note": note})
        self.save()
        return eid

    def set_status(self, eid, status, evidence=""):
        for it in self.items:
            if it["id"] == eid:
                it["status"] = status
                it["evidence"] = str(evidence)[:300]
                self.save()
                return it
        return None

    def by_status(self):
        out = {}
        for it in self.items:
            out[it["status"]] = out.get(it["status"], 0) + 1
        return out


class InsightDetector:
    def __init__(self, metrics: Metrics, ledger: Ledger, log=print):
        self.m = metrics
        self.ledger = ledger
        self.log = log
        self.drift_open = []   # drift records still inside their observation window
        self.drift_done = []   # closed records
        self.insights = []     # insight events (rule abstractions etc.)
        self.sig_watch = {}    # (fam, epoch) -> {"eid", "cycle", "family", "epoch"}
        self._shocks = 0       # count of fact shock events observed (quota)

    def shock_seen(self):
        return self._shocks

    # ---------------- drift response tracking ----------------
    def on_drift(self, cycle, events):
        for ev in events:
            if ev.get("kind") == "shock":
                self._shocks += 1
            pre = self.m.rolling(ev["lane"], cycle - 1, C.DRIFT_PRE_WINDOW)
            rec = {"lane": ev["lane"], "kind": ev["kind"], "who": ev["who"],
                   "cycle": cycle, "pre": pre, "post_max": None,
                   "recovered_at": None}
            self.drift_open.append(rec)
        # keep memory bounded
        if len(self.drift_open) > 400:
            self.drift_done.extend(self.drift_open[:200])
            self.drift_open = self.drift_open[200:]

    def on_cycle(self, cycle, rec=None):
        """Called once per cycle with that cycle's event record."""
        if rec and rec.get("drifts"):
            # counted in on_drift already when the drift fired; nothing extra
            pass
        still = []
        for r in self.drift_open:
            dt = cycle - r["cycle"]
            roll = self.m.rolling(r["lane"], cycle, C.ROLL_WINDOW)
            if roll is not None:
                r["post_max"] = roll if r["post_max"] is None else max(r["post_max"], roll)
                if r["recovered_at"] is None and r["pre"] is not None and roll <= r["pre"] + 0.05:
                    r["recovered_at"] = cycle
            if dt > C.DRIFT_POST_WINDOW + 200:
                r["recovered_in"] = (r["recovered_at"] - r["cycle"]
                                     if r["recovered_at"] else None)
                self.drift_done.append(r)
            else:
                still.append(r)
        self.drift_open = still
        self._adjudicate_signatures(cycle)

    # ---------------- rule-discovery insights ----------------
    def on_discovery(self, cycle, family, epoch, a, b, evidence_ids):
        ins = {"cycle": cycle, "kind": "rule_discovery", "family": family,
               "epoch": epoch, "rule": f"y=({a}x+{b}) mod {C.PUZ_P}",
               "evidence_ids": evidence_ids[:8]}
        self.insights.append(ins)
        if len(self.insights) > 300:
            self.insights = self.insights[-200:]
        eid = self.ledger.register(
            claim=(f"fam{family} ep{epoch} signature: rolling puzzle err over "
                   f"[d+10,d+70] <= 0.6 x rolling err over [d-70,d] (d={cycle})"),
            due_cycle=cycle + 70, kind="signature",
            note=f"discovery {family}/{epoch}")
        self.sig_watch[(family, epoch)] = {"eid": eid, "cycle": cycle}
        return eid

    def _adjudicate_signatures(self, cycle):
        for key, w in list(self.sig_watch.items()):
            if w.get("eid") and self.ledger and cycle - w["cycle"] >= 70:
                d = w["cycle"]
                pre = self.m.window_mean("puzzle", d - 70, d)
                post = self.m.window_mean("puzzle", d + 10, d + 70)
                if post is None:
                    continue  # window not filled yet
                if pre is None or pre < 1e-9:
                    self.ledger.set_status(w["eid"], "PARTIAL",
                                           f"pre={pre} post={post}")
                else:
                    ratio = pre / max(post, 1e-9)
                    ok = post <= 0.6 * pre
                    self.ledger.set_status(
                        w["eid"], "CONFIRMED" if ok else "REFUTED",
                        f"pre={pre:.3f} post={post:.3f} ratio={ratio:.2f}")
                w["eid"] = None  # adjudicated

    # ---------------- persistence ----------------
    def to_dict(self):
        return {"drift_open": self.drift_open[-100:], "drift_done": self.drift_done[-400:],
                "insights": self.insights[-200:],
                "sig_watch": {f"{k[0]}:{k[1]}": v for k, v in self.sig_watch.items()}}

    def load_dict(self, d):
        self.drift_open = d.get("drift_open", [])
        self.drift_done = d.get("drift_done", [])
        self.insights = d.get("insights", [])
        self.sig_watch = {tuple(map(int, k.split(":"))): v
                          for k, v in d.get("sig_watch", {}).items()}

    def summary(self):
        rec = [r for r in self.drift_done if r.get("recovered_in") is not None]
        by_lane = {}
        for r in self.drift_done:
            s = by_lane.setdefault(r["lane"], {"n": 0, "recovered": 0, "rec_cycles": []})
            s["n"] += 1
            if r.get("recovered_in") is not None:
                s["recovered"] += 1
                s["rec_cycles"].append(r["recovered_in"])
        for lane, s in by_lane.items():
            rc = s.pop("rec_cycles")
            s["median_recover"] = sorted(rc)[len(rc) // 2] if rc else None
        return {"drift_total": len(self.drift_done) + len(self.drift_open),
                "by_lane": by_lane, "insights": len(self.insights),
                "shocks_seen": self._shocks}
