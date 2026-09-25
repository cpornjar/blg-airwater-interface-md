"""
scripts/figures/paper_comparative_rmsd.py
============================================
BLG RMSD comparison (backbone vs calyx patch), all 4 replicas,
for the P.P. progress report (2026-09-11 update). CASEIN has no
equivalent RMSD in this report -- BLG only.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plot_style import apply_style, COLORS, savefig
import matplotlib.pyplot as plt
import numpy as np

apply_style()

# backbone, patch (nm) -- read from results/analysis/blg_rmsd_*.npz means
replicas = ["CENTER", "R1", "R2", "R3"]
backbone = {"CENTER": 0.229, "R1": 0.237, "R2": 0.206, "R3": 0.268}
patch = {"CENTER": 0.198, "R1": 0.347, "R2": 0.254, "R3": 0.276}

run_color = {
    "CENTER": COLORS["center"], "R1": COLORS["replica1"],
    "R2": COLORS["replica2"], "R3": COLORS["replica3"],
}

fig, ax = plt.subplots(figsize=(4.6, 3.4))

x = np.arange(len(replicas))
width = 0.35

for i, run in enumerate(replicas):
    ax.bar(x[i] - width / 2, backbone[run], width, color=run_color[run],
           edgecolor="black", linewidth=0.5)
    ax.bar(x[i] + width / 2, patch[run], width, color=run_color[run],
           edgecolor="black", linewidth=0.5, hatch="////")

ax.set_ylabel("RMSD (nm)")
ax.set_xticks(x)
ax.set_xticklabels(replicas)
ax.set_ylim(0, 0.45)

from matplotlib.patches import Patch
legend_handles = [
    Patch(facecolor="white", edgecolor="black", linewidth=0.5, label="Backbone"),
    Patch(facecolor="white", edgecolor="black", linewidth=0.5, hatch="////", label="Calyx patch"),
]
ax.legend(handles=legend_handles, loc="upper left", fontsize=7)

fig.tight_layout()
out = Path(__file__).resolve().parents[2] / "results" / "figures" / "paper" / "PAPER_COMPARATIVE_RMSD.png"
savefig(fig, out)
