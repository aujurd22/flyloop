import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

eps = [0.00, 0.05, 0.15, 0.25, 0.30, 0.40]
f_e20 = [2.347, 0.543, 1.102, 3.586, 2.600, 4.155]
m_e20 = [4.653, 1.286, 3.265, 4.509, 5.571, 4.155]
e_e20 = [4.918, 1.600, 3.429, 4.792, 5.714, 6.759]

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(eps, f_e20, "o-", color="#2b6cb0", markersize=10, linewidth=2.5, label="FULL (rule registry)")
ax.plot(eps, m_e20, "s--", color="#c05621", markersize=8, linewidth=2, label="MATCHED (episodic archive)")
ax.plot(eps, e_e20, "^:", color="#718096", markersize=8, linewidth=2, label="EPISODIC (no memory)")
ax.set_xlabel("observation flip probability (ε)", fontsize=12)
ax.set_ylabel("E20 on RECALL episodes", fontsize=12)
ax.set_title("Noise dose-response: moderate noise is optimal for rule memory", fontsize=13)
ax.legend(fontsize=11)
ax.annotate("optimal zone\n(ε=0.05-0.15)", xy=(0.10, 0.8), xytext=(0.12, 2.5),
            fontsize=10, arrowprops=dict(arrowstyle="->", color="#38a169"),
            color="#276749")
plt.tight_layout()
plt.savefig("docs/figs/eps_dose_response_full.png", dpi=150, bbox_inches="tight")
plt.close()
print("saved")
