"""
scripts/figures/paper_timeseries_sasa.py
==========================================
SASA vs time: BLG calyx (4 replicas) and CASEIN N-terminal 1-25
(2 replicas) -- line traces showing both proteins' accessible-area
trend over the trajectory, not just the mean+-std bar.
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

# --- (a) BLG calyx SASA ---
ax = axes[0]
for run in ["CENTER", "R1", "R2", "R3"]:
    d = np.load(ANA / f"blg_calyx_sasa_{run}.npz")
    ax.plot(d["time_ns"], d["calyx_sasa_nm2"], color=run_color[run], lw=0.5, alpha=0.8,
            label=f"BLG {run}")
ax.set_ylabel("Calyx SASA (nm$^2$)")
ax.set_ylim(0, 8)
ax.legend(loc="upper right", ncol=4, fontsize=6.5, framealpha=0.9)
ax.text(0.01, 0.92, "(a) BLG calyx", transform=ax.transAxes, fontsize=8, fontweight="bold")

# --- (b) CASEIN N-term SASA ---
ax = axes[1]
for run in ["CENTER", "R1"]:
    d = np.load(ANA / f"cas_nterm_sasa_{run}.npz")
    ax.plot(d["time_ns"], d["nterm_sasa_nm2"], color=run_color[run], lw=0.5, alpha=0.8,
            label=f"CASEIN {run}")
ax.set_xlabel("Time (ns)")
ax.set_ylabel("N-term SASA (nm$^2$)")
ax.set_ylim(15, 32)
ax.legend(loc="upper right", ncol=2, fontsize=7, framealpha=0.9)
ax.text(0.01, 0.92, "(b) CASEIN N-term", transform=ax.transAxes, fontsize=8, fontweight="bold")

fig.tight_layout()
out = ROOT / "results" / "figures" / "paper" / "PAPER_TIMESERIES_SASA.png"
savefig(fig, out)
