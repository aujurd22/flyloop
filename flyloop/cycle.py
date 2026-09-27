"""The seven-step cycle, one lap per iteration (v2.1):

  1 EXPERIENCE  world emits events (fact query / puzzle probe / symbol arrival)
  2 MEMORY      recall the right compartment (or state_lookup for arm B)
  3 PREDICT     mechanical reasoner, or k-WTA net (streams A and B)
  4 ERROR       score against the world's ground truth
  5 UPDATE      corrections / table fold-in / book update / net steps
  6 NEW EXPERIENCE  the world has drifted (rotations, shocks, regime shifts)
  7 INSIGHT     rule abstractions + restructuring signatures -> ledger + memory

v2 fixes after two live-bug audits:
  - payload-first text (never truncated): c= early, tables <= 78 chars;
  - rules live in ONE global RULEBOOK entry (state_lookup, untruncated) with an
    ASCII head — per-family rule entries collided with their own tables in the
    merge zone (0.75<sim<=0.92), measured live: f0's rule was swallowed by the
    table write that followed it (audit of runs/smoke_v2 DB);
  - ALL text formats calibrated with the REAL emitters against MiniLM before
    launch (tests/calibrate_texts.py): table cross-family 0.69, book-vs-any 0.57;
  - dual seq streams A/B, fact A/B arms, read-back verification.
"""
import time

from . import config as C
from . import world
from . import reasoner
from .memclient import parse_ids, parse_recall

# ASCII heads keep embeddings apart (measured) and survive any single-byte cut.
HEADS = ["REDLOG", "BLUELOG", "GOLDLOG", "SILVERLOG"]
BOOK_KEY = "flyloop/rulebook"


def table_text(fam, ep, c, pairs_str):
    """Pairs FIRST: whatever a reader truncates can only be the tail metadata,
    never a half pair token (a cut '12:10' -> '12:1' would fabricate an
    observation). Total length is asserted <= 80 in tests."""
    return f"{HEADS[fam]} {C.PUZ_DESC[fam][:12]}【{pairs_str} | f{fam} {C.PUZ_WORDS[fam]} c={c} e{ep}】"


def book_text(rules, c):
    """One line, all family rules: rules = {fam: (epoch, a, b)}."""
    parts = " ".join(f"f{f}={a}x+{b}m13e{ep}" for f, (ep, a, b) in sorted(rules.items()))
    return f"RULEBOOK c={c} :: {parts}"


def fact_text(st, word, ch, c, desc):
    return f"{desc}，{word}站【FLFACT st={st} {word} ch={ch} c={c}】"


def fam_query(fam):
    return f"{C.PUZ_DESC[fam][:16]} {C.PUZ_WORDS[fam]} 观测表 求解"


def book_query():
    return "RULEBOOK 规律 求解 f0 f1 f2 f3"


class CycleRunner:
    def __init__(self, mem, poets, det, ledger, log=print):
        self.mem = mem
        self.poets = poets  # {"A": PoetLeg, "B": PoetLeg}
        self.det = det
        self.ledger = ledger
        self.log = log
        self.disc = {}
        self.book = {}   # fam -> (epoch, a, b)  (mirror of the RULEBOOK entry)
        self.counts = {"writes": 0, "recalls": 0, "noise": 0, "discoveries": 0,
                       "fact_writes": 0, "pair_writes": 0, "book_writes": 0,
                       "rejected": 0, "cold": 0, "readback_fail": 0,
                       "factA_n": 0, "factB_n": 0, "factA_hit": 0, "factB_hit": 0,
                       "puz_probes": 0}

    # ------------------------------------------------------------------
    async def _remember(self, text, tags, compartment="", state_key="", state_value=""):
        resp, mode = await self.mem.remember(text, tags=tags, compartment=compartment,
                                             state_key=state_key, state_value=state_value)
        self.counts["writes"] += 1
        if "REJECTED" in resp:
            self.counts["rejected"] += 1
        return resp, mode

    async def _readback(self, state_key, checks, want):
        """Read-back verification (L4 discipline): the just-written state must be
        visible via state_lookup with a parseable payload."""
        try:
            block, _ = await self.mem.state_lookup(state_key)
        except Exception:
            return False
        if not block or "CURRENT" not in block:
            return False
        for pat, expect in checks:
            m = pat.search(block)
            if not m or m.group(1) != expect:
                return False
        if want and want not in block:
            return False
        return True

    # ------------------------------------------------------------------
    async def run_cycle(self, c: int) -> dict:
        t0 = time.perf_counter()
        rec = {"c": c, "t": time.strftime("%H:%M:%S"), "notes": []}

        drifts = world.all_drift_events(c)
        if drifts:
            self.det.on_drift(c, drifts)
            rec["drifts"] = [f"{d['lane']}:{d['kind']}:{d['who']}" for d in drifts]
        rec["mode"] = self.mem.mode

        # ------------- sequence lane: dual streams A (hidden) / B (marker) ----
        ctxA = world.seq_context(c)
        true_sym = world.seq_symbol(c)
        predA, errA = self.poets["A"].predict(ctxA)
        rec["seqA_pred"], rec["seqA_err"] = predA, int(predA != true_sym)
        ctxB = world.seq_b_context(c)
        predB, errB = self.poets["B"].predict(ctxB)
        rec["seqB_pred"], rec["seqB_err"] = predB, int(predB != true_sym)
        if errA == "cuda_fallback":
            rec["notes"].append("cudaA")
        if errB == "cuda_fallback":
            rec["notes"].append("cudaB")
        lossA = lossB = None
        for _ in range(C.SEQ_STEPS_PER_CYCLE):
            tokA = (ctxA + [true_sym])[-(C.SEQ_CTX + 1):]
            lossA, perrA = self.poets["A"].train_step(tokA)
            tokB = (ctxB + [true_sym])[-(C.SEQ_CTX + 2):]
            lossB, perrB = self.poets["B"].train_step(tokB)
            if perrA:
                rec["notes"].append(f"poetA:{perrA}")
            if perrB:
                rec["notes"].append(f"poetB:{perrB}")
        rec["lossA"] = round(lossA, 3) if lossA is not None else None
        rec["lossB"] = round(lossB, 3) if lossB is not None else None

        # ------------- alternating lanes: odd cycles fact (arm alternates),
        # ------------- even cycles puzzle
        if c % 2 == 1:
            await self._fact_leg(c, rec, arm="A" if (c // 2) % 2 == 0 else "B")
        else:
            await self._puzzle_leg(c, rec)

        # ------------- distractor pressure ----------------
        if c % C.NOISE_EVERY == 0:
            await self._remember(world.distractor_text(c), tags="flyloop,noise",
                                 compartment=C.COMPARTMENT_NOISE)
            self.counts["noise"] += 1

        # ------------- periodic full state refresh ----------------
        if c % C.FACT_REFRESH_EVERY == 0:
            n = 0
            for st in range(C.FACT_STATIONS):
                ch = world.fact_channel(st, c)
                await self._remember(
                    fact_text(st, C.FACT_WORDS[st], ch, c, C.FACT_DESC[st]),
                    tags="flyloop,fact", compartment=C.COMPARTMENT_FACT,
                    state_key=reasoner.STATE_KEY_FACT.format(st=st), state_value=ch)
                n += 1
            rec["notes"].append(f"refresh:{n}")

        rec["writes"] = self.counts["writes"]
        rec["dt_ms"] = int((time.perf_counter() - t0) * 1000)
        return rec

    # ------------------------------------------------------------------
    async def _fact_leg(self, c, rec, arm):
        st = world.fact_station_at(c)
        word = C.FACT_WORDS[st]
        truth = world.fact_channel(st, c)
        key = reasoner.STATE_KEY_FACT.format(st=st)
        if arm == "A":
            query = f"{C.FACT_DESC[st]} {word}站 当前渠道是多少？"
            block, _ = await self.mem.recall(query, compartment=C.COMPARTMENT_FACT)
            self.counts["recalls"] += 1
            ch, evid = reasoner.predict_fact(parse_recall(block), st)
        else:
            block, _ = await self.mem.state_lookup(key)
            self.counts["recalls"] += 1
            ch, evid = reasoner.predict_fact_from_state(block, st)
        err = 1 if (ch is None or ch != truth) else 0
        rec[f"fact{arm}_err"] = err
        rec[f"fact{arm}_station"] = st
        rec[f"fact{arm}_hit"] = int(ch is not None)
        self.counts[f"fact{arm}_n"] += 1
        self.counts[f"fact{arm}_hit"] += int(ch is not None)
        if err:
            rec["notes"].append(f"fact{arm}:{ch or '?'}!={truth}")
        # correction on error + sampled routine write (one shared state)
        if err or c % 150 == 0:
            await self._remember(fact_text(st, word, truth, c, C.FACT_DESC[st]),
                                 tags="flyloop,fact", compartment=C.COMPARTMENT_FACT,
                                 state_key=key, state_value=truth)
            self.counts["fact_writes"] += 1
            if self.counts["fact_writes"] % 20 == 0:
                ok = await self._readback(key, [(reasoner.P_FACT, str(st))], truth)
                if not ok:
                    self.counts["readback_fail"] += 1
                    rec["notes"].append("fact_readback_fail")

    async def _puzzle_leg(self, c, rec):
        fam = (c // 2) % C.PUZ_FAMILIES
        word = C.PUZ_WORDS[fam]
        epoch = world.puz_epoch(fam, c)
        (x1, y1), xp, truth = world.puz_probe(fam, c)
        # tables via recall (compartment), the global book via state_lookup
        block_t, _ = await self.mem.recall(
            fam_query(fam), compartment=C.COMPARTMENT_PUZZLE, top_k=C.PUZ_RECALL_TOPK)
        block_b, _ = await self.mem.state_lookup(BOOK_KEY)
        self.counts["recalls"] += 2
        entries = parse_recall(block_t)
        y, method, eids, n_ver, ab = reasoner.predict_puzzle(entries, fam, epoch, xp)
        if method == "cold":
            book_rule = reasoner.parse_book(block_b, fam, epoch)
            if book_rule:
                a, b = book_rule
                y, method, n_ver = (a * xp + b) % C.PUZ_P, "book", 1
                ab = (a, b)
        err = 1 if (y is None or y != truth) else 0
        rec.update(puz_err=err, puz_method=method, puz_fam=fam,
                   puz_hit=int(method in ("rule", "fit", "book")))
        self.counts["puz_probes"] += 1
        if method == "cold":
            self.counts["cold"] += 1
        if err:
            rec["notes"].append(f"puz:{y}!={truth}({method})")

        d = self.disc.setdefault((fam, epoch), {
            "consec": 0, "done": False, "table": {}, "table_id": None, "unseen_since_write": 0})
        # table fold-in: keep the freshest pairs; write every Nth probe or on error
        d["table"][str(x1)] = y1
        d["unseen_since_write"] += 1
        if err or d["unseen_since_write"] >= C.TABLE_WRITE_EVERY:
            d["unseen_since_write"] = 0
            d["table"] = dict(list(d["table"].items())[-5:])
            pairs_s = " ".join(f"{x}:{v}" for x, v in d["table"].items())
            resp, _ = await self._remember(
                table_text(fam, epoch, c, pairs_s), tags="flyloop,puzzle",
                compartment=C.COMPARTMENT_PUZZLE,
                state_key=reasoner.STATE_KEY_TABLE.format(fam=fam),
                state_value=f"e{epoch}")
            self.counts["pair_writes"] += 1
            ids = parse_ids(resp)
            if ids:
                d["table_id"] = ids[-1]
        # discovery -> RULEBOOK update (single global entry, state_lookup read)
        if method == "fit" and n_ver >= 1:
            d["consec"] += 1
        elif method not in ("rule", "book"):
            d["consec"] = 0
        if d["consec"] >= C.PUZ_DISC_CONSEC and not d["done"] and ab:
            d["done"] = True
            a, b = ab
            self.book[fam] = (epoch, a, b)
            resp, _ = await self._remember(
                book_text(self.book, c), tags="flyloop,insight,rule",
                compartment=C.COMPARTMENT_RULE, state_key=BOOK_KEY,
                state_value=f"n{len(self.book)}")
            self.counts["book_writes"] += 1
            # read-back: this family's rule must be visible in the book
            rule_in_book = False
            try:
                rb, _ = await self.mem.state_lookup(BOOK_KEY)
                rule_in_book = reasoner.parse_book(rb, fam, epoch) == (a, b)
            except Exception:
                pass
            if not rule_in_book:
                self.counts["readback_fail"] += 1
                rec["notes"].append("book_readback_fail")
            self.det.on_discovery(c, fam, epoch, a, b, [d["table_id"]])
            self.counts["discoveries"] += 1
            rec["notes"].append(f"DISCOVERY fam={fam} ep={epoch} a={a} b={b}")
            self.log(f"[c{c}] INSIGHT rule_discovery fam={fam}({word}) ep={epoch} "
                     f"y=({a}x+{b}) mod {C.PUZ_P} (book has {len(self.book)} rules)")

    # ------------------------------------------------------------------
    def to_dict(self):
        return {"disc": {f"{k[0]}:{k[1]}": v for k, v in self.disc.items()},
                "counts": self.counts,
                "book": {str(k): list(v) for k, v in self.book.items()}}

    def load_dict(self, d):
        self.disc = {tuple(map(int, k.split(":"))): v for k, v in d.get("disc", {}).items()}
        self.counts = d.get("counts", self.counts)
        self.book = {int(k): tuple(v) for k, v in (d.get("book") or {}).items()}
