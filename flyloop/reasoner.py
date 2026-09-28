r"""Mechanical reasoners: memory contents -> prediction. (v2)

No LLM in the loop. Parsers are strict and end-anchored where possible:
v1's failure was a regex that required a trailing `c=(\d+)` which the
80-char recall truncation could cut off — v2 puts `c=` near the front of
every payload AND accepts the pattern anchored at the closing bracket.
"""
import re

from . import config as C

# NOTE: pattern strings below use raw literals; the docstring above documents
# why payload ordering matters (truncation tests live in tests/test_parsers.py).
# FLFACT st=0 alpha ch=B c=53000 ...   (c= early, persona tail optional)
P_FACT = re.compile(r"FLFACT st=(\d+) (\S+) ch=([A-E]) c=(\d+)")
# v2.1 table layout (pairs FIRST so a cut can never truncate a pair token into
# a wrong point):  HEAD persona【6:10 12:7 … | f0 red c=53000 e65】
P_PAIRS = re.compile(r"【([0-9: ]+?) \| f(\d) (\S+) c=(\d+) e(\d+)")
# FLRULE f0 red c=53000 e65 a=10 b=8 ...   (legacy per-family rule entries)
P_RULE = re.compile(r"FLRULE f(\d) (\S+) c=(\d+) e(\d+) a=(\d+) b=(\d+)")
# Per-family book entry: "朱雀街的钟表铺… c=531 :: 红家r5=3x7e17 红家r3=10x8e14"
# (one entry PER FAMILY; the family tag lives on every line -- see cycle.py).
P_BOOK3 = re.compile(r"([红蓝金银])家r(\d+)=(\d+)x(\d+)e(\d+)")
FAM_OF_TAG = {"红": 0, "蓝": 1, "金": 2, "银": 3}
P_BOOK = re.compile(r"f(\d)=(\d+)x\+(\d+)m13e(\d+)")
# MATCHED arm's episodic archive entry: "钟表铺的原始记录… c=531 :: 红家3:7 红家11:2 e8"
# (state_lookup appends " (since ...)" after the payload, so the epoch match
# is the LAST e(\d+) in the payload, not an end-anchored one)
P_EPIREG_EP = re.compile(r"e(\d+)")
P_EPIREG_PAIR = re.compile(r"([红蓝金银])?(\d{1,2}):(\d{1,2})")
P_PAIR = re.compile(r"(\d{1,2}):(\d{1,2})")

STATE_KEY_FACT = "flyloop/st-{st}"
STATE_KEY_TABLE = "flyloop/pairs/{fam}"
BOOK_KEY = "flyloop/rulebook"


def parse_book(block: str, fam: int, epoch: int):
    """(v2 format) Extract this family's (a, b) from a RULEBOOK state_lookup
    response. Returns None if the family is absent or the epoch is stale."""
    if not block:
        return None
    for m in P_BOOK.finditer(block):
        if int(m.group(1)) == fam and int(m.group(4)) == epoch:
            return int(m.group(2)), int(m.group(3))
    return None


def parse_book_v3(block: str, fam: int):
    """One family's book entry -> [(rid, a, b, epoch), ...] (write order).
    rid is reconstructed as f{fam}r{n} from the entry's family."""
    out = []
    if not block:
        return out
    for m in P_BOOK3.finditer(block):
        if FAM_OF_TAG[m.group(1)] != fam:
            continue
        rn, a, b, ep = (int(m.group(i)) for i in range(2, 6))
        out.append((f"f{fam}r{rn}", a, b, ep))
    return out


def book_candidates(rules, cap):
    """The family's rules sorted by recency (last-active epoch), newest first,
    capped. Includes the current-epoch rule if present -- predict_puzzle_v4
    splits it into the direct 'rule' path and tests the rest as recurrence
    candidates."""
    return sorted(rules, key=lambda r: -r[3])[:cap]


def parse_epireg(block: str):
    """MATCHED archive state_lookup response -> (pairs, epoch) or None.
    The payload is the tagged pair list after '::', ending in e{epoch};
    take the LAST e(\\d+) (the response tail adds '(since ...)' text)."""
    if not block or "::" not in block:
        return None, None
    payload = block.split("::", 1)[1]
    eps = P_EPIREG_EP.findall(payload)
    if not eps:
        return None, None
    ep = int(eps[-1])
    pairs = []
    for _tag, x, y in P_EPIREG_PAIR.findall(payload[:payload.rfind("e" + eps[-1])]):
        x, y = int(x), int(y)
        if 0 <= x < C.PUZ_P and 0 <= y < C.PUZ_P:
            pairs.append((x, y))
    return pairs, ep


def book_test(cands, pairs, p: int):
    """Test book candidates against observed pairs; adopt only a UNIQUE match.

    Returns (rule, rank, n_matches). A rule matches when it reproduces every
    observed pair. With one observed pair a wrong candidate matches with
    probability 1/p, so at candidate counts > p the unique-match requirement
    is what keeps single-pair adoption honest; ambiguity falls through to
    fitting instead of guessing among matches."""
    if not pairs:
        return None, 0, 0
    matches = []
    for rank, (rid, a, b, ep) in enumerate(cands, start=1):
        if all((a * x + b) % p == y for x, y in pairs):
            matches.append(((rid, a, b, ep), rank))
    if len(matches) == 1:
        return matches[0][0], matches[0][1], 1
    return None, 0, len(matches)


def frac_best(cands, pairs, p: int, min_frac: float):
    """Tolerant matcher (V6): score each candidate by the FRACTION of live
    pairs it reproduces exactly; adopt ONLY a strict argmax that clears
    min_frac — a tie at the top is a REFUSAL, not a recency tiebreak
    (ambiguous identification is refused, consistent with the exact
    matcher's unique-match discipline; reviewer option A, 2026-09-28).
    Under flip noise the true rule reproduces ~0.75 of live pairs while
    wrong rules sit near 1/p, so the fraction separates them where the
    all-pairs criterion could not. Returns (candidate, rank, frac) or
    (None, 0, best_frac)."""
    if not pairs:
        return None, 0, 0.0
    scored = []
    for rank, cand in enumerate(cands, start=1):
        a, b = cand[1], cand[2]
        hit = sum(1 for x, y in pairs if (a * x + b) % p == y)
        scored.append((hit / len(pairs), -rank, cand, rank))
    scored.sort(reverse=True)
    best_frac, _, best, best_rank = scored[0]
    if best_frac < min_frac or len(scored) > 1 and scored[1][0] >= best_frac:
        return None, 0, best_frac
    return best, best_rank, best_frac


def epi_test(cands, obs, min_frac: float = 1.0):
    """MATCHED arm's matcher: the SAME decision rule as the book matcher, but
    candidates are RAW episodic pair tables instead of compressed rules. A
    candidate's score = fraction of live pairs it reproduces exactly (an x
    absent from the candidate's table cannot be verified -> misses the
    fraction). ONLY a strict argmax at min_frac adopts — a tie at the top is
    a refusal, not a recency tiebreak (same discipline as frac_best). Raw
    pairs do not generalize — that IS the representation difference under
    test. Returns (candidate, rank, frac) where candidate = (pairs, ep)."""
    if not obs:
        return None, 0, 0.0
    scored = []
    for rank, (pairs, ep) in enumerate(cands, start=1):
        table = dict(pairs)
        hit = sum(1 for x, y in obs if x in table and table[x] == y)
        scored.append((hit / len(obs), -rank, (pairs, ep), rank))
    scored.sort(reverse=True)
    best_frac, _, best, best_rank = scored[0]
    if best_frac < min_frac or len(scored) > 1 and scored[1][0] >= best_frac:
        return None, 0, best_frac
    return best, best_rank, best_frac


def fit_from(pairs, p: int):
    """Least-squares-free exact linear fit from >= 2 distinct x values.
    Returns (a, b) or None."""
    uniq = {}
    for x, y in pairs:
        uniq[x] = y
    pts = list(uniq.items())
    if len(pts) < 2:
        return None
    (x1, y1), (x2, y2) = pts[0], next(pr for pr in pts[1:] if pr[0] != pts[0][0])
    a = ((y1 - y2) * _inv_mod(x1 - x2, p)) % p
    b = (y1 - a * x1) % p
    return a, b


def parse_pairs(blob: str):
    """x:y tokens from a table payload tail; drops malformed tails silently."""
    out = []
    for x, y in P_PAIR.findall(blob):
        x, y = int(x), int(y)
        if 0 <= x < C.PUZ_P and 0 <= y < C.PUZ_P:
            out.append((x, y))
    return out


def predict_fact(entries, station: int):
    """Latest FLFACT for the station wins. `entries` are (id, text) pairs."""
    best = (None, None, -1)  # ch, id, cyc
    for mid, text in entries:
        m = P_FACT.search(text)
        if m and int(m.group(1)) == station and int(m.group(4)) > best[2]:
            best = (m.group(3), mid, int(m.group(4)))
    ch, mid, _ = best
    return ch, mid


def predict_fact_from_state(block: str, station: int):
    """Parse a state_lookup response: '[flyloop/st-N] CURRENT: <text> (since ...)'."""
    if not block or "CURRENT" not in block:
        return None, None
    m = P_FACT.search(block)
    if not m or int(m.group(1)) != station:
        return None, None
    return m.group(3), None


def _inv_mod(x: int, p: int) -> int:
    return pow(x % p, p - 2, p)


def predict_puzzle(entries, fam: int, epoch: int, xp: int):
    """(v2) Rule recall first, else fit a,b from the family's table, else guess.

    Returns (y, method, evidence_ids, n_verified, (a, b) or None).
    method in rule/fit/guess/cold.
    """
    p = C.PUZ_P
    rules, tables = [], []
    for mid, text in entries:
        m = P_RULE.search(text)
        if m and int(m.group(1)) == fam and int(m.group(4)) == epoch:
            rules.append((int(m.group(5)), int(m.group(6)), int(m.group(3)), mid))
        m = P_PAIRS.search(text)
        if m and int(m.group(2)) == fam:
            tables.append((parse_pairs(m.group(1)), int(m.group(5)),
                           int(m.group(4)), mid))
    if rules:
        a, b, _, mid = max(rules, key=lambda r: r[2])
        return (a * xp + b) % p, "rule", [mid], 1, (a, b)
    # epoch-exact tables first; if none (e.g. truncated at a rotation), fall
    # back to the freshest table for the family (its pairs are still valid
    # within the SAME epoch only, so this is flagged as stale-fit)
    exact = [t for t in tables if t[1] == epoch]
    pool = exact or tables
    if pool:
        pairs, tbl_ep, cyc, mid = max(pool, key=lambda t: t[2])
        uniq = {}
        for x, y in pairs:
            uniq[x] = y  # later duplicates win (order = write order)
        uniq = list(uniq.items())
        if len(uniq) >= 2:
            (x1, y1), (x2, y2) = uniq[0], next(pr for pr in uniq[1:] if pr[0] != uniq[0][0])
            a = ((y1 - y2) * _inv_mod(x1 - x2, p)) % p
            b = (y1 - a * x1) % p
            n_ver = sum(1 for x, y in uniq[2:] if (a * x + b) % p == y)
            method = "fit" if tbl_ep == epoch else "fit_stale"
            return (a * xp + b) % p, method, [mid], n_ver, (a, b)
        return uniq[0][1], "guess", [mid], 0, None
    return None, "cold", [], 0, None


def predict_puzzle_v4(entries, fam: int, epoch: int, xp: int, obs,
                      cands=None, epi_cands=None):
    """V4 hierarchy over PRE-FOLDED live observations (the current probe's
    revealed pair is already in `obs` — applies to ALL arms symmetrically).

    1. (F) book rule already active at this epoch -> "rule"
    2. (F) book candidates vs obs — V6 composite: exact unique match first
           (the probe-1 shortcut survives unflipped pairs), then fraction-best
           at MATCH_MIN_FRAC when the exact path is ambiguous (the noise
           antidote; meaningful from >= 2 live pairs)
       (M) episodic candidates: same composite over raw pair tables ->
           "epi_test", then fit from the matched table's pairs + obs
    3. live fit from >= 2 distinct obs (all arms)
    4. (E/M) stale fit from the freshest recalled table
    5. guess / cold

    Returns (y, method, n_ver, (a, b), aux).
    """
    p = C.PUZ_P
    obs = list(obs or [])
    if cands:
        for rid, a, b, ep in cands:
            if ep == epoch:
                return ((a * xp + b) % p, "rule", 1, (a, b),
                        {"rule_id": rid, "book_rank": 1, "n_book_matches": 1})
        test_cands = [r for r in cands if r[3] != epoch][:C.BOOK_TEST_K]
        if obs:
            rule, rank, n_m = book_test(test_cands, obs, p)
            if rule is None and C.MATCH_MIN_FRAC < 1.0 and len(obs) >= 2:
                # V6 tolerant fallback: the true rule reproduces ~0.75 of
                # flip-noisy live pairs while wrong rules sit near 1/p
                rule, rank, frac = frac_best(test_cands, obs, p, C.MATCH_MIN_FRAC)
                if rule is not None:
                    rid, a, b, _ = rule
                    return ((a * xp + b) % p, "book_test", 1, (a, b),
                            {"rule_id": rid, "book_rank": rank,
                             "match_frac": round(frac, 3)})
            if rule is not None:
                rid, a, b, _ = rule
                return ((a * xp + b) % p, "book_test", 1, (a, b),
                        {"rule_id": rid, "book_rank": rank,
                         "n_book_matches": n_m})
    if epi_cands and obs:
        epi_pool = [(pairs, ep) for pairs, ep in epi_cands if ep != epoch][
            :C.EPIREG_CAP]
        cand, rank, n_m = epi_test(epi_pool, obs)
        if cand is None and C.MATCH_MIN_FRAC < 1.0 and len(obs) >= 2:
            cand, rank, frac = epi_test(epi_pool, obs, min_frac=C.MATCH_MIN_FRAC)
            if cand is not None:
                cpairs, cep = cand
                ab = fit_from(list(cpairs) + obs, p)
                if ab is not None:
                    a, b = ab
                    return ((a * xp + b) % p, "epi_test", 1, (a, b),
                            {"epi_rank": rank, "match_frac": round(frac, 3)})
        if cand is not None:
            cpairs, cep = cand
            ab = fit_from(list(cpairs) + obs, p)
            if ab is not None:
                a, b = ab
                return ((a * xp + b) % p, "epi_test", 1, (a, b),
                        {"epi_rank": rank, "n_epi_matches": n_m})
    if len(obs) >= 2:
        ab = fit_from(obs, p)
        if ab is not None:
            a, b = ab
            n_ver = sum(1 for x, y in obs[2:] if (a * x + b) % p == y)
            return ((a * xp + b) % p, "fit", n_ver, (a, b), {})
    # stale fallback from memory (previous epoch's table may still be active)
    tables = []
    for mid, text in entries:
        m = P_PAIRS.search(text)
        if m and int(m.group(2)) == fam:
            tables.append((parse_pairs(m.group(1)), int(m.group(5)),
                           int(m.group(4)), mid))
    if obs:
        return obs[0][1], "guess", 0, None, {}
    if tables:
        pairs, tbl_ep, cyc, mid = max(tables, key=lambda t: t[2])
        ab = fit_from(pairs, p)
        if ab is not None:
            a, b = ab
            n_ver = sum(1 for x, y in pairs if (a * x + b) % p == y)
            method = "fit" if tbl_ep == epoch else "fit_stale"
            return ((a * xp + b) % p, method, n_ver, (a, b), {})
        return pairs[0][1], "guess", 0, None, {}
    return None, "cold", 0, None, {}
