"""
scripts/figures/paper_comparative_sasa.py
==========================================
BLG calyx SASA vs CASEIN N-terminal (1-25) SASA, all replicas -- the
headline comparative bar chart for the 2026-09-11 P.P. progress report.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plot_style import apply_style, COLORS, savefig
import matplotlib.pyplot as plt

apply_style()

# BLG calyx SASA per replica (mean, std)
blg = {"CENTER": (3.81, 0.46), "R1": (3.15, 0.34), "R2": (3.59, 0.32), "R3": (3.36, 0.48)}
# CAS N-term SASA per replica (mean, std)
cas = {"CENTER": (25.41, 1.97), "R1": (24.77, 1.40)}

run_color = {
    "CENTER": COLORS["center"], "R1": COLORS["replica1"],
    "R2": COLORS["replica2"], "R3": COLORS["replica3"],
}

fig, ax = plt.subplots(figsize=(4.2, 3.4))

x = 0
xticks, xlabels = [], []
gap = 0.4
group_centers = {}
for label, data in [("BLG calyx", blg), ("CAS N-term", cas)]:
    start = x
    for run, (mean, std) in data.items():
        ax.bar(x, mean, yerr=std, width=0.7, color=run_color[run],
               edgecolor="black", linewidth=0.5, capsize=3)
        xticks.append(x)
        xlabels.append(run)
        x += 1
    group_centers[label] = (start + (x - 1)) / 2   # true midpoint of this group's bars
    x += gap

ax.set_ylabel("SASA (nm$^2$)")
ax.set_xticks(xticks)
ax.set_xticklabels(xlabels, fontsize=7)
ax.text(group_centers["BLG calyx"], -6.5, "BLG calyx", ha="center", fontsize=8, fontweight="bold")
ax.text(group_centers["CAS N-term"], -6.5, "CAS N-term (1-25)", ha="center", fontsize=8, fontweight="bold")
ax.set_ylim(0, 30)
ax.axvline((3 + 4.4) / 2, color="0.6", lw=0.6, ls=":")

fig.tight_layout()
out = Path(__file__).resolve().parents[2] / "results" / "figures" / "paper" / "PAPER_COMPARATIVE_SASA.png"
savefig(fig, out)
