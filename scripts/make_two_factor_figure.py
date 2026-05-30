"""
make_two_factor_figure.py — publication-quality Fig 4 (Langmuir ACS style)
============================================================================
Two-factor gating of BLG adsorption at the air-water interface.

Three panels:
  (a) Hydrophobic SASA and calyx angle vs time — decoupled dynamics
  (b) 2-D joint distribution (SASA, angle) — the empty gate quadrant
  (c) Two-factor gate model schematic (2×2 matrix)

Data: results/gate_analysis/R1_gate.npz (825.5 ns, 1652 frames, stride=5)
Out:  results/figures/TWO_FACTOR_GATE_Fig4.png

Usage:
    source ~/research-env/bin/activate
    python scripts/make_two_factor_figure.py
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from plot_style import apply_style, COLORS, double_width, savefig
apply_style()

NPZ = ROOT / "results" / "gate_analysis" / "R1_gate.npz"
OUT = ROOT / "results" / "figures" / "TWO_FACTOR_GATE_Fig4.png"

SASA_THR  = 35.0   # nm² — activated
ANGLE_THR = 30.0   # degrees — aligned

# ── Load cached gate data ─────────────────────────────────────────────────────
print(f"Loading {NPZ.name} …")
z          = np.load(NPZ)
times      = z["time"]    # ns
sasa_vals  = z["sasa"]    # nm²
angle_vals = z["angle"]   # degrees
print(f"  {len(times)} frames  |  {times[0]:.1f}–{times[-1]:.1f} ns")

activated = sasa_vals  >= SASA_THR
aligned   = angle_vals <= ANGLE_THR
gate_open = activated & aligned

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(double_width * 1.45, 4.8))   # 9.8 × 4.8 in
gs  = gridspec.GridSpec(1, 3, width_ratios=[2.4, 1.5, 1.1],
                        left=0.07, right=0.97, bottom=0.13, top=0.93,
                        wspace=0.42)

# ── Panel (a): SASA + angle time series ───────────────────────────────────────
ax_a  = fig.add_subplot(gs[0])
ax_a2 = ax_a.twinx()

# shade activated frames
for i in range(len(times) - 1):
    if activated[i]:
        ax_a.axvspan(times[i], times[i+1], color=COLORS["hydrophob"],
                     alpha=0.12, linewidth=0, zorder=0)

# SASA trace
ax_a.plot(times, sasa_vals, color=COLORS["hydrophob"], lw=0.8, alpha=0.85,
          label="Hydrophobic SASA", zorder=2)
ax_a.axhline(SASA_THR, color=COLORS["hydrophob"], lw=1.2, ls="--", alpha=0.7,
             zorder=3)

# angle trace
ax_a2.plot(times, angle_vals, color=COLORS["interface"], lw=0.8, alpha=0.75,
           label="Calyx angle", zorder=2)
ax_a2.axhline(ANGLE_THR, color=COLORS["interface"], lw=1.2, ls="--", alpha=0.7,
              zorder=3)

# threshold labels at right margin (avoids legend clutter)
ax_a.text(times[-1] + 5, SASA_THR, f"{SASA_THR:.0f} nm²",
          va="center", fontsize=6.5, color=COLORS["hydrophob"],
          clip_on=False)
ax_a2.text(times[-1] + 5, ANGLE_THR, f"{ANGLE_THR:.0f}°",
           va="center", fontsize=6.5, color=COLORS["interface"],
           clip_on=False)

ax_a.set_xlabel("Time (ns)")
ax_a.set_ylabel("Hydrophobic SASA (nm²)", color=COLORS["hydrophob"])
ax_a2.set_ylabel("Calyx angle to interface (°)", color=COLORS["interface"])
ax_a.tick_params(axis="y", colors=COLORS["hydrophob"])
ax_a2.tick_params(axis="y", colors=COLORS["interface"])
ax_a2.set_ylim(0, 180)
ax_a2.set_yticks([0, 30, 60, 90, 120, 150, 180])
ax_a.set_xlim(times[0], times[-1])

# compact legend — two items, lower right
handles = [
    mpatches.Patch(color=COLORS["hydrophob"], alpha=0.7, label="Hydrophobic SASA"),
    mpatches.Patch(color=COLORS["interface"], alpha=0.7, label="Calyx angle"),
]
ax_a.legend(handles=handles, loc="lower right", framealpha=0.9, fontsize=7)
ax_a.set_title("(a)  SASA and orientation — decoupled dynamics",
               fontsize=8.5, fontweight="bold", loc="left", pad=4)

# annotate gate stats in upper left (clear region)
pct_act = 100 * activated.mean()
pct_ali = 100 * aligned.mean()
pct_gate = 100 * gate_open.mean()
ax_a.text(0.02, 0.97,
          f"Activated (SASA ≥ {SASA_THR:.0f} nm²): {pct_act:.1f}%\n"
          f"Aligned (θ ≤ {ANGLE_THR:.0f}°): {pct_ali:.1f}%\n"
          f"Gate open (both): {pct_gate:.2f}%",
          transform=ax_a.transAxes, va="top", ha="left",
          fontsize=6.5, linespacing=1.5,
          bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                    edgecolor="0.7", alpha=0.90))

# ── Panel (b): 2-D histogram SASA vs angle ────────────────────────────────────
ax_b = fig.add_subplot(gs[1])

valid = ~np.isnan(sasa_vals)
h, xedges, yedges = np.histogram2d(
    angle_vals[valid], sasa_vals[valid],
    bins=[30, 25], range=[[0, 180], [20, 65]]
)
h_masked = np.ma.masked_where(h == 0, h)
h_max    = h_masked.compressed().max() if h_masked.count() > 0 else 1
norm     = mcolors.LogNorm(vmin=1, vmax=max(h_max, 2))

im = ax_b.pcolormesh(xedges, yedges, h_masked.T,
                     cmap="YlOrRd", norm=norm, rasterized=True)
cb = plt.colorbar(im, ax=ax_b, pad=0.02, fraction=0.046)
cb.set_label("Frame count", fontsize=7.5)
cb.ax.tick_params(labelsize=7)

# gate quadrant box
gate_box = mpatches.Rectangle(
    (0, SASA_THR), ANGLE_THR, 65 - SASA_THR,
    fill=False, edgecolor="#27AE60", linewidth=1.8, linestyle="--", zorder=5
)
ax_b.add_patch(gate_box)

# GATE label centred inside the box
ax_b.text(ANGLE_THR / 2, (SASA_THR + 65) / 2, "GATE\n(empty)",
          ha="center", va="center", fontsize=8, fontweight="bold",
          color="#27AE60", zorder=6)

# threshold lines
ax_b.axhline(SASA_THR, color=COLORS["hydrophob"], lw=0.9, ls=":", alpha=0.7)
ax_b.axvline(ANGLE_THR, color=COLORS["interface"], lw=0.9, ls=":", alpha=0.7)

ax_b.set_xlabel("Calyx angle to interface (°)")
ax_b.set_ylabel("Hydrophobic SASA (nm²)")
ax_b.set_xlim(0, 180)
ax_b.set_ylim(20, 65)
ax_b.set_title("(b)  Two-factor gate\n(green box = adsorption-competent region)",
               fontsize=8.5, fontweight="bold", loc="left", pad=4)

# ── Panel (c): schematic 2×2 matrix ───────────────────────────────────────────
# Layout mirrors panel (b) 2-D histogram:
#   x-axis: calyx angle — left col = aligned (low angle), right col = random
#   y-axis: SASA        — top row = high SASA (activated), bottom = low SASA
#   Gate = top-left (aligned + high SASA) — matches the empty quadrant in (b)
ax_c = fig.add_subplot(gs[2])
ax_c.set_xlim(-0.15, 2.15)
ax_c.set_ylim(-0.35, 2.65)
ax_c.axis("off")
ax_c.set_title("(c)  Gate model", fontsize=8.5, fontweight="bold",
               loc="left", pad=4)

CELL_W, CELL_H = 0.90, 0.90
X0, Y0 = 0.12, 0.30   # lower-left origin

# (col, row, label, facecolor, textcolor, bold)
# col=0=left=aligned, col=1=right=random | row=1=top=high SASA, row=0=bottom=low SASA
cell_defs = [
    (0, 1, "✓ GATE\n(adsorption\ncompetent)",  "#C8F7C5", "#1A5C2A", True),   # top-left
    (1, 1, "Activated,\nbut misaligned\n(common)", "#FDECEA", COLORS["hydrophob"], False),  # top-right
    (0, 0, "Aligned,\nbut compact",              "#EBF5FB", COLORS["interface"],  False),  # bottom-left
    (1, 0, "Compact\n(baseline)",                "#F0F3F4", "#666666",           False),  # bottom-right
]

for col, row, label, fc, tc, bold in cell_defs:
    x = X0 + col * (CELL_W + 0.08)
    y = Y0 + row * (CELL_H + 0.08)
    rect = mpatches.FancyBboxPatch(
        (x, y), CELL_W, CELL_H,
        boxstyle="round,pad=0.05",
        facecolor=fc, edgecolor="#AAAAAA", linewidth=0.8
    )
    ax_c.add_patch(rect)
    ax_c.text(x + CELL_W / 2, y + CELL_H / 2, label,
              ha="center", va="center", fontsize=7,
              fontweight="bold" if bold else "normal", color=tc,
              linespacing=1.35)

# x-axis labels (below matrix)
x_col0 = X0 + CELL_W / 2
x_col1 = X0 + CELL_W + 0.08 + CELL_W / 2
ax_c.text(x_col0, Y0 - 0.20, f"Aligned\n(θ ≤ {ANGLE_THR:.0f}°)",
          ha="center", va="top", fontsize=7, color=COLORS["interface"])
ax_c.text(x_col1, Y0 - 0.20, "Random\norientation",
          ha="center", va="top", fontsize=7, color=COLORS["interface"])

# y-axis labels (left of matrix)
y_top  = Y0 + CELL_H + 0.08 + CELL_H / 2
y_bot  = Y0 + CELL_H / 2
ax_c.text(X0 - 0.12, y_top, f"High SASA\n(≥{SASA_THR:.0f} nm²)",
          ha="right", va="center", fontsize=7, color=COLORS["hydrophob"],
          rotation=90)
ax_c.text(X0 - 0.12, y_bot, "Low\nSASA",
          ha="right", va="center", fontsize=7, color=COLORS["hydrophob"],
          rotation=90)

# GATE label above the matrix (not overlapping cells)
gate_label_y = Y0 + 2 * CELL_H + 0.08 + 0.12
ax_c.text(X0 + CELL_W / 2, gate_label_y, "← rare\n(GATE)",
          ha="center", va="bottom", fontsize=7, color="#27AE60",
          fontweight="bold", linespacing=1.3)

# ── Save ──────────────────────────────────────────────────────────────────────
savefig(fig, OUT)
print(f"\nPanel summary:")
print(f"  (a) SASA {sasa_vals.min():.1f}–{sasa_vals.max():.1f} nm²  |  "
      f"angle {angle_vals.min():.0f}–{angle_vals.max():.0f}°")
print(f"  Activated: {pct_act:.1f}%  |  Aligned: {pct_ali:.1f}%  |  "
      f"Gate: {pct_gate:.2f}%")
