"""
scripts/figures/paper_timeseries_rg.py
========================================
Radius of gyration vs time, BLG (4 replicas) and CASEIN (2 replicas),
as line-trace panels (not summary bars) -- shows the actual trend/
fluctuation over the trajectory, not just the mean+-std.

CAVEAT: blg_rg.py's TRAJS dict for R1/R2/R3 never reads the extension
trajectory segments, so these three replicas' traces here stop at 500
ns (visible directly in the plot -- CENTER continues to 1000 ns, the
other three don't). See project memory project_paper1_expansion.md
session 17/19 for the full writeup. Update this comment once the
underlying blg_rg.py fix lands and the traces are regenerated full-length.
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

# --- (a) BLG ---
ax = axes[0]
for run in ["CENTER", "R1", "R2", "R3"]:
    d = np.load(ANA / f"blg_rg_{run}.npz")
    ax.plot(d["time_ns"], d["rg_nm"], color=run_color[run], lw=0.6, alpha=0.85,
            label=f"BLG {run}")
ax.set_ylabel(r"$R_g$ (nm)")
ax.set_ylim(1.4, 1.65)
ax.legend(loc="upper right", ncol=4, fontsize=6.5, framealpha=0.9)
ax.text(0.01, 0.92, "(a) BLG", transform=ax.transAxes, fontsize=8, fontweight="bold")

# --- (b) CASEIN ---
ax = axes[1]
for run in ["CENTER", "R1"]:
    d = np.load(ANA / f"cas_rg_{run}.npz")
    ax.plot(d["time_ns"], d["rg_nm"], color=run_color[run], lw=0.6, alpha=0.85,
            label=f"CASEIN {run}")
ax.set_xlabel("Time (ns)")
ax.set_ylabel(r"$R_g$ (nm)")
ax.legend(loc="upper right", ncol=2, fontsize=7, framealpha=0.9)
ax.text(0.01, 0.92, "(b) CASEIN", transform=ax.transAxes, fontsize=8, fontweight="bold")

fig.tight_layout()
out = ROOT / "results" / "figures" / "paper" / "PAPER_TIMESERIES_RG.png"
savefig(fig, out)
