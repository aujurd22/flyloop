"""Deterministic environment: every ground truth is a pure function of position.

This is what makes crash-resume trivial (the world can always be recomputed)
and lets the ledger pre-register predictions about drift responses.
"""
import hashlib
import math

from . import config as C


def _rng(*args):
    """Deterministic numpy Generator from an arbitrary key tuple."""
    import numpy as np
    key = hashlib.sha256(repr(("flyloop", C.SEED, *args)).encode()).digest()
    return np.random.default_rng(int.from_bytes(key[:8], "big"))


# ---------------------------------------------------------------- fact lane ----
def fact_period(station: int) -> int:
    return C.FACT_PERIOD0 + C.FACT_PERIOD_STEP * station


def fact_channel(station: int, cycle: int) -> str:
    """Channel of a station at a cycle. Rotates each period; shocks jump."""
    base = int(_rng("fact", "base", station).integers(0, 5))
    rot = cycle // fact_period(station)
    jump = 0
    n_shocks = cycle // C.FACT_SHOCK_EVERY
    for k in range(1, int(n_shocks) + 1):
        s = int(_rng("fact", "shock", k).integers(0, C.FACT_STATIONS))
        if s == station:
            jump += int(_rng("fact", "shockjump", k).integers(1, 5))
    return C.FACT_DOMAIN[(base + rot + jump) % 5]


def fact_drift_events(cycle: int) -> list:
    """Drift events *at* this exact cycle (for event logging): station rotations + shock."""
    evs = []
    for st in range(C.FACT_STATIONS):
        if cycle > 0 and cycle % fact_period(st) == 0:
            evs.append(("rotate", st))
    if cycle > 0 and cycle % C.FACT_SHOCK_EVERY == 0:
        evs.append(("shock", int(_rng("fact", "shock", cycle // C.FACT_SHOCK_EVERY).integers(0, C.FACT_STATIONS))))
    return evs


def fact_station_at(cycle: int, offset: int = 0) -> int:
    r = _rng("fact", "query", cycle, offset)
    return int(r.integers(0, C.FACT_STATIONS))


def fact_query(station: int) -> str:
    return f"车站 st-{station:02d} 当前渠道是哪个？"


# ---------------------------------------------------------------- seq lane -----
# The stream is built in independent blocks of 512 symbols. Each block starts
# from a hashed seed symbol and follows a regime-specific Markov matrix, so
# symbol(t) is a pure function of t (blocks are regenerated on demand).
SEQ_BLOCK = 512

_MATRICES = None


def seq_matrices():
    global _MATRICES
    if _MATRICES is None:
        import numpy as np
        mats = []
        for r in range(C.SEQ_N_REGIMES):
            rng = _rng("seq", "matrix", r)
            # sparse-ish transition rows: a few strong successors per symbol
            m = rng.dirichlet(alpha=[0.35] * C.SEQ_V, size=C.SEQ_V).astype(np.float64)
            mats.append(m)
        _MATRICES = mats
    return _MATRICES


def seq_regime(pos: int) -> int:
    return (pos // C.SEQ_REGIME_LEN) % C.SEQ_N_REGIMES


def seq_block_symbols(block: int) -> list:
    import numpy as np
    rng = _rng("seq", "block", block)
    mats = seq_matrices()
    s = int(rng.integers(0, C.SEQ_V))
    out = []
    for i in range(SEQ_BLOCK):
        pos = block * SEQ_BLOCK + i
        out.append(s)
        s = int(rng.choice(C.SEQ_V, p=mats[seq_regime(pos)][s]))
    return out


def seq_symbol(pos: int) -> int:
    b, i = divmod(pos, SEQ_BLOCK)
    return seq_block_symbols(b)[i]


def seq_context(cycle: int, ctx: int = None) -> list:
    """Context window ending at position cycle-1 (the model predicts stream[cycle])."""
    ctx = ctx or C.SEQ_CTX
    start = max(0, cycle - ctx)
    return [seq_symbol(p) for p in range(start, cycle)]


# stream B (identifiability arm): same underlying symbol process, but each
# context is prefixed with a regime marker token 16+r. The regime is a pure
# function of position, so this is exactly the "external information" opening
# from the P15-f regime theorem / P30 information-limit statement.
SEQ_B_MARKER = 16  # tokens 16..18 = regime markers (vocab 19)


def seq_b_context(cycle: int, ctx: int = None) -> list:
    ctx = ctx or C.SEQ_CTX
    start = max(0, cycle - ctx)
    return [SEQ_B_MARKER + seq_regime(cycle)] + [seq_symbol(p) for p in range(start, cycle)]


# ---------------------------------------------------------------- puzzle lane --
# v4: episodes have VARIABLE lengths in probes (config.EPISODE_PROBE_LENS).
# Episode boundaries are prefix sums of 8*n_probes cycles; a family is probed
# at cycles c with c%2==0 and (c//2)%4==f (unchanged cadence — cycle.py's lane
# alternation depends on it), so an episode of n probes lasts 8n cycles and
# receives exactly n of the family's probes. Short episodes end before the
# abstraction loop completes -> discovery-failure variation (V4_DESIGN §3).
def puz_period(fam: int) -> int:
    """Deprecated in v4 (variable lengths); kept for callers that only need a
    scale reference — the mean episode length in cycles."""
    return C.PUZ_PERIOD0 + C.PUZ_PERIOD_STEP * fam


_SCHEDULE = None


def puz_schedule():
    """{fam: [episode, ...]} where episode = {i, type, rule_id, a, b, gap,
    n_probes, start_cycle, end_cycle}.

    NEW     fresh (a,b), never used in this family (future RECALL candidate)
    VARIANT fresh (a,b) drawn NEAR the previous rule (nonzero deltas) — the
            stale-memory trap and the NC1 negative control
    RECALL  the exact rule active k epochs ago, k ~ uniform{2,3,4,5}
    """
    global _SCHEDULE
    if _SCHEDULE is not None:
        return _SCHEDULE
    sched = {}
    for fam in range(C.PUZ_FAMILIES):
        rng = _rng("puz", "sched", fam)
        episodes = []
        used = set()
        by_index = {}          # epoch -> rule_id
        rules = {}             # rule_id -> (a, b)
        counter = 0
        cycle = 0
        i = 0
        while cycle < C.SCHEDULE_HORIZON and i < C.MAX_EPISODES_V4:
            u = float(rng.random())
            can_recall = i >= min(C.RECALL_GAPS)
            if i == 0:
                typ = "NEW"
            elif can_recall and u < C.EPISODE_MIX["NEW"]:
                typ = "NEW"
            elif can_recall and u < (C.EPISODE_MIX["NEW"]
                                     + C.EPISODE_MIX["VARIANT"]):
                typ = "VARIANT"
            elif can_recall:
                typ = "RECALL"
            else:
                typ = "NEW" if u < 0.5 else "VARIANT"
            gap = 0
            if typ == "RECALL":
                valid = [g for g in C.RECALL_GAPS if g <= i]
                gap = int(rng.choice(valid))
                src = i - gap
                rid = by_index[src]
                a, b = rules[rid]
            elif typ == "VARIANT":
                pa, pb = episodes[-1]["a"], episodes[-1]["b"]
                a = (pa + int(rng.choice([1, 2, C.PUZ_P - 1, C.PUZ_P - 2]))) % C.PUZ_P
                b = (pb + int(rng.choice([1, 2, 3, C.PUZ_P - 1, C.PUZ_P - 2, C.PUZ_P - 3]))) % C.PUZ_P
                if a == 0:
                    a = 1
                rid = f"f{fam}r{counter}"; counter += 1
                rules[rid] = (a, b)
            else:  # NEW
                # only p*(p-1) = 156 distinct rules exist per family; cap the
                # draw and fall back to a VARIANT of the previous rule (the
                # cap binds only near the end of the horizon)
                for _ in range(200):
                    a = int(rng.integers(1, C.PUZ_P))
                    b = int(rng.integers(0, C.PUZ_P))
                    if (a, b) not in used:
                        break
                else:
                    a, b = episodes[-1]["a"], episodes[-1]["b"]
                    typ = "VARIANT"
                rid = f"f{fam}r{counter}"; counter += 1
                rules[rid] = (a, b)
            used.add((a, b))
            by_index[i] = rid
            n_probes = int(rng.choice(C.EPISODE_PROBE_LENS, p=C.EPISODE_PROBE_WEIGHTS))
            episodes.append({"i": i, "type": typ, "rule_id": rid,
                             "a": a, "b": b, "gap": gap, "n_probes": n_probes,
                             "start_cycle": cycle,
                             "end_cycle": cycle + C.PUZ_PROBE_CADENCE * n_probes})
            cycle = episodes[-1]["end_cycle"]
            i += 1
        sched[fam] = episodes
    _SCHEDULE = sched
    return sched


def puz_epoch(fam: int, cycle: int) -> int:
    """Index of the episode whose [start_cycle, end_cycle) contains cycle."""
    eps = puz_schedule()[fam]
    lo, hi = 0, len(eps) - 1
    if cycle >= eps[-1]["end_cycle"]:
        return len(eps) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if cycle < eps[mid]["end_cycle"]:
            hi = mid
        else:
            lo = mid + 1
    return lo


def puz_episode(fam: int, cycle: int) -> dict:
    return puz_schedule()[fam][puz_epoch(fam, cycle)]


def puz_rule(fam: int, cycle: int):
    ep = puz_episode(fam, cycle)
    return ep["a"], ep["b"]


def puz_episode_counts(cycle: int) -> dict:
    """Cumulative NEW/VARIANT/RECALL episode starts at or before `cycle`."""
    counts = {"NEW": 0, "VARIANT": 0, "RECALL": 0}
    for fam in range(C.PUZ_FAMILIES):
        for ep in puz_schedule()[fam]:
            if ep["start_cycle"] <= cycle:
                counts[ep["type"]] += 1
            else:
                break
    return counts


def puz_phase(cycle: int) -> str:
    """Quota-gated noise phase: advance on cumulative NEW-episode starts
    (pooled over families), never on cycle thresholds (V3 P07/P08 lesson)."""
    n_new = puz_episode_counts(cycle)["NEW"]
    phase = C.NOISE_PHASE_GATES[0][0]
    for name, gate in C.NOISE_PHASE_GATES:
        if n_new >= gate:
            phase = name
    return phase


def puz_rotation_cycle(fam: int, epoch: int) -> int:
    eps = puz_schedule()[fam]
    return eps[epoch]["start_cycle"] if epoch < len(eps) else None


def puz_probe(fam: int, cycle: int):
    """One revealed example pair + a probe x whose y is hidden until scored.
    V5: the revealed y1 is corrupted with probability NOISE_EPS (measurement
    noise — truth stays exact; the flip is a pure function of the same keys,
    so all arms see identical observations)."""
    r = _rng("puz", "probe", fam, cycle)
    a, b = puz_rule(fam, cycle)
    x1 = int(r.integers(0, C.PUZ_P))
    xp = int(r.integers(0, C.PUZ_P))
    y1 = (a * x1 + b) % C.PUZ_P
    if C.NOISE_EPS > 0 and float(r.random()) < C.NOISE_EPS:
        y1 = (y1 + int(r.integers(1, C.PUZ_P))) % C.PUZ_P
    truth = (a * xp + b) % C.PUZ_P
    return (x1, y1), xp, truth


def puz_rotation_events(cycle: int) -> list:
    """Episode boundaries at this exact cycle (one per family), for the
    drift-event log and insight detector."""
    evs = []
    if cycle <= 0:
        return evs
    for f in range(C.PUZ_FAMILIES):
        eps = puz_schedule()[f]
        # bisect: does any episode START at this cycle?
        lo, hi = 0, len(eps) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if eps[mid]["start_cycle"] < cycle:
                lo = mid + 1
            else:
                hi = mid
        if lo < len(eps) and eps[lo]["start_cycle"] == cycle:
            evs.append(("rotate", f))
    return evs


# ---------------------------------------------------------------- noise --------
def distractor_text(cycle: int) -> str:
    r = _rng("noise", cycle)
    words = []
    for _ in range(14):
        h = hashlib.md5(r.bytes(8)).hexdigest()[:7]
        words.append(f"zx{h}")
    return "噪声条目 " + " ".join(words)


def noise_every(cycle: int) -> int:
    """Three-phase distractor pressure, gated on cumulative NEW episodes
    (pure function of the schedule — cycle.py calls this per cycle)."""
    return C.NOISE_EVERY_BY_PHASE[puz_phase(cycle)]


# ---------------------------------------------------------------- helpers ------
def all_drift_events(cycle: int) -> list:
    """Named drift events at this cycle, for logging + insight detector."""
    evs = []
    for kind, who in fact_drift_events(cycle):
        evs.append({"lane": "fact", "kind": kind, "who": who})
    for kind, who in puz_rotation_events(cycle):
        evs.append({"lane": "puzzle", "kind": kind, "who": who})
    if cycle > 0 and cycle % C.SEQ_REGIME_LEN == 0:
        evs.append({"lane": "seq", "kind": "regime_shift",
                    "who": seq_regime(cycle)})
    return evs


def total_fact_rotations_before(cycle: int) -> int:
    return sum(cycle // fact_period(st) for st in range(C.FACT_STATIONS))


def expected_counts(cycles: int) -> dict:
    """Sanity expectations the final report can compare against."""
    return {
        "fact_rotations": total_fact_rotations_before(cycles),
        "puz_rotations": sum(cycles // puz_period(f) for f in range(C.PUZ_FAMILIES)),
        "episodes": puz_episode_counts(cycles),
        "seq_shifts": cycles // C.SEQ_REGIME_LEN,
        "shocks": cycles // C.FACT_SHOCK_EVERY,
    }
