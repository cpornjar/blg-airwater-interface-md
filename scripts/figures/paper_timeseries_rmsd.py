"""
scripts/figures/paper_timeseries_rmsd.py
==========================================
BLG RMSD vs time (backbone + calyx patch), all 4 replicas, as line
traces -- shows R1's patch RMSD stepping up after its long contact
event, not just the elevated mean.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plot_style import apply_style, COLORS, savefig
import matplotlib.pyplot as plt
import numpy as np

apply_style()

ROOT = Path(__file__).resolve().parents[2]
ANA = ROOT / "results" / "analysis"

run_color = {
    "CENTER": COLORS["center"], "R1": COLORS["replica1"],
    "R2": COLORS["replica2"], "R3": COLORS["replica3"],
}

fig, axes = plt.subplots(2, 1, figsize=(6.0, 5.4), sharex=True)

for ax, key, label in zip(axes, ["rmsd_backbone", "rmsd_patch"], ["Backbone", "Calyx patch"]):
    for run in ["CENTER", "R1", "R2", "R3"]:
        d = np.load(ANA / f"blg_rmsd_{run}.npz")
        ax.plot(d["time_ns"], d[key], color=run_color[run], lw=0.6, alpha=0.85,
                label=run)
    ax.set_ylabel("RMSD (nm)")
    ax.text(0.99, 0.92, f"({'a' if label=='Backbone' else 'b'}) {label}",
            transform=ax.transAxes, fontsize=8, fontweight="bold", ha="right")

axes[0].legend(loc="upper left", ncol=4, fontsize=6.5, framealpha=0.9)
axes[1].set_xlabel("Time (ns)")

fig.tight_layout()
out = ROOT / "results" / "figures" / "paper" / "PAPER_TIMESERIES_RMSD.png"
savefig(fig, out)
