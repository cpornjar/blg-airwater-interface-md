"""
make_fig4_optionA.py — Fig 4 (Option A): honest SASA/orientation distribution
===============================================================================
Drops the gate-quadrant framing. Shows two panels:
  (a) Per-replica SASA distribution — calyx exposure range is 24–37 nm²,
      never reaching a clean "activated" regime
  (b) All-replica 2-D joint distribution (angle vs SASA) — orientation is
      uniform and decoupled from SASA at any level

No gate-quadrant overlay. Caption will state: calyx SASA confined 24–37 nm²;
orientation uniform; contact does not elevate SASA or select orientation.

Out: results/figures/Fig4_optionA.png
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
from scipy.stats import gaussian_kde

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from plot_style import apply_style, COLORS, double_width, savefig_pdf as savefig
apply_style()

OUT = ROOT / "results" / "figures" / "paper" / "Fig4_optionA.png"
GATE_DIR = ROOT / "results" / "gate_analysis"

REPLICAS = {
    "CENTER": ("center",   COLORS["center"]),
    "R1":     ("replica1", COLORS["replica1"]),
    "R2":     ("replica2", COLORS["replica2"]),
    "R3":     ("replica3", COLORS["replica3"]),
}

# ── Load data ─────────────────────────────────────────────────────────────────
all_sasa, all_angle = [], []
rep_sasa, rep_angle = {}, {}

for label, (ckey, col) in REPLICAS.items():
    z = np.load(GATE_DIR / f"{label}_gate.npz")
    s, a = z["sasa"], z["angle"]
    rep_sasa[label]  = s
    rep_angle[label] = a
    all_sasa.append(s)
    all_angle.append(a)
    print(f"  {label}: {len(s)} frames  SASA {s.min():.1f}–{s.max():.1f} nm²  "
          f"angle {a.min():.0f}–{a.max():.0f}°")

s_all = np.concatenate(all_sasa)
a_all = np.concatenate(all_angle)
print(f"  Total: {len(s_all)} frames")

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(double_width, 4.4))
gs  = gridspec.GridSpec(1, 2, width_ratios=[1, 1.6],
                        left=0.09, right=0.97, bottom=0.18, top=0.97,
                        wspace=0.38)

# ── Panel (a): SASA distribution per replica (KDE) ───────────────────────────
ax_a = fig.add_subplot(gs[0])

sasa_range = np.linspace(22, 40, 300)
color_list = [COLORS[v[0]] for v in REPLICAS.values()]

for (label, (ckey, col)), s_rep in zip(REPLICAS.items(), rep_sasa.values()):
    kde = gaussian_kde(s_rep, bw_method=0.15)
    density = kde(sasa_range)
    ax_a.plot(sasa_range, density, color=col, lw=1.4, label=label, alpha=0.85)
    ax_a.fill_between(sasa_range, density, alpha=0.10, color=col)

P95 = 32.10  # distribution-based threshold: top 5% SASA, chosen without reference to Obs/Indep

ax_a.set_xlabel("Hydrophobic SASA (nm²)")
ax_a.set_ylabel("Probability density")
ax_a.set_xlim(22, 40)
ax_a.legend(bbox_to_anchor=(0.5, -0.15), loc="upper center", ncol=4,
            fontsize=7, framealpha=0.9)
ax_a.text(0.03, 0.97, "(a)", transform=ax_a.transAxes,
          fontsize=9, fontweight="bold", va="top", ha="left")

# p95 dashed line — value is in stats box and caption; no internal label needed
ax_a.axvline(P95, color="0.35", lw=0.9, ls="--", alpha=0.8)

# Stats in caption — no box inside axes

# ── Panel (b): 2-D joint distribution, all replicas, no gate box ──────────────
ax_b = fig.add_subplot(gs[1])

h, xedges, yedges = np.histogram2d(
    a_all, s_all,
    bins=[36, 30], range=[[0, 180], [22, 40]]
)
h_masked = np.ma.masked_where(h == 0, h)
h_max    = h_masked.compressed().max() if h_masked.count() > 0 else 1
norm     = mcolors.LogNorm(vmin=1, vmax=max(h_max, 2))

im = ax_b.pcolormesh(xedges, yedges, h_masked.T,
                     cmap="YlOrRd", norm=norm, rasterized=True)
cb = plt.colorbar(im, ax=ax_b, pad=0.02, fraction=0.046)
cb.set_label("Frame count (log scale)", fontsize=7.5)
cb.ax.tick_params(labelsize=7)

# p95 line only (no quadrant box)
ax_b.axhline(P95, color="0.35", lw=0.9, ls="--", alpha=0.8,
             label=f"p95 = {P95:.1f} nm²")
ax_b.axvline(30, color=COLORS["interface"], lw=0.9, ls=":", alpha=0.7,
             label="θ ≤ 30° (aligned)")

ax_b.set_xlabel("Calyx angle to interface (°)")
ax_b.set_ylabel("Hydrophobic SASA (nm²)")
ax_b.set_xlim(0, 180)
ax_b.set_ylim(22, 40)
ax_b.legend(loc="upper right", fontsize=7, framealpha=0.9)
ax_b.text(0.03, 0.97, "(b)", transform=ax_b.transAxes,
          fontsize=9, fontweight="bold", va="top", ha="left")

# Annotate Obs/Indep at p95
pct_act = 100 * (s_all >= P95).mean()
pct_ali = 100 * (a_all <= 30).mean()
obs     = ((s_all >= P95) & (a_all <= 30)).mean()
exp     = (s_all >= P95).mean() * (a_all <= 30).mean()
ratio   = obs / exp if exp > 0 else float("nan")

# Stats moved to caption — no text boxes inside the 2-D KDE panel

# ── Save ──────────────────────────────────────────────────────────────────────
savefig(fig, OUT)
print(f"\nOption A:")
print(f"  SASA range (all): {s_all.min():.1f}–{s_all.max():.1f} nm²  "
      f"mean {s_all.mean():.2f} nm²")
print(f"  Angle range:      {a_all.min():.0f}–{a_all.max():.0f}°  "
      f"mean {a_all.mean():.1f}°")
print(f"  Activated (p95={P95:.1f}): {pct_act:.2f}%  Aligned: {pct_ali:.2f}%  "
      f"Obs/Indep={ratio:.3f}")
