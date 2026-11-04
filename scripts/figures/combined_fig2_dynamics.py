"""
scripts/figures/combined_fig2_dynamics.py
==========================================
Figure 2 - structural dynamics (RMSD/RMSF/Rg), BLG real + CAS pending.
"""
from pathlib import Path
import sys

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from plot_style import apply_style, COLORS, double_width, savefig
from utils import SPECIES, run_color, run_label, load_analysis, pending_panel

apply_style()

fig, axes = plt.subplots(3, 2, figsize=(double_width, 7.5))
# row 0 = RMSD, row 1 = RMSF, row 2 = Rg
# column 0 = BLG, column 1 = CAS (pending)

# ===== TODO: Rg panel (axes[2, 0]) =====
# CAVEAT (2026-09-09): R1/R2/R3 Rg data here only covers 0-500 ns, not the full
# 1000 ns each replica actually ran. blg_rg.py's TRAJS dict only reads the base
# traj_comp.xtc per replica and never concatenates the extension trajectories
# (md_replica{1,2,3}_*.part00*.xtc, which exist on disk). CENTER is unaffected
# (single unbroken 1000 ns file). Pending fix: extend blg_rg.py (and check
# blg_rmsd.py / RMSF for the same gap) to include the extension segments, then
# rerun and regenerate this figure. Do not treat current R1/R2/R3 Rg means as
# final 1000 ns numbers until that's done.
ax = axes[2, 0]
for run in SPECIES["BLG"] ["replicas"]:
    d = load_analysis("BLG", "rg", run)
    ax.plot(d["time_ns"], d["rg_nm"],
              color=run_color(run), lw=0.8, alpha=0.85,
              label=run_label("BLG", run))
ax.set_xlabel("Time (ns)")
ax.set_ylabel("Rg (nm)")
ax.legend(loc="upper right", ncol=2)
ax.set_title("BLG Rg", fontsize=9)
# ===== RMSD panel (axes[0, 0]) =====
# Solid = whole-backbone, dashed = calyx patch. Per-replica traces, NOT averaged:
# R1's patch RMSD steps up permanently after its longest contact event
# (362-419.5 ns), a real rearrangement that a mean would hide.
ax = axes[0, 0]
for run in SPECIES["BLG"]["replicas"]:
    d = load_analysis("BLG", "rmsd", run)
    ax.plot(d["time_ns"], d["rmsd_backbone"], color=run_color(run),
            lw=0.8, alpha=0.85, label=run_label("BLG", run))
    ax.plot(d["time_ns"], d["rmsd_patch"], color=run_color(run),
            lw=0.8, alpha=0.85, ls="--")
ax.plot([], [], color="k", lw=0.8, label="backbone")
ax.plot([], [], color="k", lw=0.8, ls="--", label="calyx patch")
ax.set_xlabel("Time (ns)")
ax.set_ylabel("RMSD (nm)")
ax.legend(loc="upper left", ncol=3, fontsize=6)
ax.set_title("BLG RMSD (solid: backbone, dashed: calyx patch)", fontsize=9)

# ===== RMSF panel (axes[1, 0]) =====
# Per-residue Calpha RMSF caches live in results/gate_analysis/rmsf_<label>.*.npy
ax = axes[1, 0]
for run in SPECIES["BLG"]["replicas"]:
    tag = run.lower()
    resids = np.load(ROOT / "results" / "gate_analysis" / f"rmsf_{tag}.resids.npy")
    rmsf = np.load(ROOT / "results" / "gate_analysis" / f"rmsf_{tag}.rmsf.npy")
    ax.plot(resids, rmsf, color=run_color(run), lw=0.8, alpha=0.85,
            label=run_label("BLG", run))
ax.set_xlabel("Residue")
ax.set_ylabel("RMSF (nm)")
ax.legend(loc="upper right", ncol=2)
ax.set_title("BLG RMSF", fontsize=9)

# ===== CAS pending panels (axes[0,1], axes[1,1], axes[2,1]) =====
for r in range(3):
    pending_panel(axes[r, 1], "CAS")

fig.tight_layout()
out = ROOT / "results" / "figures" / "paper" / "PAPER_FIG2_DYNAMICS.png"
savefig(fig, out)
