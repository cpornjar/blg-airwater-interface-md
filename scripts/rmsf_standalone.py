"""
rmsf_standalone.py
==================
Standalone publication figure: Per-residue RMSF with Loop BC highlighted.
This is Figure 6 in Paper 1 (Loop BC as predicted first-contact region).

Usage:
    cd outputs_BLG/CENTER/MD1000
    python ../../../scripts/rmsf_standalone.py
"""

import numpy as np
import matplotlib.pyplot as plt
import MDAnalysis as mda
from MDAnalysis.analysis import rms, align
from MDAnalysis.transformations import unwrap
from plot_style import (apply_style, COLORS, double_width,
                        ACTIVATION_WINDOWS, savefig)
apply_style()

# ── CONFIG ────────────────────────────────────────────────────────────────────
TPR_FILE   = "md_1000ns.tpr"
XTC_FILE   = "traj_comp.xtc"
OUTPUT_PNG = "../../../results/figures/rmsf/CENTER_1000ns_rmsf.png"
STRIDE     = 5

BETA_REGIONS  = [(2,8),(16,21),(29,35),(46,52),
                 (62,67),(75,82),(92,98),(106,113),(138,145)]
HELIX_REGION  = (130, 137)
LOOP_BC       = (30, 35)    # key prediction — first contact region
# ──────────────────────────────────────────────────────────────────────────────


def calc_rmsf(tpr, xtc, stride):
    u = mda.Universe(tpr, xtc)
    u.trajectory.add_transformations(unwrap(u.select_atoms("protein")))
    align.AlignTraj(u, u, select="backbone", in_memory=True).run()
    ca    = u.select_atoms("protein and name CA")
    R     = rms.RMSF(ca)
    R.run(step=stride)
    return ca.resids, R.results.rmsf / 10.0   # Å → nm


def plot(resids, rmsf):
    fig, ax = plt.subplots(figsize=(double_width, 2.8))

    # ── Background: secondary structure regions ───────────────────────────────
    for i, (s, e) in enumerate(BETA_REGIONS):
        ax.axvspan(s, e, alpha=0.10, color=COLORS["beta"],
                   label="β-sheet" if i == 0 else "", zorder=1)
    ax.axvspan(*HELIX_REGION, alpha=0.12, color=COLORS["helix"],
               label="α-helix (130–142)", zorder=1)

    # ── Loop BC highlight ─────────────────────────────────────────────────────
    ax.axvspan(*LOOP_BC, alpha=0.30, color=COLORS["patch"],
               label=f"Loop BC (res. {LOOP_BC[0]}–{LOOP_BC[1]})", zorder=2)

    # ── RMSF bars ─────────────────────────────────────────────────────────────
    ax.bar(resids, rmsf, color=COLORS["backbone"],
           alpha=0.8, width=1.0, zorder=3)

    # ── Reference lines ───────────────────────────────────────────────────────
    mean_val = np.mean(rmsf)
    thresh   = mean_val + 2 * np.std(rmsf)
    ax.axhline(mean_val, color="0.4", lw=0.8, ls="--",
               label=f"Mean = {mean_val:.3f} nm", zorder=4)
    ax.axhline(thresh, color=COLORS["helix"], lw=0.8, ls=":",
               label=f"Mean + 2σ = {thresh:.3f} nm", zorder=4)

    # ── Annotate Loop BC peak ─────────────────────────────────────────────────
    mask_bc  = (resids >= LOOP_BC[0]) & (resids <= LOOP_BC[1])
    if mask_bc.any():
        peak_res  = resids[mask_bc][np.argmax(rmsf[mask_bc])]
        peak_rmsf = rmsf[mask_bc].max()
        ax.annotate(f"Loop BC\npeak {peak_rmsf:.2f} nm",
                    xy=(peak_res, peak_rmsf),
                    xytext=(peak_res + 12, peak_rmsf + 0.03),
                    fontsize=7,
                    arrowprops=dict(arrowstyle="->", lw=0.7, color="black"),
                    ha="left", va="center")

    ax.set_xlabel("Residue number")
    ax.set_ylabel("RMSF (nm)")
    ax.set_xlim(resids.min() - 1, resids.max() + 1)
    ax.legend(loc="upper right", ncol=3, fontsize=7)

    # Print summary
    print(f"\nRMSF Summary:")
    print(f"  Mean ± std : {mean_val:.3f} ± {np.std(rmsf):.3f} nm")
    print(f"  Threshold  : {thresh:.3f} nm")
    flexible = resids[rmsf > thresh]
    print(f"  Highly flexible residues (> mean+2σ): {list(flexible)}")
    bc_vals  = rmsf[mask_bc]
    print(f"  Loop BC ({LOOP_BC[0]}-{LOOP_BC[1]}) RMSF: "
          f"mean {bc_vals.mean():.3f}, max {bc_vals.max():.3f} nm")

    savefig(fig, OUTPUT_PNG)


if __name__ == "__main__":
    import os
    os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)
    print(f"Computing RMSF from {XTC_FILE} ...")
    resids, rmsf = calc_rmsf(TPR_FILE, XTC_FILE, STRIDE)
    plot(resids, rmsf)
