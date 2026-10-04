"""The seven-step cycle, one lap per iteration (v3).

v3 = Recurrent Drift x Memory Consolidation (V3_DESIGN.md):

  Two memory arms run the IDENTICAL world/probe schedule in the same process:
    FULL — observation tables + the RULEBOOK (a rule registry: every rule ever
           discovered, tagged with the epoch it was last active in)
    EPI  — observation tables only; the book is off-limits. Every book write
           the FULL arm makes is mirrored by a byte-exact padding write on the
           EPI arm (PadSync), so both arms buy the same write pressure.

  The recurrence shortcut under test: at an episode start the FULL arm may test
  recent book candidates against live observations — one confirming pair adopts
  an old rule ("book_test"), while the EPI arm must re-fit from two fresh pairs.
  Wrong adoptions are the stale-intrusion cost, measured as SIR.

Carried over from v2 (unchanged): payload-first text formats (truncation-proof),
the real-emitter calibration discipline, fact A/B arms, dual seq streams.
"""
import time
from collections import deque

from . import config as C
from . import world
from . import reasoner
from .memclient import parse_ids, parse_recall

# ASCII heads keep embeddings apart (measured) and survive any single-byte cut.
HEADS = ["REDLOG", "BLUELOG", "GOLDLOG", "SILVERLOG"]
# per-family book format: distinct CJK head + a family tag on EVERY rule line.
# Measured (tests/calibrate_texts.py, real MiniLM): cross-family book sim 0.655
# (< 0.75 merge line; the ASCII family words alone measured 0.90-0.93), book
# update 0.98 (in-place rewrite), book-vs-table 0.73. Max length ~94 chars <
# 120 (split_chunks threshold; >120 a state_key write is rejected by the v4
# atomicity guard -- the smoke_v3_1790532091 autopsy).
BOOK_HEADS = ["朱雀街的钟表铺，规律刻在黄铜齿轮上，一代代传下来",
              "渡口的老账房，规则记在流水簿子里，从不涂改",
              "山顶的观星台，定律写在发黄的星图之间",
              "巷尾的裁缝铺，样式留在泛黄的纸样册里"]
FAM_TAGS = ["红家", "蓝家", "金家", "银家"]
BOOK_TAG = "RULEBOOK"


class PadSync:
    """FULL book writes + MATCHED archive writes -> EPISODIC padding writes,
    1:1 by event count and byte-exact in total (three-way write parity)."""

    def __init__(self):
        self.queue = deque()
        self.charged = {"FULL": 0, "MATCHED": 0}
        self.drained = 0

    def charge(self, arm: str, nbytes: int):
        self.queue.append(nbytes)
        self.charged[arm] = self.charged.get(arm, 0) + nbytes

    def take(self):
        """Pop the next owed padding size (one book/archive write -> one pad
        write; byte parity is checked on totals, not per event)."""
        if self.queue:
            return self.queue.popleft()
        return None

    def parity(self) -> dict:
        pending = sum(self.queue)
        return {"charged_FULL": self.charged.get("FULL", 0),
                "charged_MATCHED": self.charged.get("MATCHED", 0),
                "drained": self.drained, "pending": pending,
                "pending_events": len(self.queue)}


def table_text(fam, ep, c, pairs_str):
    """Pairs FIRST: whatever a reader truncates can only be the tail metadata,
    never a half pair token (a cut '12:10' -> '12:1' would fabricate an
    observation). Total length is asserted <= 80 in tests."""
    return f"{HEADS[fam]} {C.PUZ_DESC[fam][:12]}【{pairs_str} | f{fam} {C.PUZ_WORDS[fam]} c={c} e{ep}】"


def book_text_v3(fam, rules, c):
    """One family's book entry: rules = {rid: {"a","b","ep"}} (capped at
    BOOK_CAP most recent). Distinct CJK head + a family tag on every rule
    line keeps cross-family and book-vs-table similarity below the merge
    line (calibrated, see BOOK_HEADS note). M7: derived rules carry a d1
    suffix (P_BOOK3 tolerates trailing chars)."""
    parts = []
    for rid in sorted(rules[fam], key=lambda r: -rules[fam][r]["ep"])[:C.BOOK_CAP]:
        r = rules[fam][rid]
        parts.append(f"{FAM_TAGS[fam]}r{rid.split('r')[1]}={r['a']}x{r['b']}e{r['ep']}")
    return f"{BOOK_HEADS[fam]} c={c} :: " + " ".join(parts)


def book_state_key(fam):
    return C.BOOK_STATE_KEY.format(fam=fam)


def derived_state_key(fam):
    return f"flyloop/book/{fam}/derived"


def parse_derived(block: str):
    """M7.2 derived candidate entry -> (rid, a, b, ep) or None."""
    import re as _re
    if not block:
        return None
    m = _re.search(r"[红蓝金银]家r(\d+)=(\d+)x(\d+)e(\d+)", block)
    if not m:
        return None
    rn, a, b, ep = (int(m.group(i)) for i in range(1, 5))
    # bare rule number: the caller prefixes the family (f"f{fam}r{rn}").
    # Returning "f?r{rn}" here led the caller to double-prefix and the
    # candidate to enter cands under a mangled rid (M7.3 root cause).
    return (rn, a, b, ep)


def book_rule_text(fam, rid, r, c):
    """RSI-0 G2 per-rule entry: one rule, ~45 chars — immune to the
    >120-char split_chunks/atomicity trap that killed G1's 13-rule entry."""
    return (f"{BOOK_TAG} {FAM_TAGS[fam]}规律 c={c} :: "
            f"{FAM_TAGS[fam]}r{rid.split('r')[1]}={r['a']}x{r['b']}e{r['ep']}")


def book_rule_key(fam, rid):
    return f"flyloop/book/{fam}/{rid}"


def res_text(fam, rid, a, b, ep, res, c):
    """W9C M5: one residual entry per rule (~70 chars with 4 residuals) --
    the compact rule's OWN LOSS, stored so prediction can add it back.
    Perrule discipline applies: force_new (same head >0.92 similar, the
    merge zone must not rewrite in place). Format mirrors reasoner's
    parse_res_entry: res=a,b,ep,x1,x2,..::(x1,r1)(x2,r2)..."""
    tag = FAM_TAGS[fam]
    xs = ",".join(str(x) for x, _ in res)
    pts = "".join(f"({x},{r})" for x, r in res)
    return (f"{BOOK_TAG} {FAM_TAGS[fam]}残差 c={c} :: "
            f"{tag}r{rid.split('r')[1]}res={a},{b},{ep},{xs}::{pts}")


def res_state_key(fam, rid):
    return f"flyloop/book/{fam}/{rid}/res"


def epireg_text(fam, ep, c, pairs_str):
    """MATCHED arm's episodic archive entry: the episode's raw pair table,
    one entry per episode (unique state_key -> no in-place overwrites).
    Distinct CJK head + a family tag on every pair token keeps cross-family
    similarity below the merge line (calibrated; see config.EPIREG_HEADS)."""
    tagged = " ".join(f"{FAM_TAGS[fam]}{t}" for t in pairs_str.split())
    return f"{C.EPIREG_HEADS[fam]} c={c} :: {tagged} e{ep}"


def epireg_state_key(fam, ep):
    return C.EPIREG_STATE_KEY.format(fam=fam, ep=ep)


def pad_text(nbytes: int, seq: int) -> str:
    head = f"{C.PAD_HEAD} p{seq:06d} "
    return (head + "z" * nbytes)[:max(nbytes, 1)]


def fact_text(st, word, ch, c, desc):
    return f"{desc}，{word}站【FLFACT st={st} {word} ch={ch} c={c}】"


def fam_query(fam):
    return f"{C.PUZ_DESC[fam][:16]} {C.PUZ_WORDS[fam]} 观测表 求解"


class CycleRunner:
    def __init__(self, mem, poets, det, ledger, log=print, arm="FULL",
                 pad_sync=None, pad_seq=0):
        self.mem = mem
        self.poets = poets  # {"A": PoetLeg, "B": PoetLeg}
        self.det = det
        self.ledger = ledger
        self.log = log
        self.arm = arm                 # "FULL" | "MATCHED" | "EPISODIC"
        self.pad_sync = pad_sync       # shared; F/M charge, E drains
        self.pad_seq = pad_seq
        self.disc = {}
        self.book = {}   # {fam: {rid: {"a","b","ep"}}}  (mirror of the RULEBOOK entry)
        # W9C M5: residual confirmation mirrors (RAM-only; the store holds
        # confirmed entries). res_seen[x][r] counts visits; res_conf[x]=r
        # after 2-of-2 agreement at the same x (flip resistance).
        self.res_seen = {}   # {fam: {rid: {x: {r: count}}}}
        self.res_conf = {}   # {fam: {rid: {x: r}}}
        self.res_last = {}   # {(fam, rid): last written keep-list}
        self.derived_rids = set()   # M7: rids ever derived (insight-note tag
                                    # only; derived_use uses derived_params,
                                    # see the M7.3 flag site)
        self.derived_params = {}    # M7.2: {fam: (rid, a, b, ep)} live candidate
        self.ep_hist = {}           # M7.5: {fam: deque([(a,b), ...])} last
                                    # identified episodes (multiset, maxlen 2)
        self.ep_hist_seen = set()   # {(fam, epoch)} already pushed
        self.epi_index = {}  # {fam: [epochs archived]} — keys of the M-arm archive
        self.book_index = {}  # {fam: set(rids written)} — G2 perrule keys
        self.flip_hist = deque(maxlen=20)  # V8 adaptive: rolling book_test outcomes
        self.adapt = {"eps_hat": 0.0}  # V8 adaptive read policy estimate
        self.counts = {"writes": 0, "recalls": 0, "noise": 0, "discoveries": 0,
                       "fact_writes": 0, "pair_writes": 0, "book_writes": 0,
                       "book_bytes": 0, "epireg_writes": 0, "epireg_bytes": 0,
                       "pad_writes": 0, "pad_bytes": 0,
                       "derived_writes": 0, "derived_write_fails": 0,
                       "rejected": 0, "cold": 0,
                       "fact_readback_fail": 0, "rulebook_readback_fail": 0,
                       "table_readback_fail": 0,
                       "factA_n": 0, "factB_n": 0, "factA_hit": 0, "factB_hit": 0,
                       "puz_probes": 0, "book_test_uses": 0, "epi_test_uses": 0,
                       "stale_intrusions": 0, "episodes": {"NEW": 0, "VARIANT": 0,
                                                           "RECALL": 0}}

    # ------------------------------------------------------------------
    async def _remember(self, text, tags, compartment="", state_key="",
                        state_value="", force_new=False):
        resp, mode = await self.mem.remember(text, tags=tags, compartment=compartment,
                                             state_key=state_key,
                                             state_value=state_value,
                                             force_new=force_new)
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
        rec = {"c": c, "t": time.strftime("%H:%M:%S"), "notes": [],
               "memory_arm": self.arm}

        drifts = world.all_drift_events(c)
        if drifts:
            self.det.on_drift(c, drifts)
            rec["drifts"] = [f"{d['lane']}:{d['kind']}:{d['who']}" for d in drifts]
        rec["mode"] = self.mem.mode

        # ------------- sequence lane (CONTINUAL-LEARNING CONTROL; demoted per
        # V3 §10 — kept identical in both arms, never load-bearing for verdicts)
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

        # ------------- EPISODIC arm: mirror the structured writes -----------
        if self.arm == "EPISODIC" and self.pad_sync is not None:
            await self._drain_padding(rec)

        # ------------- distractor pressure (quota-gated phases, v4) --------
        if c % world.noise_every(c) == 0:
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
                    self.counts["fact_readback_fail"] += 1
                    rec["notes"].append("fact_readback_fail")

    async def _drain_padding(self, rec):
        """EPISODIC arm only: mirror the FULL/MATCHED structured writes."""
        n = self.pad_sync.take() if self.pad_sync else None
        if n is None:
            return
        self.pad_seq += 1
        text = pad_text(n, self.pad_seq)
        await self._remember(text, tags="flyloop,pad",
                             compartment=C.COMPARTMENT_NOISE,
                             state_key=C.PAD_STATE_KEY, state_value=f"p{self.pad_seq}")
        self.counts["pad_writes"] += 1
        self.counts["pad_bytes"] += n
        self.pad_sync.drained += n
        rec["notes"].append(f"pad:{n}")

    async def _puzzle_leg(self, c, rec):
        fam = (c // 2) % C.PUZ_FAMILIES
        word = C.PUZ_WORDS[fam]
        epoch = world.puz_epoch(fam, c)
        wep = world.puz_episode(fam, c)
        (x1, y1), xp, truth = world.puz_probe(fam, c)

        d = self.disc.setdefault((fam, epoch), {
            "consec": 0, "done": False, "table": {}, "table_id": None,
            "unseen_since_write": 0, "probes": 0, "ep_counted": False,
            "adopted": None, "archived": False, "verified": False})
        probe_idx = d["probes"] + 1
        if not d["ep_counted"]:
            d["ep_counted"] = True
            self.counts["episodes"][wep["type"]] += 1

        # M7 (V10c): preemptive composition inference -- a fresh episode
        # whose rule is NOT in the book but whose family holds >=2 rules
        # gets a DERIVED candidate from the two most recent:
        # R_new = (a1+a2, b2-b1) with r1 most recent. Blind capability
        # (all families derive; poison cost measured); the derived entry
        # faces the same verification gate as any rule and is overwritten
        # by observation when wrong.
        if (self.arm == "FULL-COMP" and d["probes"] == 0
                and wep["rule_id"] not in self.book.get(fam, {})):
            a_d = b_d = None
            if C.DERIVE_EPISODES:
                # M7.5: world composes EPISODE slots ep[i-2], ep[i-1]
                # (RECALL episodes occupy slots); compose the last two
                # identified episodes instead of deduped book rules.
                hist = self.ep_hist.get(fam)
                if hist is not None and len(hist) == 2:
                    (a2, b2), (a1, b1) = hist[0], hist[1]
                    a_d = (a2 + a1) % C.PUZ_P
                    b_d = (b2 - b1) % C.PUZ_P
            else:
                fam_rules = self.book.get(fam, {})
                if len(fam_rules) >= 2:
                    r1, r2 = sorted(fam_rules.items(),
                                    key=lambda kv: -kv[1]["ep"])[:2]
                    a_d = (r1[1]["a"] + r2[1]["a"]) % C.PUZ_P
                    b_d = (r2[1]["b"] - r1[1]["b"]) % C.PUZ_P
            if a_d is not None:
                rid_d = wep["rule_id"]
                # M7.2: the derived candidate lives in its OWN store slot
                # (never in the budgeted book text -- M7.1's evict-first
                # sort meant it was never stored once families filled, and
                # its ep=epoch stamp poisoned non-composite families while
                # it did persist). One key per family, overwritten each
                # derivation; read as an EXTRA candidate by the read path.
                self.derived_rids.add(rid_d)
                self.derived_params[fam] = (rid_d, a_d, b_d, epoch)
                tag = FAM_TAGS[fam]
                text_d = (f"{BOOK_TAG} {tag}推演 c={c} :: "
                          f"{tag}r{rid_d.split('r')[1]}={a_d}x{b_d}e{epoch}")
                resp_d, ok_d = await self._remember(
                    text_d, tags="flyloop,derived,rule",
                    compartment=C.COMPARTMENT_RULE,
                    state_key=derived_state_key(fam),
                    state_value=f"e{epoch}", force_new=True)
                if ok_d:
                    self.counts["derived_writes"] =                         self.counts.get("derived_writes", 0) + 1
                else:
                    self.counts["derived_write_fails"] =                         self.counts.get("derived_write_fails", 0) + 1
                    self.derived_rids.discard(rid_d)
                    rec["notes"].append(f"derived_write_fail:{resp_d}")

        # V4 interface fix (applied to ALL arms identically): the current
        # probe's revealed pair is folded into the live observations BEFORE
        # prediction — in V3 it landed after, blinding probe 1 by artifact.
        d["table"][str(x1)] = y1
        # W9C M5: per-episode residual sample buffer (NOT the write-capped
        # table) -- within-episode x repeats confirm raw pairs 2-of-2 on the
        # spot; cross-visit repeats confirm on later visits.
        buf = d.setdefault("res_buf", [])
        buf.append((x1, y1))
        if len(buf) > 12:
            del buf[:-12]
        d["probes"] += 1
        d["unseen_since_write"] += 1
        # table dict keys are str (JSON round-trip through state.json); the
        # reasoner needs int pairs
        obs = [(int(k), v) for k, v in d["table"].items()]  # live observations

        # memory reads
        block_t, _ = await self.mem.recall(
            fam_query(fam), compartment=C.COMPARTMENT_PUZZLE, top_k=C.PUZ_RECALL_TOPK)
        self.counts["recalls"] += 1
        entries = parse_recall(block_t)
        cands = None
        epi_cands = None
        if self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT", "FULL-RES",
                             "FULL-COMP"):
            # RSI-0 G2 perrule mode: exact state_lookup over the runner's own
            # rule index (RAM mirror), same pattern as the MATCHED archive
            cands = []
            if C.BOOK_MODE == "perrule":
                # guard BEFORE sorting: drop index keys whose mirror entry was
                # evicted (desync otherwise KeyErrors the sort key itself)
                live = [r for r in self.book_index.get(fam, set())
                        if r in self.book.get(fam, {})]
                for stale_rid in self.book_index.get(fam, set()) - set(live):
                    self.book_index[fam].discard(stale_rid)
                for rid_old in sorted(
                        live,
                        key=lambda r: -self.book[fam][r]["ep"])[:C.BOOK_CAP]:
                    if self.book[fam][rid_old]["ep"] == epoch:
                        continue
                    try:
                        blk, _ = await self.mem.state_lookup(
                            book_rule_key(fam, rid_old))
                    except Exception:
                        continue
                    got = reasoner.parse_book_v3(blk or "", fam)
                    for rr in got:
                        if rr[0] == rid_old:
                            cands.append(rr)
                            break
                cands.sort(key=lambda r: -r[3])
            else:
                block_b, _ = await self.mem.state_lookup(book_state_key(fam))
                self.counts["recalls"] += 1
                registry = reasoner.parse_book_v3(block_b, fam)
                cands = reasoner.book_candidates(registry, C.BOOK_CAP)
                if self.arm == "FULL-COMP":
                    # M7.2: the family's derived candidate joins the
                    # candidate list. Read from the RAM mirror when this
                    # runner wrote it (saves an HTTP round-trip per probe);
                    # fall back to the store for rules written before a
                    # resume.
                    dp = self.derived_params.get(fam)
                    if dp is not None:
                        d_rule = (dp[0], dp[1], dp[2], dp[3])
                    else:
                        blk_d, _ = await self.mem.state_lookup(
                            derived_state_key(fam))
                        d_rule = parse_derived(blk_d or "")
                    self.counts["derived_lookups"] =                         self.counts.get("derived_lookups", 0) + 1
                    if d_rule:
                        self.counts["derived_lookup_hits"] =                             self.counts.get("derived_lookup_hits", 0) + 1
                        if dp is not None:
                            # mirror path: dp[0] is already the full rid --
                            # prefixing again produced f3r+f3r2="f3rf3r2",
                            # the M7.3 root cause (mangled rid in cands,
                            # flag's dp[0]==aux comparison always false)
                            rid_d, a_d, b_d, ep_d = d_rule
                        else:
                            # store path: d_rule[0] is the bare rule number
                            rn, a_d, b_d, ep_d = d_rule
                            rid_d = f"f{fam}r{rn}"
                        if all(r[0] != rid_d for r in cands):
                            cands.append((rid_d, a_d, b_d, ep_d))
                            self.counts["derived_cand_added"] =                                 self.counts.get("derived_cand_added", 0) + 1
        elif self.arm in ("MATCHED", "MATCHED-VER", "MATCHED-EXACT"):
            # exact state_lookup over the runner's own archive index (RAM
            # mirror of written keys) — similarity-based recall would rank
            # same-family archive entries arbitrarily (heads identical)
            epi = []
            for ep_old in self.epi_index.get(fam, [])[-C.EPIREG_CAP:]:
                if ep_old == epoch:
                    continue
                try:
                    blk, _ = await self.mem.state_lookup(
                        epireg_state_key(fam, ep_old))
                except Exception:
                    continue
                pairs, _ep = reasoner.parse_epireg(blk or "")
                if pairs:
                    epi.append((pairs, ep_old))
            epi.sort(key=lambda t: -t[1])
            epi_cands = epi
        # V8 adaptive read policy (FULL-ADAPT arm): the effective match bar
        # ADAPTS to the measured reveal-flip rate, estimated from the rolling
        # book_test success rate over the last 20 probes. At eps=0 the best
        # rule reproduces ~every live pair (bar stays at BASE); under flips
        # the success rate drops and the bar lowers proportionally, keeping
        # true rules recoverable while strict-argmax still refuses garbage.
        adj_min_frac = C.MATCH_MIN_FRAC
        if self.arm == "FULL-ADAPT" and len(self.flip_hist) >= 5:
            flip_rate = sum(self.flip_hist) / len(self.flip_hist)
            adj_min_frac = max(0.50, C.MATCH_MIN_FRAC * (1.0 - flip_rate))
        res_map = None
        if self.arm == "FULL-RES" and cands:
            res_map = {}
            for rid_c, *_ in cands[:C.BOOK_TEST_K]:
                try:
                    rb_res, _ = await self.mem.state_lookup(
                        res_state_key(fam, rid_c))
                    got = reasoner.parse_res_entry(rb_res or "")
                    if got:
                        res_map[rid_c] = got
                except Exception:
                    pass
        y, method, n_ver, ab, aux = reasoner.predict_puzzle_v4(
            entries, fam, epoch, xp, obs, cands=cands, epi_cands=epi_cands,
            min_frac=adj_min_frac,
            epi_tol=0 if self.arm == "MATCHED-EXACT" else None,
            res_map=res_map)

        stale_present = bool(cands) if self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT", "FULL-RES", "FULL-COMP") else \
            any(int(m.group(5)) != epoch for m in
                [reasoner.P_PAIRS.search(t) for _, t in entries]
                if m and int(m.group(2)) == fam)
        err = 1 if (y is None or y != truth) else 0
        stale_intrusion = int(err == 1 and method in
                              ("book_test", "epi_test", "fit_stale", "rule"))
        # M7.3 per-answer derived flag: 1 only when the answer actually came
        # from THIS episode's live derived candidate -- method is rule /
        # book_test, the aux rule_id equals the family's live derived rid AND
        # that candidate was derived for the current epoch (dp[3]). The old
        # ever-derived set (derived_rids) kept flagging every later probe of
        # a once-derived rid -- post-discovery book hits, RECALL re-runs of
        # the same rid -- polluting the composition-transfer metric.
        dp = self.derived_params.get(fam)
        derived_use = int(method in ("rule", "book_test")
                          and dp is not None
                          and dp[0] == aux.get("rule_id")
                          and dp[3] == epoch)
        rec.update(lane="puzzle",
                   episode_type=wep["type"], family=fam, epoch=epoch,
                   rule_id=wep["rule_id"], rule_age=(wep["gap"] if wep["type"] == "RECALL" else 0),
                   probe_idx=probe_idx,
                   prediction=y, truth=truth, error=err,
                   method=method, retrieval_rank=aux.get("book_rank", aux.get("epi_rank")),
                   anomaly=int(world.puz_anomaly(fam, c)),
                   derived_use=derived_use,
                   res_pred=aux.get("res_pred"),
                   stale_candidate_present=int(bool(stale_present)),
                   stale_intrusion=stale_intrusion,
                   discovery=False, reactivation=False, insight_kind=None,
                   useful_insight=None)
        # M7.3 early-return trace: on composite NEW probe-1 with a live
        # derived candidate, log exactly what answered -- aux rid vs the
        # live dp, candidate list with epochs. Confirms or refutes the
        # per-answer flag at the return site (was the puzzle flag
        # semantics, or the return path itself?).
        if (C.COMPOSITE and wep["type"] == "NEW" and probe_idx == 1
                and dp is not None):
            self.counts["m73_new_p1_dp"] =                 self.counts.get("m73_new_p1_dp", 0) + 1
            self.counts["m73_new_p1_used"] =                 self.counts.get("m73_new_p1_used", 0) + derived_use
            rec["notes"].append(
                "m73:aux=%s,m=%s,dp=%s,cands=%s,flag=%d" % (
                    aux.get("rule_id"), method,
                    ",".join(str(v) for v in dp),
                    "|".join("%s@e%s" % (r[0], r[3]) for r in cands[:8]),
                    derived_use))
        self.counts["puz_probes"] += 1
        if method == "book_test":
            self.counts["book_test_uses"] += 1
            # V8 adaptive: track the rolling book_test outcome for flip estimation
            self.flip_hist.append(1 - err if method == "book_test" else 0)
        if method == "epi_test":
            self.counts["epi_test_uses"] += 1
        if stale_intrusion:
            self.counts["stale_intrusions"] += 1
            rec["notes"].append(f"stale:{aux.get('rule_id') or method}")
        if method == "cold":
            self.counts["cold"] += 1
        if err:
            rec["notes"].append(f"puz:{y}!={truth}({method})")

        # M7.5: record the episode's rule once identified (present in book) --
        # the DERIVE_EPISODES variant composes the last two identified
        # EPISODES (multiset, RECALL repeats included), matching the world's
        # episode-slot composition ep[i-2], ep[i-1].
        if self.arm == "FULL-COMP":
            br = self.book.get(fam, {}).get(wep["rule_id"])
            if br is not None and (fam, epoch) not in self.ep_hist_seen:
                self.ep_hist_seen.add((fam, epoch))
                self.ep_hist.setdefault(
                    fam, deque(maxlen=2)).append((br["a"], br["b"]))

        # table fold-in write (all arms, identical cadence)
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
            if self.counts["pair_writes"] % 20 == 0:
                try:
                    rb, _ = await self.mem.state_lookup(
                        reasoner.STATE_KEY_TABLE.format(fam=fam))
                    ok = bool(rb) and f"e{epoch}" in rb and bool(reasoner.P_PAIRS.search(rb))
                except Exception:
                    ok = False
                if not ok:
                    self.counts["table_readback_fail"] += 1
                    rec["notes"].append("table_readback_fail")

        # MATCHED arm: archive the episode's raw pairs once, at its last
        # probe. force_new is LOAD-BEARING: same-family archive entries share
        # the head and measure >0.92 similar, so without it the merge zone
        # would rewrite older episodes' entries and the archive would
        # degenerate to one entry per family (the >120-char lesson's sibling).
        # Unique per-episode state_keys + force_new keep every episode's row.
        # MATCHED-VER (V7 factorial, verified-write cell): the archive write
        # is gated on consec-3 instead of episode end -- rows enter only
        # after 3 consecutive correct predictions from their own content.
        ver_gate = (self.arm == "MATCHED-VER" and d.get("verified", False))
        if (self.arm in ("MATCHED", "MATCHED-VER", "MATCHED-EXACT") and not d["archived"]
                and (ver_gate or
                     (self.arm == "MATCHED" and d["probes"] >= wep["n_probes"]))):
            pairs_s = " ".join(f"{x}:{v}" for x, v in
                               list(d["table"].items())[-5:])
            text = epireg_text(fam, epoch, c, pairs_s)
            resp, _ = await self._remember(
                text, tags="flyloop,epireg", compartment=C.COMPARTMENT_EPIREG,
                state_key=epireg_state_key(fam, epoch), state_value=f"e{epoch}",
                force_new=True)
            # flag AFTER the write succeeds: a failed write must not silently
            # skip the archive on the worker's cycle retry (V4 smoke lesson)
            d["archived"] = True
            self.counts["epireg_writes"] += 1
            nbytes = len(text.encode("utf-8"))
            self.counts["epireg_bytes"] += nbytes
            self.epi_index.setdefault(fam, []).append(epoch)
            if len(self.epi_index[fam]) > C.EPIREG_CAP:
                self.epi_index[fam] = self.epi_index[fam][-C.EPIREG_CAP:]
            if self.pad_sync is not None:
                self.pad_sync.charge("MATCHED", nbytes)

        # discovery / re-activation -> RULEBOOK update (FULL family arms).
        # V7 factorial: the WRITE gate is the manipulated factor --
        #   FULL      consec >= PUZ_DISC_CONSEC (verified)
        #   FULL-RAW  consec >= 1 (raw: first confirmed prediction writes)
        # V7B wavy world: a prediction within +-WAVE_TOL of truth counts as
        # correct for the gate -- the best possible prototype is band-correct
        # (exact is impossible), so the gate must not demand exactness.
        band_ok = (y is not None and C.WAVE_TOL > 0 and
                   min((y - truth) % C.PUZ_P,
                       (truth - y) % C.PUZ_P) <= C.WAVE_TOL)
        if method == "fit" and (err == 0 or band_ok) and \
                (n_ver >= 1 or C.WAVE_TOL > 0):
            d["consec"] += 1
        elif method in ("book_test", "rule", "epi_test") and \
                (err == 0 or band_ok):
            d["consec"] += 1
        else:
            d["consec"] = 0
        # verified milestone (V7): once consec reaches the gate, the episode's
        # content counts as verified FOREVER -- a later failure must not
        # un-verify an already-confirmed write
        if d["consec"] >= C.PUZ_DISC_CONSEC:
            d["verified"] = True
        disc_gate = 1 if self.arm == "FULL-RAW" else C.PUZ_DISC_CONSEC
        if (self.arm in ("FULL", "FULL-RAW", "FULL-ADAPT", "FULL-RES",
                             "FULL-COMP") and d["consec"] >= disc_gate
                and not d["done"] and ab):
            d["done"] = True
            a, b = ab
            rid = wep["rule_id"]
            fam_book = self.book.setdefault(fam, {})
            prev = fam_book.get(rid)
            is_reactivation = prev is not None and (prev["a"], prev["b"]) == (a, b)
            fam_book[rid] = {"a": a, "b": b, "ep": epoch}
            # cap: keep only the BOOK_CAP most recent rules of this family;
            # prune the G2 perrule index in LOCKSTEP (a stale index entry
            # crashes the read path with KeyError -- V7A-first-launch lesson)
            if len(fam_book) > C.BOOK_CAP:
                for old_rid in sorted(fam_book, key=lambda r: fam_book[r]["ep"])[
                        :len(fam_book) - C.BOOK_CAP]:
                    del fam_book[old_rid]
                    self.book_index.get(fam, set()).discard(old_rid)
            if C.BOOK_MODE == "perrule":
                # RSI-0 G2: one SHORT entry per rule (~45 chars) — immune to
                # the >120-char split_chunks/atomicity trap that rejected
                # G1's 13-rule single entry. force_new is LOAD-BEARING here:
                # same-family perrule entries share the head and measure
                # >0.92 similar, so without it the merge zone rewrites the
                # previous rule's entry in place and the book degenerates to
                # one entry per family (the V1 table-swallows-rule failure
                # mode, perrule edition — found live in rsi0_g2 first launch)
                text = book_rule_text(fam, rid, fam_book[rid], c)
                skey = book_rule_key(fam, rid)
                force_new = True
            else:
                text = book_text_v3(fam, self.book, c)
                skey = book_state_key(fam)
                force_new = False
            resp, _ = await self._remember(
                text, tags="flyloop,insight,rule",
                compartment=C.COMPARTMENT_RULE, state_key=skey,
                state_value=f"n{len(fam_book)}", force_new=force_new)
            self.book_index.setdefault(fam, set()).add(rid)
            self.counts["book_writes"] += 1
            nbytes = len(text.encode("utf-8"))
            self.counts["book_bytes"] += nbytes
            if self.pad_sync is not None:
                self.pad_sync.charge("FULL", nbytes)
            # read-back: this family's rules must be visible in its book entry
            try:
                if C.BOOK_MODE == "perrule":
                    rb, _ = await self.mem.state_lookup(book_rule_key(fam, rid))
                    got = reasoner.parse_book_v3(rb, fam)
                    ok = any(r[0] == rid and (r[1], r[2]) == (a, b) for r in got)
                else:
                    rb, _ = await self.mem.state_lookup(book_state_key(fam))
                    got = reasoner.parse_book_v3(rb, fam)
                    ok = any(r[0] == rid and (r[1], r[2]) == (a, b) for r in got)
            except Exception:
                ok = False
            if not ok:
                self.counts["rulebook_readback_fail"] += 1
                rec["notes"].append("book_readback_fail")
            self.det.on_discovery(c, fam, epoch, a, b, [d["table_id"]])
            self.counts["discoveries"] += 1
            kind = "REACTIVATION" if is_reactivation else "DISCOVERY"
            # V3 post-review: DISCOVERY (first abstraction of a rule_id) and
            # REACTIVATION (book write for a known rule) are different events;
            # only DISCOVERY can prefix a "future recurrence benefit" claim.
            rec["discovery"] = not is_reactivation
            rec["reactivation"] = is_reactivation
            rec["insight_kind"] = kind
            rec["notes"].append(
                f"{kind} fam={fam} ep={epoch} rid={rid} a={a} b={b}"
                + (" derived" if rid in self.derived_rids else ""))
            self.log(f"[c{c}] INSIGHT {kind} fam={fam}({word}) ep={epoch} rid={rid} "
                     f"y=({a}x+{b}) mod {C.PUZ_P} (book has "
                     f"{sum(len(v) for v in self.book.values())} rules)")

        # FULL-RES (W9C / M5 residual registry): store the compact rule's OWN
        # LOSS. At episode end, residuals r = y1-(a*x1+b) from revealed pairs
        # are confirmed 2-of-2 across visits of the same x (a flip lands the
        # same wrong r twice with prob ~ eps^2 -- structural noise拒绝), then
        # written to the rule's residual entry. Prediction replays the
        # nearest-x residual (reasoner.wave_est) -- the wave enters the
        # prediction instead of being compressed away (the W9B floor).
        if self.arm == "FULL-RES":
            # W9C debug counters (remove after adjudication)
            self.counts["res_chk"] = self.counts.get("res_chk", 0) + 1
            if d["probes"] >= wep["n_probes"]:
                self.counts["res_chk_end"] = \
                    self.counts.get("res_chk_end", 0) + 1
                if not (self.book.get(fam, {}).get(wep["rule_id"])):
                    self.counts["res_chk_norule"] = \
                        self.counts.get("res_chk_norule", 0) + 1
        if (self.arm == "FULL-RES" and not d.get("res_archived")
                and d["probes"] >= wep["n_probes"]):
            d["res_archived"] = True
            rid_r = wep["rule_id"]
            rmeta = self.book.get(fam, {}).get(rid_r)
            if rmeta:
                try:
                    a_r, b_r = rmeta["a"], rmeta["b"]
                    seen = self.res_seen.setdefault(fam, {}).setdefault(rid_r, {})
                    conf = self.res_conf.setdefault(fam, {}).setdefault(rid_r, {})
                    fresh_n = 0
                    for x1, y1 in d.get("res_buf", [])[-12:]:
                        xi, yi = int(x1), int(y1)
                        # confirm RAW pairs (x, y): the wave is rule-stable,
                        # so the true pair replays exactly across visits and
                        # hits 2-of-2; a flipped y is random and never does.
                        # No fit-based filtering: the fit carries its own
                        # wave pollution (the W9B lesson) -- and the anchor
                        # prediction cancels any constant fit offset anyway.
                        fresh_n += 1
                        cnts = seen.setdefault(xi, {})
                        cnts[yi] = cnts.get(yi, 0) + 1
                        if cnts[yi] >= 2:
                            conf[xi] = yi
                    self.counts["res_fresh"] = self.counts.get("res_fresh", 0) + fresh_n
                    self.counts["res_conf_n"] = sum(len({}) for _ in [0]) or len(conf)
                    keep = sorted(conf.items())[-C.RES_CAP:]
                    if keep and keep != self.res_last.get((fam, rid_r)):
                        self.res_last[(fam, rid_r)] = keep
                        text_r = res_text(fam, rid_r, a_r, b_r, epoch, keep, c)
                        await self._remember(
                            text_r, tags="flyloop,residual",
                            compartment=C.COMPARTMENT_RULE,
                            state_key=res_state_key(fam, rid_r),
                            state_value=f"n{len(keep)}", force_new=True)
                        self.counts["res_writes"] = \
                            self.counts.get("res_writes", 0) + 1
                        if self.pad_sync is not None:
                            self.pad_sync.charge("FULL",
                                                 len(text_r.encode("utf-8")))
                except Exception as e:
                    self.counts["res_err"] = \
                        self.counts.get("res_err", 0) + 1
                    rec["notes"].append(f"res_err:{type(e).__name__}")

    # ------------------------------------------------------------------
    def to_dict(self):
        return {"disc": {f"{k[0]}:{k[1]}": v for k, v in self.disc.items()},
                "counts": self.counts,
                "book": {str(k): v for k, v in self.book.items()},
                "epi_index": {str(k): v for k, v in self.epi_index.items()},
                "book_index": {str(k): sorted(v) for k, v in self.book_index.items()},
                "arm": self.arm, "pad_seq": self.pad_seq}

    def load_dict(self, d):
        self.disc = {tuple(map(int, k.split(":"))): v for k, v in d.get("disc", {}).items()}
        self.counts = d.get("counts", self.counts)
        self.book = {int(k): v for k, v in (d.get("book") or {}).items()}
        self.epi_index = {int(k): v for k, v in (d.get("epi_index") or {}).items()}
        self.book_index = {int(k): set(v) for k, v in (d.get("book_index") or {}).items()}
        self.pad_seq = d.get("pad_seq", 0)
