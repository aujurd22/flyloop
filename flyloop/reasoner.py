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
# RULEBOOK c=53000 :: f0=10x+8m13e65 f1=3x+7m13e52   (single global book entry)
P_BOOK = re.compile(r"f(\d)=(\d+)x\+(\d+)m13e(\d+)")
P_PAIR = re.compile(r"(\d{1,2}):(\d{1,2})")

STATE_KEY_FACT = "flyloop/st-{st}"
STATE_KEY_TABLE = "flyloop/pairs/{fam}"
BOOK_KEY = "flyloop/rulebook"


def parse_book(block: str, fam: int, epoch: int):
    """Extract this family's (a, b) from a RULEBOOK state_lookup response.
    Returns None if the family is absent or the epoch is stale."""
    if not block:
        return None
    for m in P_BOOK.finditer(block):
        if int(m.group(1)) == fam and int(m.group(4)) == epoch:
            return int(m.group(2)), int(m.group(3))
    return None


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
    """Rule recall first, else fit a,b from the family's table, else guess.

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
