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

# sandbox FlyMemory instance (third instance; 8765=ZCode prod, 8766=WorkBuddy)
MEM_HOST = "127.0.0.1"
MEM_PORT = int(os.environ.get("FLYLOOP_PORT", "8767"))
MEM_URL = f"http://{MEM_HOST}:{MEM_PORT}/mcp"
SANDBOX_MEM_DIR = os.path.join(ROOT, "sandbox_mem", "flymemory")

# --- run budget (quota-stop rules; time is a ceiling, not a goal) --------------
DURATION_H = 5.0             # wall-clock ceiling for tonight's run
MAX_CYCLES = 150000          # hard safety cap
CHECKPOINT_EVERY_CYCLES = 50
CHECKPOINT_EVERY_S = 120.0
REPORT_EVERY_S = 1800.0      # 30-min reports (5h run -> ~10 reports)
STATUS_EVERY_S = 60.0
HEARTBEAT_EVERY_S = 15.0
CONSECUTIVE_FAIL_LIMIT = 25
SERVICE_DOWN_GRACE_S = 60.0
RAM_MIN_AVAIL_GB = 2.5

# stop quotas (satisfied -> graceful end, per DESIGN_V2 §8).
# DISABLED for this run: the user explicitly booked the full 5h window, so the
# deadline is the binding constraint; quotas stay as the documented v3 default.
QUOTA_ENABLED = False
QUOTA_SHOCKS = 60            # fact shock events observed
QUOTA_DISCOVERIES = 120      # rule discoveries
QUOTA_DREAMS = 0             # dream audits (instrument; 0 = disabled)

# --- speed knobs (world clock, not wall clock) ----------------------------------
FACT_SHOCK_EVERY = 750       # was 1500 -> halves time to 24 shocks
SEQ_STEPS_PER_CYCLE = 2      # was 1 update / 2 cycles -> 4x updates/hour
SPEED_PACING_MS = 250        # per-cycle floor (was 600)

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

# puzzle lane: 4 families of y=(a*x+b) mod 13; rules rotate on staggered periods
PUZ_FAMILIES = 4
PUZ_P = 13
PUZ_PERIOD0 = 800
PUZ_PERIOD_STEP = 200
PUZ_DISC_CONSEC = 3
PUZ_RECALL_TOPK = 8          # raise to catch both table and rule entries

# distractor stream
NOISE_EVERY = 20
FACT_REFRESH_EVERY = 600

# word anchors & personas (calibrated with MiniLM; see DESIGN_V2 §2)
FACT_WORDS = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf",
              "hotel", "india", "juliett", "kilo", "lima", "mike", "november",
              "oscar", "papa", "quebec", "romeo", "sierra", "tango", "uniform",
              "victor", "whiskey", "xray"]
FACT_CITY = ["兰州", "洛阳", "扬州", "泉州", "徐州", "常州", "沧州", "苏州", "杭州",
             "广州", "福州", "郑州", "株洲", "锦州", "荆州", "温州", "台州", "滁州",
             "湖州", "梅州", "梧州", "柳州", "泸州", "贵港"]
# Two feature clauses per station, greedy-optimized pairings (real MiniLM
# emitters): cross-station max 0.711 < 0.75 merge line; same-station update
# 0.983 (in-place rewrite); query self-hit 0.813. Re-measured on every edit.
FACT_FEAT1 = ['粮仓外运的集站', '河道转运的码头', '侗寨支线的尾站', '口岸查验的关口',
              '盐矿支线的尽头', '梯田粮线的仓站', '温泉旅游线的站', '多雾多山的枢纽',
              '陶瓷外运的货场', '竹林纸运的渡口', '果园集散的枢纽', '煤运重线的交点',
              '蔗糖专线的库站', '湖泽船运的接点', '高原专线的起点', '古渡遗留的老站',
              '茶马古道的驿站', '油菜花季的支线', '芦苇编织的集点', '边境互市的通道',
              '夜班编组的场站', '渔港冷链的中转', '酒曲运输的专线', '风沙区段的孤站']
FACT_FEAT2 = ['粮仓外运的集站', '茶马古道的驿站', '梯田粮线的仓站', '果园集散的枢纽',
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
TABLE_WRITE_EVERY = 8       # fold an observed pair into the table every Nth probe

# --- insight/ledger ----------------------------------------------------------------
ROLL_WINDOW = 100
DRIFT_PRE_WINDOW = 60
DRIFT_POST_WINDOW = 60
SIGNATURE_RATIO_MIN = 1.5
