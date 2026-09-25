"""
scripts/figures/paper_timeseries_contact.py
==============================================
Signed protein-to-interface gap vs time: BLG (4 replicas, from
gate_analysis) vs CASEIN (2 replicas, from cas_contact) -- the
clearest visual of "selective/intermittent" (BLG) vs "constant"
(CASEIN) interfacial contact behavior.

NOTE on sign convention (both blg_gate_analysis.py and cas_contact.py
use the identical formula, confirmed): this is NOT a plain atom-to-atom
distance. It is min(d_up, d_lo) where d_up/d_lo are the gaps between
the protein's extremities and the water region's 2nd/98th-percentile
z-boundary. Positive = protein fully inside the water bulk, away from
the interface. Negative = protein already extends PAST the water's
statistical edge, i.e. into the interfacial/vacuum region. CASEIN's
mean is actually negative (~-0.6 nm) -- it doesn't just touch the
interface, it persistently protrudes beyond it. An earlier version of
this figure clipped the y-axis at 0, which hid this entirely and made
CASEIN's trace look like it vanished after ~10 ns -- fixed here.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plot_style import apply_style, COLORS, savefig
import matplotlib.pyplot as plt
import numpy as np

apply_style()

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "results" / "gate_analysis"
ANA = ROOT / "results" / "analysis"

run_color = {
    "CENTER": COLORS["center"], "R1": COLORS["replica1"],
    "R2": COLORS["replica2"], "R3": COLORS["replica3"],
}
CONTACT_NM = 0.3

fig, axes = plt.subplots(2, 1, figsize=(6.0, 5.4), sharex=True)

YLIM = (-1.6, 2.2)

# --- (a) BLG: min_dist vs time ---
ax = axes[0]
for run in ["CENTER", "R1", "R2", "R3"]:
    d = np.load(GATE / f"{run}_gate.npz")
    ax.plot(d["time"], d["min_dist"], color=run_color[run], lw=0.4, alpha=0.75, label=run)
ax.axhline(CONTACT_NM, color="black", lw=0.8, ls="--", alpha=0.6)
ax.axhline(0, color="black", lw=0.6, ls="-", alpha=0.4)
ax.set_ylabel("Signed gap to\ninterface (nm)")
ax.set_ylim(*YLIM)
ax.legend(loc="upper right", ncol=4, fontsize=6.5, framealpha=0.9)
ax.text(0.01, 0.93, "(a) BLG -- mostly positive (in bulk), brief negative dips",
        transform=ax.transAxes, fontsize=7.5, fontweight="bold")

# --- (b) CASEIN: dmin vs time ---
ax = axes[1]
for run in ["CENTER", "R1"]:
    d = np.load(ANA / f"cas_contact_{run}.npz")
    ax.plot(d["time_ns"], d["dmin_nm"], color=run_color[run], lw=0.4, alpha=0.75, label=run)
ax.axhline(CONTACT_NM, color="black", lw=0.8, ls="--", alpha=0.6,
           label=f"{CONTACT_NM} nm contact threshold")
ax.axhline(0, color="black", lw=0.6, ls="-", alpha=0.4, label="interface edge (0 nm)")
ax.set_xlabel("Time (ns)")
ax.set_ylabel("Signed gap to\ninterface (nm)")
ax.set_ylim(*YLIM)
ax.legend(loc="upper right", ncol=2, fontsize=6.5, framealpha=0.9)
ax.text(0.01, 0.93, "(b) CASEIN -- mostly negative (protruding past interface)",
        transform=ax.transAxes, fontsize=7.5, fontweight="bold")

fig.tight_layout()
out = ROOT / "results" / "figures" / "paper" / "PAPER_TIMESERIES_CONTACT.png"
savefig(fig, out)
