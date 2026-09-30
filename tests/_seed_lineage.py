# -*- coding: utf-8 -*-
import json
lin = {
 "objective": "minimize FULL E20 on discovered-rule RECALL episodes; SIR floor >= 20 counts; menu mutations only",
 "generations": [
  {"gen": -2, "run": "v4_20260928_1636", "config": {"MATCH_MIN_FRAC": 1.0, "BOOK_CAP": 5, "NOISE_EPS": 0.0},
   "FULL_E20": 0.431, "note": "eps=0 control"},
  {"gen": -1, "run": "v5b_20260928_1848", "config": {"MATCH_MIN_FRAC": 1.0, "BOOK_CAP": 5, "NOISE_EPS": 0.25},
   "FULL_E20": 3.621, "note": "noise baseline"},
  {"gen": 0, "run": "v6t_20260928_2159", "config": {"MATCH_MIN_FRAC": 0.6, "BOOK_CAP": 5, "NOISE_EPS": 0.25},
   "FULL_E20": 2.347, "note": "M2 exercised: tolerance accepted"},
  {"gen": 3, "run": "rsi0_g3_20260930_0808",
   "config": {"MATCH_MIN_FRAC": "adaptive (0.6 base, rolling flip adjust)",
              "BOOK_CAP": 5, "NOISE_EPS": 0.25},
   "FULL_E20": 2.000, "note": "G3 accepted: adaptive read policy (-0.347 vs parent)"},
 ],
 "struck_mutations": ["M1 naive cap raise (mechanically infeasible)",
                      "M1 feasible re-encoding (no E20 improvement)"],
}
with open("runs/rsi0_lineage.json", "w", encoding="utf-8") as f:
    json.dump(lin, f, ensure_ascii=False, indent=1)
print("lineage updated")
