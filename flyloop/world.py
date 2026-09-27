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
def puz_period(fam: int) -> int:
    return C.PUZ_PERIOD0 + C.PUZ_PERIOD_STEP * fam


def puz_epoch(fam: int, cycle: int) -> int:
    return cycle // puz_period(fam)


def puz_rule(fam: int, cycle: int):
    r = _rng("puz", "rule", fam, puz_epoch(fam, cycle))
    a = int(r.integers(1, C.PUZ_P))
    b = int(r.integers(0, C.PUZ_P))
    return a, b


def puz_rotation_cycle(fam: int, epoch: int) -> int:
    return epoch * puz_period(fam)


def puz_probe(fam: int, cycle: int):
    """One revealed example pair + a probe x whose y is hidden until scored."""
    r = _rng("puz", "probe", fam, cycle)
    a, b = puz_rule(fam, cycle)
    x1 = int(r.integers(0, C.PUZ_P))
    xp = int(r.integers(0, C.PUZ_P))
    y1 = (a * x1 + b) % C.PUZ_P
    truth = (a * xp + b) % C.PUZ_P
    return (x1, y1), xp, truth


def puz_rotation_events(cycle: int) -> list:
    evs = []
    for f in range(C.PUZ_FAMILIES):
        if cycle > 0 and cycle % puz_period(f) == 0:
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
        "seq_shifts": cycles // C.SEQ_REGIME_LEN,
        "shocks": cycles // C.FACT_SHOCK_EVERY,
    }
