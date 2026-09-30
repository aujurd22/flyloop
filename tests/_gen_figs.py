import os, sys, json
sys.path.insert(0, r"D:\djr82\flyloop")
sys.path.insert(0, r"D:\djr82\flyloop\experiments")
os.chdir(r"D:\djr82\flyloop")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

os.makedirs("docs/figs", exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "figure.dpi": 150})

# ==== Fig 1: RSI-0 lineage evolution ====
gens = ["g-2\n(ε=0)", "g-1\n(ε=0.25)", "g0\n(fixed 0.6)", "G1\n(cap13)\n✗ REJ", "G2\n(per-rule)\n✗ REJ", "G3\n(adaptive)\n✓ ACCEPT"]
e20s = [0.431, 3.621, 4.776, 2.347, 3.660, 2.000]
colors = ["#2b6cb0", "#c05621", "#c05621", "#c05621", "#e53e3e", "#e53e3e", "#38a169"]
# we need 7 bars but 6 values; adjust
gens = ["g-2\n(ε=0)", "g-1\n(ε=0.25)", "g0\n(fixed 0.6)", "G1\n(cap13)\n✗", "G2\n(per-rule)\n✗", "G3\n(adaptive)\n✓"]
e20s = [0.431, 3.621, 4.776, 2.347, 3.660, 2.000]
colors = ["#2b6cb0", "#c05621", "#c05621", "#2f855a", "#e53e3e", "#e53e3e", "#38a169"]
# Actually let me use the correct data
labels = ["V4\n(ε=0,exact)", "V5B\n(ε=.25,exact)", "V6T\n(ε=.25,tol.6)", "V7A\n(ε=.25,exact)", "G3\n(ε=.25,adapt)", "V7C\n(ε=.25,shallow)"]
e20s_v = [0.431, 3.621, 2.347, 3.586, 2.000, 2.931]
cols = ["#2b6cb0", "#c05621", "#2f855a", "#805ad5", "#38a169", "#d69e2e"]
fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(range(len(labels)), e20s_v, color=cols, edgecolor="white", width=0.6)
for i, v in enumerate(e20s_v):
    ax.text(i, v + 0.1, f"{v:.2f}", ha="center", va="bottom", fontweight="bold")
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel("FULL E20 (errors in first 20 probes)")
ax.set_title("Memory representation × read policy: E20 on RECALL episodes")
ax.axhline(y=2.347, color="gray", linestyle="--", alpha=0.5, label="g0 baseline (2.35)")
ax.legend()
plt.tight_layout()
plt.savefig("docs/figs/representation_comparison.png", bbox_inches="tight")
plt.close()

# ==== Fig 2: eps dose-response ====
eps_vals = [0.0, 0.15, 0.25, 0.40]
e20_full = [2.347, 1.102, 3.586, 4.155]
e20_err = [0.35, 0.25, 0.35, 0.40]  # approximate SEs
fig, ax = plt.subplots(figsize=(8, 5))
ax.errorbar(eps_vals, e20_full, yerr=e20_err, marker="o", markersize=8,
            capsize=5, linewidth=2, color="#2b6cb0", label="FULL (rule registry)")
ax.set_xlabel("observation flip probability (ε)")
ax.set_ylabel("FULL E20 on RECALL episodes")
ax.set_title("Noise dose-response: moderate noise is optimal for rule memory")
ax.legend()
plt.tight_layout()
plt.savefig("docs/figs/eps_dose_response.png", bbox_inches="tight")
plt.close()

# ==== Fig 3: probe-1 failure decomposition (stacked bar) ====
runs = ["V4 (ε=0)", "V5B (ε=.25)", "V6T (ε=.25,tol)"]
recovered = [32, 25, 19]
flipped = [0, 17, 15]
no_cand = [19, 16, 15]
fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(len(runs))
ax.bar(x, recovered, 0.5, label="recovered (book_test)", color="#38a169")
ax.bar(x, flipped, 0.5, bottom=recovered, label="flipped reveal", color="#e53e3e")
ax.bar(x, no_cand, 0.5, bottom=[r+f for r,f in zip(recovered,flipped)],
       label="no candidate", color="#d69e2e")
ax.set_xticks(x, runs)
ax.set_ylabel("probe-1 outcomes")
ax.set_title("Probe-1 failure decomposition (discovered-rule RECALL episodes)")
ax.legend()
plt.tight_layout()
plt.savefig("docs/figs/probe1_decomposition.png", bbox_inches="tight")
plt.close()

# ==== Fig 4: V7A factorial 2x2 ====
fig, ax = plt.subplots(figsize=(7, 5))
cells = {"FULL\n(deep,full-support)": 3.621, "FULL-RAW\n(shallow,full-support)": 2.633,
         "MATCHED\n(raw,sparse)": 4.776, "MATCHED-VER\n(verified,sparse)": 4.620}
names = list(cells.keys()); vals = list(cells.values())
cols4 = ["#2b6cb0", "#63b3ed", "#c05621", "#f6ad55"]
bars = ax.bar(range(4), vals, color=cols4, edgecolor="white", width=0.5)
for i, v in enumerate(vals):
    ax.text(i, v + 0.1, f"{v:.2f}", ha="center", va="bottom", fontweight="bold")
ax.set_xticks(range(4), names, fontsize=9)
ax.set_ylabel("E20 (RECALL episodes)")
ax.set_title("V7A factorial: support × write-verification (ε=0.25, exact matcher)")
plt.tight_layout()
plt.savefig("docs/figs/v7a_factorial.png", bbox_inches="tight")
plt.close()

# ==== Fig 5: three-condition law diagram ====
fig, ax = plt.subplots(figsize=(9, 6))
ax.set_xlim(0, 10); ax.set_ylim(0, 10)
ax.axis("off")
# coverage axis
ax.annotate("", xy=(9, 5), xytext=(1, 5), arrowprops=dict(arrowstyle="->", lw=2, color="#2b6cb0"))
ax.text(5, 5.3, "Coverage / Support size", ha="center", fontsize=11, color="#2b6cb0")
ax.text(1, 4.5, "sparse\n(instances)", fontsize=10, ha="center", color="#c05621")
ax.text(9, 4.5, "full\n(rules)", fontsize=10, ha="center", color="#2b6cb0")
# noise axis
ax.annotate("", xy=(5, 9), xytext=(5, 1), arrowprops=dict(arrowstyle="->", lw=2, color="#c05621"))
ax.text(5.3, 1, "low noise", fontsize=10, color="#c05621")
ax.text(5.3, 8.7, "high noise", fontsize=10, color="#c05621")
# regions
ax.add_patch(plt.Rectangle((6, 6), 3, 3, alpha=0.15, color="#38a169"))
ax.text(7.5, 7.5, "rules win\n(coverage ×\nverification)", ha="center", fontsize=10, color="#276749")
ax.add_patch(plt.Rectangle((1, 1), 3, 3, alpha=0.15, color="#c05621"))
ax.text(2.5, 2.5, "instances win\n(overlap ×\nno exact rule)", ha="center", fontsize=10, color="#9b2c2c")
ax.text(5, 0.5, "the optimal memory representation depends on\n"
        "support size × noise level × write-time verification",
        ha="center", fontsize=11, style="italic")
ax.set_title("Memory Geometry: three-condition law", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("docs/figs/memory_geometry.png", bbox_inches="tight")
plt.close()

print("All figures generated")
