"""Periodic markdown reports: STATUS.md (always-latest), periodic reports, final."""
import json
import os
import time

from . import config as C
from . import world


def _binned(metrics, lane, cycle_max, bin_size=1000):
    d = metrics.err.get(lane, {})
    out = []
    for lo in range(0, max(cycle_max, bin_size), bin_size):
        vals = [v for c, v in d.items() if lo < c <= lo + bin_size]
        out.append((lo, round(sum(vals) / len(vals), 3) if vals else None))
    return out


def scan_events(run_dir):
    """Cheap aggregates from events.jsonl (method distribution, hits, drifts seen)."""
    path = os.path.join(run_dir, "events.jsonl")
    methods, drifts_seen = {}, 0
    hits = {"factA": [0, 0], "factB": [0, 0], "puzzle": [0, 0]}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                except Exception:
                    continue
                if r.get("drifts"):
                    drifts_seen += len(r["drifts"])
                m = r.get("puz_method")
                if m:
                    methods[m] = methods.get(m, 0) + 1
                for lane in ("factA", "factB", "puzzle"):
                    h = r.get(f"{lane}_hit")
                    if h is not None:
                        hits[lane][1] += 1
                        hits[lane][0] += int(h)
    return {"puz_methods": methods, "drifts_seen": drifts_seen, "hits": hits}


def ledger_table(ledger):
    rows = ["| id | kind | status | claim | evidence |",
            "|---|---|---|---|---|"]
    for it in ledger.items:
        rows.append(f"| {it['id']} | {it['kind']} | **{it['status']}** | "
                    f"{it['claim'][:90]} | {it['evidence'][:90]} |")
    return "\n".join(rows)


def _arm_block(arm, stats):
    """One memory arm's key numbers for the v3 status render."""
    m = stats["metrics"]
    c = stats["counts"]
    err = {lane: s.get("err100") for lane, s in m.items()}
    return (f"- **{arm}**: puzzle err100={err.get('puzzle')} "
            f"factA={err.get('factA')} factB={err.get('factB')} "
            f"seqA={err.get('seqA')} seqB={err.get('seqB')} | "
            f"probes={c.get('puz_probes')} discoveries={c.get('discoveries')} "
            f"book_test={c.get('book_test_uses')} stale={c.get('stale_intrusions')} "
            f"cold={c.get('cold')} | episodes={c.get('episodes')} | "
            f"writes={c.get('writes')} (fact {c.get('fact_writes')}, pairs "
            f"{c.get('pair_writes')}, book {c.get('book_writes')}, pads "
            f"{c.get('pad_writes')}, noise {c.get('noise')}) | readback fails "
            f"fact={c.get('fact_readback_fail')} book={c.get('rulebook_readback_fail')} "
            f"table={c.get('table_readback_fail')}")


def render_v4(snap, detail=False):
    L = []
    L.append(f"# flyloop v4 status — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    L.append("")
    L.append(f"- cycle **{snap['cycle']}**，elapsed **{snap['elapsed_h']:.2f} h** / "
             f"{snap['duration_h']:.0f} h，memory **FULL {snap.get('mode')}**，"
             f"end: {snap.get('end', 'running')}，RAM avail {snap.get('ram_gb', '?')} GB")
    L.append(f"- run_status: **{snap.get('run_status', 'OK')}**")
    q = snap.get("quotas", {})
    L.append(f"- quotas (need N{C.QUOTA_NEW}/V{C.QUOTA_VARIANT}/R{C.QUOTA_RECALL}/"
             f"s{C.QUOTA_SHOCKS}): {q}")
    pp = snap.get("pad_parity")
    if pp:
        L.append(f"- three-way write parity (FULL book + MATCHED archive vs "
                 f"EPI pads): {pp}")
    en = snap.get("entries")
    if en:
        L.append(f"- memory entries: {en}")
    L.append("")
    L.append("## arms (rolling err100)")
    for arm in ("FULL", "MATCHED", "EPISODIC"):
        L.append(_arm_block(arm, snap["arm_stats"][arm]))
    L.append("")
    if detail:
        L.append("## FULL bins (1k cycles)")
        for lane in ("puzzle", "factA", "factB", "seqA", "seqB"):
            bins = snap.get("binned", {}).get(lane)
            if bins:
                cells = " | ".join(f"{lo//1000}k:{v}" for lo, v in bins if v is not None)
                L.append(f"- {lane}: {cells}")
        L.append("")
        if snap.get("insights"):
            L.append(f"## FULL insights ({len(snap['insights'])})")
            for ins in snap["insights"][-30:]:
                L.append(f"- c{ins['cycle']} fam={ins['family']} ep={ins['epoch']} "
                         f"rule `{ins['rule']}`")
            L.append("")
        if snap.get("expected"):
            L.append(f"- world expectation: {snap['expected']}")
        L.append("## prediction ledger")
        L.append(ledger_table(snap["ledger"]))
        L.append("")
    return "\n".join(L) + "\n"


def render(snap, detail=False):
    L = []
    L.append(f"# flyloop status — {time.strftime('%Y-%m-%d %H:%M:%S')}")
    L.append("")
    poets = snap.get("poets") or {}
    dev = ", ".join(f"{tag}:{p['device']}(u={p['updates']})" for tag, p in poets.items()) or "?"
    L.append(f"- cycle **{snap['cycle']}**，elapsed **{snap['elapsed_h']:.2f} h** / "
             f"{snap['duration_h']:.0f} h，memory **{snap['mode']}**，poets {dev}")
    L.append(f"- end condition: {snap.get('end', 'running')}，RAM avail "
             f"{snap.get('ram_gb', '?')} GB")
    L.append("")
    L.append("## rolling error (window=100)")
    for lane, s in snap["metrics"].items():
        L.append(f"- **{lane}**: n={s['n']}, err100={s['err100']}")
    L.append("")
    L.append("## counts")
    c = snap["counts"]
    L.append(f"- writes={c.get('writes')} (fact {c.get('fact_writes')}, pairs "
             f"{c.get('pair_writes')}, rules {c.get('rule_writes')}, noise {c.get('noise')}), "
             f"rejected={c.get('rejected')}, recalls={c.get('recalls')}")
    L.append(f"- rule discoveries = **{len([1 for v in snap.get('disc', {}).values() if v.get('done')])}**"
             f"，cold={c.get('cold')}，book writes={c.get('book_writes')}，"
             f"readback_fail={c.get('readback_fail')}")
    if snap.get("puz_methods"):
        L.append(f"- puzzle prediction methods: {snap['puz_methods']}")
    if snap.get("hits"):
        h = snap["hits"]
        L.append(f"- recall hit: factA {h['factA'][0]}/{h['factA'][1]}, "
                 f"factB {h['factB'][0]}/{h['factB'][1]}, puzzle {h['puzzle'][0]}/{h['puzzle'][1]}")
    if snap.get("mem_stats"):
        L.append(f"- flymemory: `{snap['mem_stats']}`")
    L.append("")
    ds = snap.get("drift_summary")
    if ds:
        L.append("## drift response")
        L.append(f"- total drift events observed: {ds.get('drift_total')} "
                 f"(shocks seen {ds.get('shocks_seen')}/{C.QUOTA_SHOCKS}), "
                 f"events in log: {snap.get('drifts_seen')}")
        for lane, s in ds.get("by_lane", {}).items():
            L.append(f"- **{lane}**: {s['recovered']}/{s['n']} recovered, "
                     f"median {s.get('median_recover')} cycles")
        L.append("")
    if detail:
        L.append("## error by 1000-cycle bins")
        for lane in ("seqA", "seqB", "factA", "factB", "puzzle"):
            bins = snap.get("binned", {}).get(lane)
            if bins:
                cells = " | ".join(f"{lo//1000}k:{v}" for lo, v in bins if v is not None)
                L.append(f"- {lane}: {cells}")
        L.append("")
        L.append("## A/B arms (cumulative)")
        ct = snap["counts"]
        L.append(f"- fact recall arm: hit {ct.get('factA_hit')}/{ct.get('factA_n')} | "
                 f"state_lookup arm: hit {ct.get('factB_hit')}/{ct.get('factB_n')}")
        L.append("")
        if snap.get("insights"):
            L.append(f"## insights ({len(snap['insights'])})")
            for ins in snap["insights"][-30:]:
                L.append(f"- c{ins['cycle']} fam={ins['family']} ep={ins['epoch']} "
                         f"rule `{ins['rule']}`")
            L.append("")
        if snap.get("expected"):
            L.append(f"- world drift expectation: {snap['expected']}")
        L.append("## prediction ledger")
        L.append(ledger_table(snap["ledger"]))
        L.append("")
    return "\n".join(L) + "\n"


def build_snapshot(cycle, wall_start, duration_h, max_cycles, metrics, det, runner,
                   ledger, mem_mode, mem_stats, poets, end="running", ram_gb=None):
    return {
        "cycle": cycle, "elapsed_h": (time.time() - wall_start) / 3600.0,
        "duration_h": duration_h, "max_cycles": max_cycles, "end": end,
        "mode": mem_mode, "device": "?", "updates": 0, "ram_gb": ram_gb,
        "poets": ({tag: {"device": p.device, "updates": p.updates}
                   for tag, p in poets.items()} if poets else {}),
        "metrics": metrics.summary(cycle), "counts": runner.counts,
        "disc": runner.disc, "drift_summary": det.summary(),
        "insights": det.insights, "ledger": ledger,
        "mem_stats": (mem_stats or "")[:120],
        "expected": world.expected_counts(cycle),
    }


def write_status(run_dir, snap_text):
    path = os.path.join(run_dir, "STATUS.md")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(snap_text)
    os.replace(tmp, path)


def write_hourly(run_dir, text, n):
    d = os.path.join(run_dir, "reports")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"report_{n:02d}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def write_final(run_dir, text, end):
    path = os.path.join(run_dir, "final_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path
