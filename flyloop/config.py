"""flyloop — closed-loop sandbox wiring FlyMemory + FlyPoet + intuition-mechanism.

Experience -> Memory -> Prediction -> Error -> Update -> New Experience -> New Insight

All paths/ports/thresholds live here so a run is reproducible.
v2 (2026-09-27): truncation fix, rule de-anchoring, seq dual-stream A/B,
fact state_lookup arm, speed knobs, quota-stop rules.
"""
import os
import sys

# --- interpreters & locations -------------------------------------------------
# Override with env vars when running on a different machine:
#   FLYLOOP_PYTHON     path to the interpreter with mcp/torch/sentence-transformers
#   FLYLOOP_ROOT       repository root (defaults to the package's parent directory)
#   FLYLOOP_FLYPOET    FlyPoet checkout containing train_v2.py
_HERE = os.path.dirname(os.path.abspath(__file__))


def _python_exe():
    exe = os.environ.get("FLYLOOP_PYTHON") or sys.executable
    # a pythonw launch has no console; derive the console interpreter for
    # children that need stdio (git-bash/pythonw launches are common here)
    if exe.lower().endswith("pythonw.exe"):
        cand = exe[:-len("pythonw.exe")] + "python.exe"
        if os.path.exists(cand):
            return cand
    return exe


def _pythonw_exe():
    exe = os.environ.get("FLYLOOP_PYTHONW") or _python_exe()
    if exe.lower().endswith("python.exe"):
        cand = exe[:-len("python.exe")] + "pythonw.exe"
        if os.path.exists(cand):
            return cand
    return exe


PYTHON = _python_exe()
PYTHONW = _pythonw_exe()
ROOT = os.environ.get("FLYLOOP_ROOT", os.path.dirname(_HERE))
FLYPOET_REPO = os.environ.get(
    "FLYLOOP_FLYPOET", os.path.join(os.path.dirname(ROOT), "flypoet"))

# sandbox FlyMemory instances (v4: one per arm — FULL 8769 / MATCHED 8770 /
# EPISODIC 8771; separate processes AND pickles, because the merge zone
# ignores compartments, so same-persona texts from different arms would
# collide in one store. 8765=ZCode prod, 8766=WorkBuddy, 8767=v2 legacy).
MEM_HOST = "127.0.0.1"
MEM_PORT = int(os.environ.get("FLYLOOP_PORT", "8769"))
MEM_URL = f"http://{MEM_HOST}:{MEM_PORT}/mcp"
MEM_PORT_MATCHED = int(os.environ.get("FLYLOOP_PORT_MATCHED", "8770"))
MEM_URL_MATCHED = f"http://{MEM_HOST}:{MEM_PORT_MATCHED}/mcp"
MEM_PORT_EPI = int(os.environ.get("FLYLOOP_PORT_EPI", "8771"))
MEM_URL_EPI = f"http://{MEM_HOST}:{MEM_PORT_EPI}/mcp"
SANDBOX_MEM_DIR = os.path.join(ROOT, "sandbox_mem", "flymemory")

# --- run budget (quota-stop rules; time is a ceiling, not a goal) --------------
DURATION_H = float(os.environ.get("FLYLOOP_HOURS", "10.0"))
MAX_CYCLES = 200000          # hard safety cap
CHECKPOINT_EVERY_CYCLES = 50
CHECKPOINT_EVERY_S = 120.0
REPORT_EVERY_S = 1800.0      # 30-min reports
STATUS_EVERY_S = 60.0
HEARTBEAT_EVERY_S = 15.0
CONSECUTIVE_FAIL_LIMIT = 25
SERVICE_DOWN_GRACE_S = 60.0
RAM_MIN_AVAIL_GB = 2.5

# stop quotas (V3 §14): statistics first, wall clock second. All must hold.
QUOTA_ENABLED = os.environ.get("FLYLOOP_QUOTA", "1") == "1"
QUOTA_NEW = 150              # first-time rules (per run, both families pooled)
QUOTA_VARIANT = 75           # near-parameter variants
QUOTA_RECALL = 75            # exact recurrences (the primary statistic unit)
QUOTA_SHOCKS = 100           # fact shock events observed

# engineering-invalid tripwires (V3 §14): an engineering failure voids the run
# as a hypothesis test WITHOUT scoring it as a negative result.
MAX_MEM_ENTRIES = 60000      # per arm; beyond this the store is corrupted
MAX_READBACK_FAIL_FRAC = 0.05

# --- speed knobs (world clock, not wall clock) ----------------------------------
FACT_SHOCK_EVERY = 600       # v3: 600 (was 750) -> shock quota lands ~60k cycles
SEQ_STEPS_PER_CYCLE = 2
SPEED_PACING_MS = float(os.environ.get("FLYLOOP_PACING_MS", "70"))  # per arm pass

# --- lane configuration ---------------------------------------------------------
SEED = 20260927

# fact lane: 24 stations, channel rotates on a per-station period (+ shocks)
FACT_STATIONS = 24
FACT_DOMAIN = "ABCDE"
FACT_PERIOD0 = 350
FACT_PERIOD_STEP = 30
FACT_ARM = "ab"              # "recall" | "lookup" | "ab": A/B alternating per query

# sequence lane: char-level markov stream, regime shifts every 500 positions
SEQ_V = 16
SEQ_REGIME_LEN = 500
SEQ_N_REGIMES = 3
SEQ_CTX = 32
SEQ_TRAIN_FRAC = 0.25        # trainable partition of every weight tensor
SEQ_LR = 1e-3
SEQ_D, SEQ_LAYERS, SEQ_HEADS, SEQ_FFN = 128, 3, 4, 256
SEQ_K_FRAC = 0.25
SEQ_SHOWER = False
SEQ_STREAM_B = True          # dual stream: B gets a regime token (identifiability)

# puzzle lane: 4 families of y=(a*x+b) mod 13; episodes follow a precomputed
# recurrent schedule. V4: episodes have VARIABLE lengths in probes — short
# episodes end before the abstraction loop (fit -> consec=3 -> book write)
# completes, creating the discovery-failure variation the discovered-vs-
# undiscovered contrast needs (V3's FULL abstracted 100% of rules, so the
# contrast had zero variation). Type mix and gaps unchanged from V3.
PUZ_FAMILIES = 4
PUZ_P = 13
PUZ_PERIOD0 = int(os.environ.get("FLYLOOP_PUZ_PERIOD0", "500"))
PUZ_PERIOD_STEP = int(os.environ.get("FLYLOOP_PUZ_PERIOD_STEP", "150"))
PUZ_DISC_CONSEC = 3
PUZ_RECALL_TOPK = 8          # raise to catch both table and rule entries
EPISODE_MIX = {"NEW": 0.50, "VARIANT": 0.25, "RECALL": 0.25}
RECALL_GAPS = [2, 3, 4, 5]   # epochs since the returning rule was last active
MAX_EPISODES = 240           # (v3 legacy; v4 uses MAX_EPISODES_V4)
BOOK_TEST_K = 5              # recency window of book candidates tested per probe
# V4 length mix: probes per episode. A family is probed every 8 cycles
# (cycle c with c%2==0 and (c//2)%4==f), so n_probes -> cycle length is 8n.
# Short episodes (4-6 probes) usually end before consec reaches 3.
PUZ_PROBE_CADENCE = 8
EPISODE_PROBE_LENS = [4, 6, 10, 20, 40]
EPISODE_PROBE_WEIGHTS = [0.15, 0.15, 0.25, 0.25, 0.20]
# V5 observation noise: the REVEALED pair's y1 flips to a different value with
# probability NOISE_EPS (truth untouched — measurement noise, not drift). Pure
# function of (fam, cycle, seed), identical across arms. Run A (V4) is the
# eps=0 baseline; see V5_DESIGN.md.
NOISE_EPS = float(os.environ.get("FLYLOOP_NOISE_EPS", "0"))
# V6 tolerant matching: a memory candidate (rule / archived table) matches the
# live observations when it reproduces >= MATCH_MIN_FRAC of them exactly
# (strict argmax, recency tiebreak). 1.0 = exact (V4/V5 behavior). Under flip
# noise the true rule reproduces ~0.75 of live pairs while wrong rules sit at
# ~1/13 — the fraction separates them where the all-pairs criterion could not
# (V6_DESIGN.md). Scoring stays exact; only identification is tolerant.
MATCH_MIN_FRAC = float(os.environ.get("FLYLOOP_MATCH_MIN_FRAC", "1.0"))
# horizon/mix arithmetic (do not eyeball): mean length 17 probes = 136 cycles
# -> ~310 episodes/family in 42k cycles -> NEW ~155/family, just inside the
# 156 distinct (a,b) pairs per family; the 200-draw NEW fallback covers the
# tail. A 3-arm run reaches ~30-40k cycles in 10h, so the horizon binds only
# in pathological fast runs (past it, a family's rule freezes; deadline-first).
MAX_EPISODES_V4 = 300        # per family within the schedule horizon
SCHEDULE_HORIZON = 42000     # cycles the precomputed schedule covers
# quota-gated noise phases: advance on cumulative NEW-episode starts (pooled
# over families), never on cycle thresholds (V3 P07/P08 lesson)
NOISE_PHASE_GATES = [("A", 0), ("B", 50), ("C", 110)]   # by NEW count
NOISE_EVERY_BY_PHASE = {"A": 20, "B": 10, "C": 5}

# distractor pressure, quota-gated (V4): phases advance on cumulative
# NEW-episode starts (NOISE_PHASE_GATES), never on cycle thresholds.
# world.puz_phase(cycle) is the only reader.
FACT_REFRESH_EVERY = 600

# word anchors & personas (calibrated with MiniLM; see DESIGN_V2 §2).
# v3 fix: FACT_FEAT2[0] used to duplicate FACT_FEAT1[0] (self-repeat persona,
# a degenerate calibration hazard found in the v2 audit) — replaced with a
# distinct clause; re-calibrated with the real emitters before launch.
FACT_WORDS = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf",
              "hotel", "india", "juliett", "kilo", "lima", "mike", "november",
              "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform",
              "victor", "whiskey", "xray"]
FACT_CITY = ["兰州", "洛阳", "扬州", "泉州", "徐州", "常州", "沧州", "苏州", "杭州",
             "广州", "福州", "郑州", "株洲", "锦州", "荆州", "温州", "台州", "滁州",
             "湖州", "梅州", "梧州", "柳州", "泸州", "贵港"]
# Two feature clauses per station, greedy-optimized pairings (real MiniLM
# emitters): cross-station max < 0.75 merge line; same-station update
# in-place rewrite; query self-hit first. Re-measured on every edit.
FACT_FEAT1 = ['粮仓外运的集站', '河道转运的码头', '侗寨支线的尾站', '口岸查验的关口',
              '盐矿支线的尽头', '梯田粮线的仓站', '温泉旅游线的站', '多雾多山的枢纽',
              '陶瓷外运的货场', '竹林纸运的渡口', '果园集散的枢纽', '煤运重线的交点',
              '蔗糖专线的库站', '湖泽船运的接点', '高原专线的起点', '古渡遗留的老站',
              '茶马古道的驿站', '油菜花季的支线', '芦苇编织的集点', '边境互市的通道',
              '夜班编组的场站', '渔港冷链的中转', '酒曲运输的专线', '风沙区段的孤站']
FACT_FEAT2 = ['百货中转的货栈', '茶马古道的驿站', '梯田粮线的仓站', '果园集散的枢纽',
              '风沙区段的孤站', '边境互市的通道', '温泉旅游线的站', '河道转运的码头',
              '夜班编组的场站', '油菜花季的支线', '芦苇编织的集点', '高原专线的起点',
              '陶瓷外运的货场', '湖泽船运的接点', '多雾多山的枢纽', '盐矿支线的尽头',
              '蔗糖专线的库站', '古渡遗留的老站', '侗寨支线的尾站', '酒曲运输的专线',
              '口岸查验的关口', '煤运重线的交点', '竹林纸运的渡口', '渔港冷链的中转']
FACT_DESC = [f"{c}，{f1}，{f2}" for c, f1, f2 in zip(FACT_CITY, FACT_FEAT1, FACT_FEAT2)]
PUZ_WORDS = ["red", "blue", "gold", "silver"]
PUZ_DESC = ["红族世袭算术名家，总把规律藏在一阶线性式里，讲究一击即中",
            "蓝族以严谨著称，逐条记录观测，从不跳过任何一步验证",
            "金族偏爱小素数上的模运算，自信规则总能被两次观测点破",
            "银族冷静挑剔，只在证据充分时才肯写下一条规则"]

# --- memory write policy ---------------------------------------------------------
COMPARTMENT_FACT = "flyloop-fact"
COMPARTMENT_PUZZLE = "flyloop-puzzle"
COMPARTMENT_RULE = "flyloop-rule"
COMPARTMENT_NOISE = "flyloop-noise"
RECALL_TOPK = 6
# v2: rules live in ONE global book entry (read via state_lookup, which does not
# truncate); per-family table entries carry ASCII heads. Calibrated against the
# real emitters: cross-family tables 0.69, book-vs-anything max 0.57.
# v3: the book is a RULE REGISTRY — every rule ever discovered stays, carrying
# the epoch it was last active in; recurrences are recognized by testing recent
# book candidates against the live observation (see reasoner.predict_puzzle_v3).
# The EPISODIC arm never writes the book; it pays byte/count-matched padding
# writes (PAD_STATE_KEY) so both arms buy the same total write pressure.
TABLE_WRITE_EVERY = 8       # fold an observed pair into the table every Nth probe
PAD_STATE_KEY = "flyloop/pad"
PAD_HEAD = "PADLOG"
# v3 book = ONE entry PER FAMILY, holding the family's most recent rules only.
# Rationale (smoke_v3_1790532091 autopsy): the engine's split_chunks cuts texts
# >120 chars into multiple chunks, and the v4 atomicity guard then REJECTS any
# state_key write that produces >1 chunk -- an unbounded registry silently
# stopped updating at ~120 chars. Per-family entries with the 5 most recent
# rules stay <120 chars forever, and RECALL gaps are 2-5 epochs, so the cap
# loses no recurrence coverage.
BOOK_STATE_KEY = "flyloop/book/f{fam}"
BOOK_CAP = 5                # recent rules kept per family (gaps are 2-5)
# v4 MATCHED arm: episodic pair-table archive, one entry per episode (unique
# state_key per episode -> no in-place overwrites -> history survives), same
# cap depth as the book. The archive entry text reuses the table payload
# format (pairs first) with its own head, in its own compartment.
COMPARTMENT_EPIREG = "flyloop-epireg"
EPIREG_STATE_KEY = "flyloop/epi/{fam}/e{ep}"
# distinct CJK heads + a family tag on every pair token (measured, real
# MiniLM: cross-family 0.731 < 0.75; the shared-template first draft measured
# 0.962 — same failure mode as the v1 book). Matcher reads via state_lookup
# (exact key), so this is hygiene, not a load-bearing path.
EPIREG_HEADS = ["钟表铺的原始记录，齿轮转一遍记一笔",
                "账房先生的流水簿，进出笔笔即时录",
                "观星台的速记板，星位随见随画",
                "裁缝铺的纸样袋，剪一刀存一页"]
EPIREG_CAP = 5              # archive depth used by the matcher

# --- insight/ledger ----------------------------------------------------------------
ROLL_WINDOW = 100
DRIFT_PRE_WINDOW = 60
DRIFT_POST_WINDOW = 60
SIGNATURE_RATIO_MIN = 1.5
REC_WINDOW = 20              # probes per episode scored for recovery
