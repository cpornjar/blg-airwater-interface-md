"""
scripts/figures/paper_comparative_rg.py
=========================================
Radius of gyration comparison, BLG (4 replicas) vs CASEIN (2 replicas),
for the P.P. progress report (2026-09-11 update).

CAVEAT: blg_rg.py's TRAJS dict for R1/R2/R3 never reads the extension
trajectory segments, so these three replicas' Rg here are computed from
only the first 500 of 1000 ns each replica actually ran (CENTER is
unaffected -- single unbroken file). See project memory
project_paper1_expansion.md session 17/19 for the full writeup. Do not
drop this comment when the underlying blg_rg.py fix eventually lands --
update it to say the numbers are now full-length instead.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plot_style import apply_style, COLORS, savefig
import matplotlib.pyplot as plt

apply_style()

# mean, std (nm) -- read from results/analysis/{blg,cas}_rg_*.npz
blg = {"CENTER": (1.504, 0.022), "R1": (1.497, 0.009), "R2": (1.493, 0.008), "R3": (1.499, 0.012)}
cas = {"CENTER": (2.652, 0.209), "R1": (2.477, 0.223)}

run_color = {
    "CENTER": COLORS["center"], "R1": COLORS["replica1"],
    "R2": COLORS["replica2"], "R3": COLORS["replica3"],
}

fig, ax = plt.subplots(figsize=(4.2, 3.4))

x = 0
xticks, xlabels = [], []
gap = 0.4
group_centers = {}
for label, data in [("BLG", blg), ("CASEIN", cas)]:
    start = x
    for run, (mean, std) in data.items():
        ax.bar(x, mean, yerr=std, width=0.7, color=run_color[run],
               edgecolor="black", linewidth=0.5, capsize=3)
        xticks.append(x)
        xlabels.append(run)
        x += 1
    group_centers[label] = (start + (x - 1)) / 2
    x += gap

ax.set_ylabel(r"$R_g$ (nm)")
ax.set_xticks(xticks)
ax.set_xticklabels(xlabels, fontsize=7)
ax.text(group_centers["BLG"], -0.55, "BLG", ha="center", fontsize=8, fontweight="bold")
ax.text(group_centers["CASEIN"], -0.55, "CASEIN", ha="center", fontsize=8, fontweight="bold")
ax.set_ylim(0, 3.2)
ax.axvline((3 + 4.4) / 2, color="0.6", lw=0.6, ls=":")

fig.tight_layout()
out = Path(__file__).resolve().parents[2] / "results" / "figures" / "paper" / "PAPER_COMPARATIVE_RG.png"
savefig(fig, out)
