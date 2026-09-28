"""V4 analyzer tests: planted-effect synthetic fixture + negative fixture.
Run: python tests/test_v4_analyze.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")
    if not cond:
        FAILS.append(name)


def build_fixture(run_dir, all_discovered=False):
    """Synthetic world, temporally faithful for the analyzer.

    Episode i (per family): RECALL of rule r_{i-2} when i%3==0 and i>=2,
    else the birth episode of r_i. So every RECALL borrows a rule born two
    episodes earlier, and r_i with i%3==0 never has a birth episode of its
    own. Even-indexed rules are DISCOVERED (note attached inside episode i if
    that is non-RECALL, else episode i+1 — always before episode i+2, the
    first RECALL borrowing r_i); odd-indexed rules stay undiscovered. RECALL
    groups: i even borrows an even (discovered) rule, i odd borrows an odd
    (undiscovered) rule — 50/50.

    Planted per-episode error profiles (e20 over 20 probes):
      discovered recurrences: FULL 0, MATCHED 5, EPISODIC 20
      undiscovered recurrences: FULL 20, MATCHED 0, EPISODIC 20
    """
    os.makedirs(run_dir, exist_ok=True)
    recs = []
    n_ep = 120                     # per family; NEW 40/family -> phase C reached
    for fam in range(4):
        for i in range(n_ep):
            is_recall = (i % 3 == 0 and i >= 2)
            rid = f"f{fam}r{i - 2}" if is_recall else f"f{fam}r{i}"
            etype = "RECALL" if is_recall else ("VARIANT" if i % 3 == 1 else "NEW")
            rule_idx = int(rid.split("r")[1])
            discovered = (rule_idx % 2 == 0)
            start = i * 160
            for arm in ("FULL", "MATCHED", "EPISODIC"):
                for probe in range(1, 21):
                    c = start + 8 * (probe - 1) + 2 * fam
                    rec = {"c": c, "memory_arm": arm, "lane": "puzzle",
                           "episode_type": etype, "family": fam, "epoch": i,
                           "rule_id": rid, "rule_age": (2 if is_recall else 0),
                           "probe_idx": probe, "truth": 1,
                           "stale_candidate_present": 0, "stale_intrusion": 0,
                           "discovery": 0, "reactivation": 0,
                           "insight_kind": None, "retrieval_rank": None,
                           "notes": [], "prediction": 1, "method": "fit",
                           "error": 0}
                    if is_recall:
                        if discovered:
                            rec["error"] = {"FULL": 0,
                                            "MATCHED": 0 if probe > 5 else 1,
                                            "EPISODIC": 1}[arm]
                            rec["method"] = {"FULL": "book_test",
                                             "MATCHED": "epi_test",
                                             "EPISODIC": "fit"}[arm]
                        else:
                            rec["error"] = {"FULL": 1, "MATCHED": 0,
                                            "EPISODIC": 1}[arm]
                            rec["method"] = {"FULL": "fit", "MATCHED": "epi_test",
                                             "EPISODIC": "fit"}[arm]
                    recs.append(rec)
    # DISCOVERY notes for even rules: episode i when non-RECALL, else i+1
    def note_home(i):
        return i if not (i % 3 == 0 and i >= 2) else i + 1
    noted = set()   # (fam, i) — rules are per-family, dedup MUST be per family
    for r in recs:
        if r["memory_arm"] != "FULL" or r["probe_idx"] != 3:
            continue
        for i in (r["epoch"], r["epoch"] - 1):
            if i < 0 or i % 2 != 0 or (r["family"], i) in noted:
                continue
            if r["epoch"] == note_home(i):
                r["notes"] = [f"DISCOVERY fam={r['family']} ep={i} "
                              f"rid=f{r['family']}r{i} a=1 b=2"]
                r["discovery"] = 1
                r["insight_kind"] = "DISCOVERY"
                noted.add((r["family"], i))
    if all_discovered:
        # attach notes for the remaining (odd / RECALL-born) rules by index;
        # APPEND — a record can be the note-home of several rules, and the
        # base loop's even-rule notes must survive
        by_key = {(r["family"], r["epoch"]): r for r in recs
                  if r["memory_arm"] == "FULL" and r["probe_idx"] == 3}
        for fam in range(4):
            for i in range(n_ep):
                if i % 2 == 0 or (fam, i) in noted:
                    continue
                rec = by_key.get((fam, note_home(i)))
                if rec is None:
                    continue
                rec["notes"].append(f"DISCOVERY fam={fam} ep={i} "
                                    f"rid=f{fam}r{i} a=1 b=2")
                rec["discovery"] = 1
                rec["insight_kind"] = "DISCOVERY"
                noted.add((fam, i))
    with open(os.path.join(run_dir, "events.jsonl"), "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(r) for r in recs) + "\n")
    with open(os.path.join(run_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump({"run_status": "OK", "cycle": 999999}, f)
    with open(os.path.join(run_dir, "ledger.jsonl"), "w", encoding="utf-8") as f:
        for pid in range(1, 9):
            f.write(json.dumps({"id": f"FL-P{pid:03d}", "kind": "run",
                                "status": "REGISTERED",
                                "claim": f"V4-P0{pid}: synthetic claim {pid}",
                                "evidence": ""}) + "\n")


def run_analyzer(run_dir):
    r = subprocess.run([PY, os.path.join(ROOT, "experiments", "analyze_v4.py"),
                        "--run-dir", run_dir, "--boot", "500"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
    return r.returncode


def read_ledger(run_dir):
    rows = {}
    for line in open(os.path.join(run_dir, "ledger.jsonl"), encoding="utf-8"):
        d = json.loads(line)
        rows[d["claim"][:6]] = d["status"]
    return rows


def main():
    tmp = tempfile.mkdtemp(prefix="v4an_")
    run_dir = os.path.join(tmp, "pos")
    build_fixture(run_dir)
    check("analyzer exits 0 (positive)", run_analyzer(run_dir) == 0)
    led = read_ledger(run_dir)
    check("P01 CONFIRMED", led.get("V4-P01") == "CONFIRMED", str(led))
    check("P02 CONFIRMED (F<=M<=E planted)", led.get("V4-P02") == "CONFIRMED")
    check("P03 CONFIRMED", led.get("V4-P03") == "CONFIRMED")
    check("P04 CONFIRMED (probe-1 book_test planted)",
          led.get("V4-P04") == "CONFIRMED")
    check("P05 CONFIRMED (no intrusions planted)",
          led.get("V4-P05") == "CONFIRMED")
    check("P06 CONFIRMED (NEW/VARIANT zero)", led.get("V4-P06") == "CONFIRMED")
    check("P07 has phase-C data", led.get("V4-P07") in ("CONFIRMED", "REFUTED"))
    check("analysis_v4.md written",
          os.path.exists(os.path.join(run_dir, "analysis_v4.md")))

    # negative fixture: every rule discovered -> P01/P03 unevaluable
    run_dir2 = os.path.join(tmp, "neg")
    build_fixture(run_dir2, all_discovered=True)
    check("analyzer exits 0 (negative)", run_analyzer(run_dir2) == 0)
    led2 = read_ledger(run_dir2)
    check("P01 INCONCLUSIVE when nothing undiscovered",
          led2.get("V4-P01") == "INCONCLUSIVE", str(led2.get("V4-P01")))
    check("P03 INCONCLUSIVE when nothing undiscovered",
          led2.get("V4-P03") == "INCONCLUSIVE", str(led2.get("V4-P03")))

    shutil.rmtree(tmp, ignore_errors=True)
    print()
    print("FAILURES:", FAILS if FAILS else "none")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
