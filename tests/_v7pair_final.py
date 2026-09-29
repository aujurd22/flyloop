import sys
import os; os.chdir(r"D:djr82lyloop")
sys.path.insert(0, r"D:\djr82\flyloop\experiments")
import os
os.chdir(r"D:\djr82\flyloop")
from compare_v7 import load_probes_v7, load_insights
import numpy as np

g2 = load_probes_v7(r"runs\rsi0_g2_20260929_0029")
first2 = load_insights(r"runs\rsi0_g2_20260929_0029")
F, M, E = g2["FULL"], g2["MATCHED"], g2["EPISODIC"]
keys = sorted(set(F) & set(M) & set(E))
rec = [k for k in keys if F[k]["type"] == "RECALL"]
for a, A in (("FULL", F), ("MATCHED", M), ("EPISODIC", E)):
    v = [A[k]["e20"] for k in rec]
    print(f"G2 {a}: RECALL n={len(v)} E20={np.mean(v):.3f}")

v7c = load_probes_v7(r"runs\v7c_20260929_0029")
Fd, Fr = v7c["FULL"], v7c["FULL-RAW"]
keys = sorted(set(Fd) & set(Fr))
rec = [k for k in keys if Fd[k]["type"] == "RECALL"]
d = np.array([Fr[k]["e20"] - Fd[k]["e20"] for k in rec], float)
cl = [Fd[k]["rule_id"] for k in rec]
rng = np.random.default_rng(11)
u = np.unique([c for c in cl if c])
ms = []
for _ in range(10000):
    k = rng.choice(u, size=len(u), replace=True)
    vals = np.concatenate([d[[cl[i] == x for i in range(len(cl))]] for x in k])
    ms.append(vals.mean())
print(f"V7C write-depth (shallow-deep): n={len(d)} mean={d.mean():+.3f} "
      f"CI[{np.percentile(ms,2.5):+.3f},{np.percentile(ms,97.5):+.3f}]")
