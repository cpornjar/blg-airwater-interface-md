"""
blg_fig_hbonds.py
=================
HBond count time series — BLG CENTER run, 3-panel figure (Fig 4 prep).
Plots protein-protein, protein-water, interface water-water HBond counts vs time.

Input:  results/analysis/blg_hbonds_CENTER.npz
Output: results/figures/blg_fig_hbonds_CENTER.png
"""

import sys
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from plot_style import apply_style, COLORS, double_width, savefig, smooth_sg

DATA = ROOT / "results" / "analysis" / "blg_hbonds_CENTER.npz"
OUT  = ROOT / "results" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def main():
    apply_style()

    d       = np.load(DATA)
    time_ns = d["time_ns"]
    n_pp    = d["n_prot_prot"]
    n_pw    = d["n_prot_water"]
    n_ww    = d["n_water_interface"]

    panel_data = [
        ("Protein–protein",    n_pp, COLORS["backbone"],
         float(d["mean_prot_prot"]),      n_pp.std()),
        ("Protein–water",      n_pw, COLORS["helix"],
         float(d["mean_prot_water"]),     n_pw.std()),
        ("Interface H₂O–H₂O", n_ww, COLORS["beta"],
         float(d["mean_water_interface"]),n_ww.std()),
    ]

    fig, axes = plt.subplots(3, 1, figsize=(double_width, 5.5), sharex=True)
    fig.subplots_adjust(hspace=0.08)

    for ax, (label, arr, color, mean, std) in zip(axes, panel_data):
        ax.plot(time_ns, arr,
                color=color, lw=0.5, alpha=0.30)
        ax.plot(time_ns, smooth_sg(arr, window=51, poly=3),
                color=color, lw=1.2,
                label=f"{label}:  {mean:.0f} ± {std:.0f}")
        ax.axhline(mean, color="0.55", lw=0.7, ls="--")
        ax.set_ylabel("H-bond count")
        ax.legend(loc="upper right", handlelength=1.2)

    axes[-1].set_xlabel("Time (ns)")
    axes[0].set_title(
        "BLG CENTER — Hydrogen bond counts (1000 ns, STRIDE=5 frames)", pad=4)

    savefig(fig, OUT / "blg_fig_hbonds_CENTER.png")
    print("Done.")


if __name__ == "__main__":
    main()
