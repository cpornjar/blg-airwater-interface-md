"""
make_fig4_optionB.py — Fig 4 (Option B): p95 threshold with honest CI
=======================================================================
Keeps the gate-quadrant framing but uses the distribution-based p95 =
32.10 nm² threshold (top 5% SASA, chosen without reference to Obs/Indep
outcome) and reports honest Obs/Indep = 0.92 with 95% CI [0.54, 1.31] —
CI straddles 1.0, meaning no statistically significant suppression is
observed. Per-replica breakdown is shown in panel (c).

Three panels (same layout as original Fig 4):
  (a) R1 SASA + angle timeseries — p95 threshold line
  (b) All-replica 2-D histogram — p95 × 30° gate quadrant (green box)
  (c) 2×2 schematic — updated with Obs/Indep and CI

Out: results/figures/Fig4_optionB_p95.png
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

OUT      = ROOT / "results" / "figures" / "Fig4_optionB_p95.png"
GATE_DIR = ROOT / "results" / "gate_analysis"

SASA_THR  = 32.10   # nm²  — p95 of pooled PBC-corrected SASA
ANGLE_THR = 30.0    # degrees — unchanged (a priori geometric criterion)

# Bootstrap CIs from LOO jackknife + 5000-resample bootstrap at p95 threshold
CI_LO = 0.543
CI_HI = 1.311

# ── Load data ─────────────────────────────────────────────────────────────────
def load_npz(label):
    z = np.load(GATE_DIR / f"{label}_gate.npz")
    return z["time"], z["sasa"], z["angle"], z["min_dist"]

t1, s1, a1, d1 = load_npz("R1")
print(f"R1: {len(t1)} frames  SASA {s1.min():.1f}–{s1.max():.1f} nm²")

# All replicas for panels (b) and (c) — also compute per-replica Obs/Indep
REPLICAS = ("CENTER", "R1", "R2", "R3")
all_s, all_a = [], []
per_rep = {}
for lbl in REPLICAS:
    z = np.load(GATE_DIR / f"{lbl}_gate.npz")
    s, a = z["sasa"], z["angle"]
    all_s.append(s); all_a.append(a)
    act = s >= SASA_THR
    ali = a <= ANGLE_THR
    indep = act.mean() * ali.mean()
    oi = (act & ali).mean() / indep if indep > 0 else float("nan")
    per_rep[lbl] = oi
    tag = f"{oi:.2f}" if not np.isnan(oi) else "n/a"
    print(f"  {lbl}: act={100*act.mean():.1f}%  ali={100*ali.mean():.1f}%  Obs/Ind={tag}")

s_all = np.concatenate(all_s)
a_all = np.concatenate(all_a)
print(f"All: {len(s_all)} frames")

activated1 = s1 >= SASA_THR
aligned1   = a1 <= ANGLE_THR
gate_open1 = activated1 & aligned1

act_all = s_all >= SASA_THR
ali_all = a_all <= ANGLE_THR
go_all  = act_all & ali_all
obs_exp = act_all.mean() * ali_all.mean()
OBS_OVER_INDEP = go_all.mean() / obs_exp if obs_exp > 0 else float("nan")
print(f"Computed Obs/Indep = {OBS_OVER_INDEP:.3f}  (bootstrap CI: [{CI_LO:.3f}, {CI_HI:.3f}])")

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(double_width * 1.45, 4.8))
gs  = gridspec.GridSpec(1, 3, width_ratios=[2.4, 1.5, 1.1],
                        left=0.07, right=0.97, bottom=0.13, top=0.93,
                        wspace=0.42)

# ── Panel (a): R1 SASA + angle timeseries ─────────────────────────────────────
ax_a  = fig.add_subplot(gs[0])
ax_a2 = ax_a.twinx()

# shade activated frames (p95 definition)
for i in range(len(t1) - 1):
    if activated1[i]:
        ax_a.axvspan(t1[i], t1[i+1], color=COLORS["hydrophob"],
                     alpha=0.12, linewidth=0, zorder=0)

ax_a.plot(t1, s1, color=COLORS["hydrophob"], lw=0.8, alpha=0.85,
          label="Hydrophobic SASA", zorder=2)
ax_a.axhline(SASA_THR, color=COLORS["hydrophob"], lw=1.2, ls="--", alpha=0.7,
             zorder=3)

ax_a2.plot(t1, a1, color=COLORS["interface"], lw=0.8, alpha=0.75,
           label="Calyx angle", zorder=2)
ax_a2.axhline(ANGLE_THR, color=COLORS["interface"], lw=1.2, ls="--", alpha=0.7,
              zorder=3)

# threshold labels
ax_a.text(t1[-1] + 5, SASA_THR, f"{SASA_THR:.1f} nm²\n(p95)",
          va="center", fontsize=6.0, color=COLORS["hydrophob"], clip_on=False)
ax_a2.text(t1[-1] + 5, ANGLE_THR, f"{ANGLE_THR:.0f}°",
           va="center", fontsize=6.5, color=COLORS["interface"], clip_on=False)

ax_a.set_xlabel("Time (ns)")
ax_a.set_ylabel("Hydrophobic SASA (nm²)", color=COLORS["hydrophob"])
ax_a2.set_ylabel("Calyx angle to interface (°)", color=COLORS["interface"])
ax_a.tick_params(axis="y", colors=COLORS["hydrophob"])
ax_a2.tick_params(axis="y", colors=COLORS["interface"])
ax_a2.set_ylim(0, 180)
ax_a2.set_yticks([0, 30, 60, 90, 120, 150, 180])
ax_a.set_xlim(t1[0], t1[-1])

handles = [
    mpatches.Patch(color=COLORS["hydrophob"], alpha=0.7, label="Hydrophobic SASA"),
    mpatches.Patch(color=COLORS["interface"], alpha=0.7, label="Calyx angle"),
]
ax_a.legend(handles=handles, loc="lower right", framealpha=0.9, fontsize=7)
ax_a.set_title("(a)  R1: SASA and orientation dynamics\n(distribution-based threshold: top 5% SASA = 32.1 nm²)",
               fontsize=8.5, fontweight="bold", loc="left", pad=4)

pct_act1  = 100 * activated1.mean()
pct_ali1  = 100 * aligned1.mean()
pct_gate1 = 100 * gate_open1.mean()
ax_a.text(0.02, 0.97,
          f"Activated (SASA ≥ p95): {pct_act1:.1f}%\n"
          f"Aligned (θ ≤ {ANGLE_THR:.0f}°): {pct_ali1:.1f}%\n"
          f"Gate open (both): {pct_gate1:.2f}%",
          transform=ax_a.transAxes, va="top", ha="left",
          fontsize=6.5, linespacing=1.5,
          bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                    edgecolor="0.7", alpha=0.90))

# ── Panel (b): All-replica 2-D histogram with p95 gate box ────────────────────
ax_b = fig.add_subplot(gs[1])

h, xedges, yedges = np.histogram2d(
    a_all, s_all,
    bins=[30, 25], range=[[0, 180], [22, 40]]
)
h_masked = np.ma.masked_where(h == 0, h)
h_max    = h_masked.compressed().max() if h_masked.count() > 0 else 1
norm     = mcolors.LogNorm(vmin=1, vmax=max(h_max, 2))

im = ax_b.pcolormesh(xedges, yedges, h_masked.T,
                     cmap="YlOrRd", norm=norm, rasterized=True)
cb = plt.colorbar(im, ax=ax_b, pad=0.02, fraction=0.046)
cb.set_label("Frame count", fontsize=7.5)
cb.ax.tick_params(labelsize=7)

# gate quadrant box (p95 threshold)
gate_box = mpatches.Rectangle(
    (0, SASA_THR), ANGLE_THR, 40 - SASA_THR,
    fill=False, edgecolor="#27AE60", linewidth=1.8, linestyle="--", zorder=5
)
ax_b.add_patch(gate_box)

# GATE label + Obs/Indep with CI inside the box
ax_b.text(ANGLE_THR / 2, (SASA_THR + 40) / 2,
          f"GATE\nObs/Ind={OBS_OVER_INDEP:.2f}\n95% CI [{CI_LO:.2f},{CI_HI:.2f}]",
          ha="center", va="center", fontsize=6.5, fontweight="bold",
          color="#27AE60", zorder=6, linespacing=1.4)

ax_b.axhline(SASA_THR, color=COLORS["hydrophob"], lw=0.9, ls=":", alpha=0.7)
ax_b.axvline(ANGLE_THR, color=COLORS["interface"], lw=0.9, ls=":", alpha=0.7)

ax_b.set_xlabel("Calyx angle to interface (°)")
ax_b.set_ylabel("Hydrophobic SASA (nm²)")
ax_b.set_xlim(0, 180)
ax_b.set_ylim(22, 40)
ax_b.set_title("(b)  Joint distribution (all 4 replicas)\ngate = θ ≤ 30°, SASA ≥ p95",
               fontsize=8.5, fontweight="bold", loc="left", pad=4)

# ── Panel (c): 2×2 schematic — updated with Obs/Indep and CI ──────────────────
ax_c = fig.add_subplot(gs[2])
ax_c.set_xlim(-0.15, 2.15)
ax_c.set_ylim(-0.70, 2.65)
ax_c.axis("off")
ax_c.set_title("(c)  Gate model", fontsize=8.5, fontweight="bold",
               loc="left", pad=4)

CELL_W, CELL_H = 0.90, 0.90
X0, Y0 = 0.12, 0.30

# Updated cell text — note Obs/Indep < 1 (no significant suppression)
cell_defs = [
    (0, 1, f"GATE\nObs/Ind={OBS_OVER_INDEP:.2f}\nCI [{CI_LO:.2f},{CI_HI:.2f}]",
     "#F5FCF4", "#27AE60", True),   # top-left — CI straddles 1.0
    (1, 1, "Activated,\nbut misaligned\n(common)", "#FDECEA", COLORS["hydrophob"], False),
    (0, 0, "Aligned,\nbut compact",                "#EBF5FB", COLORS["interface"],  False),
    (1, 0, "Compact\n(baseline)",                  "#F0F3F4", "#666666",            False),
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
              ha="center", va="center", fontsize=6.5,
              fontweight="bold" if bold else "normal", color=tc,
              linespacing=1.25)

x_col0 = X0 + CELL_W / 2
x_col1 = X0 + CELL_W + 0.08 + CELL_W / 2
ax_c.text(x_col0, Y0 - 0.20, f"Aligned\n(θ ≤ {ANGLE_THR:.0f}°)",
          ha="center", va="top", fontsize=7, color=COLORS["interface"])
ax_c.text(x_col1, Y0 - 0.20, "Random\norientation",
          ha="center", va="top", fontsize=7, color=COLORS["interface"])

y_top = Y0 + CELL_H + 0.08 + CELL_H / 2
y_bot = Y0 + CELL_H / 2
ax_c.text(X0 - 0.12, y_top, f"High SASA\n(≥p95\n{SASA_THR:.1f} nm²)",
          ha="right", va="center", fontsize=6.5, color=COLORS["hydrophob"],
          rotation=90)
ax_c.text(X0 - 0.12, y_bot, "Low\nSASA",
          ha="right", va="center", fontsize=7, color=COLORS["hydrophob"],
          rotation=90)

gate_label_y = Y0 + 2 * CELL_H + 0.08 + 0.12
ax_c.text(X0 + CELL_W / 2, gate_label_y, "← 5.0% frames\n(no suppression)",
          ha="center", va="bottom", fontsize=6.5, color="#27AE60",
          fontweight="bold", linespacing=1.3)

# Per-replica Obs/Indep breakdown — critical for transparency
def _oi_str(v):
    return f"{v:.2f}" if not np.isnan(v) else "n/a"

rep_lines = (f"Per-replica Obs/Ind (p95):\n"
             f"CTR:{_oi_str(per_rep['CENTER'])}  R1:{_oi_str(per_rep['R1'])}\n"
             f"R2:{_oi_str(per_rep['R2'])}  R3:{_oi_str(per_rep['R3'])}")
ax_c.text(X0 + CELL_W / 2, Y0 - 0.33, rep_lines,
          ha="center", va="top", fontsize=5.8, color="#555555",
          linespacing=1.35,
          bbox=dict(boxstyle="round,pad=0.25", facecolor="#F8F8F8",
                    edgecolor="0.75", alpha=0.90))

# ── Save ──────────────────────────────────────────────────────────────────────
savefig(fig, OUT)
pct_act_all = 100 * act_all.mean()
pct_ali_all = 100 * ali_all.mean()
print(f"\nOption B (p95 = {SASA_THR} nm²):")
print(f"  All-replica: activated={pct_act_all:.2f}%  aligned={pct_ali_all:.2f}%  "
      f"gate-open={100*go_all.mean():.2f}%  Obs/Indep={OBS_OVER_INDEP:.3f}")
print(f"  Bootstrap CI: [{CI_LO:.3f}, {CI_HI:.3f}]  (straddles 1.0)")
