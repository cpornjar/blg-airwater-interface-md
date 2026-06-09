"""
make_slide_figs.py
==================
Regenerate ACADEMIC_NAVY presentation figures with fixed annotation positions.
All data loaded from pre-computed cache — no trajectory required.

Fixes applied:
  Fig 1  contact  — "In bulk water" moved left; annotation de-stacked; stats box clear
  Fig 2  SASA     — legend moved below x-axis; p95 label de-duplicated; annotation outside axes
  Fig 3  RMSF     — loop annotations repositioned above/below peaks, not on lines
  Fig 4  scatter  — legend moved to upper-left clear area; replica colors shown

Usage:
  conda run -n research-env python3 scripts/make_slide_figs.py
"""
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT    = Path(__file__).resolve().parent.parent.parent
GATE    = ROOT / "results" / "gate_analysis"
OUT_DIR = ROOT / "slides" / "COMFHA_Talk_May2026" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Dark ACADEMIC_NAVY palette ────────────────────────────────────────────────
BG      = "#0D1B2E"
PLOT_BG = "#0A1628"
TEXT    = "#E8EDF5"
SUB     = "#8FA5BC"
GOLD    = "#C9A84C"
TEAL    = "#4ECDC4"
AMBER   = "#F59E0B"
RED     = "#E07070"
DRED    = "#E74C3C"
DBLUE   = "#5BA4CF"
DGREEN  = "#5BAD8A"
DPURP   = "#A78BCC"

# replica colors consistent with paper plot_style.py
REP_COL = {
    "CENTER": "#C9A84C",  # gold
    "R1":     "#E07070",  # red
    "R2":     "#5BA4CF",  # blue
    "R3":     "#5BAD8A",  # green
}

def dark_style():
    plt.rcParams.update({
        "figure.facecolor"  : BG,
        "axes.facecolor"    : PLOT_BG,
        "axes.edgecolor"    : SUB,
        "axes.labelcolor"   : TEXT,
        "text.color"        : TEXT,
        "xtick.color"       : TEXT,
        "ytick.color"       : TEXT,
        "xtick.labelsize"   : 9,
        "ytick.labelsize"   : 9,
        "axes.labelsize"    : 10,
        "axes.titlesize"    : 12,
        "axes.titlecolor"   : TEXT,
        "legend.facecolor"  : "#0D1B2E",
        "legend.edgecolor"  : GOLD,
        "legend.labelcolor" : TEXT,
        "legend.fontsize"   : 9,
        "font.family"       : "sans-serif",
        "font.sans-serif"   : ["Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size"         : 10,
        "lines.linewidth"   : 1.3,
        "savefig.dpi"       : 200,
        "savefig.bbox"      : "tight",
        "savefig.facecolor" : BG,
    })

def save(fig, name):
    out = OUT_DIR / name
    fig.savefig(out, dpi=200, bbox_inches="tight", facecolor=BG)
    print(f"  → {out.name}")
    plt.close(fig)

# ── Load gate data ────────────────────────────────────────────────────────────
print("Loading gate data...")
gdata = {}
for rep in ["CENTER", "R1", "R2", "R3"]:
    z = np.load(GATE / f"{rep}_gate.npz")
    gdata[rep] = {
        "t"    : z["time"] / 1000.0,  # ns → µs
        "sasa" : z["sasa"],
        "angle": z["angle"],
        "dmin" : z["min_dist"],
    }
    print(f"  {rep}: {len(z['sasa'])} frames, SASA {z['sasa'].min():.1f}–{z['sasa'].max():.1f} nm²")

# Load RMSF
print("Loading RMSF cache...")
rc = np.load(GATE / "rmsf_center.resids.npy")
fc = np.load(GATE / "rmsf_center.rmsf.npy")
rr = np.load(GATE / "rmsf_r1.resids.npy")
fr = np.load(GATE / "rmsf_r1.rmsf.npy")

dark_style()

# =============================================================================
# FIG 1 — R1 Contact Trace  (single panel, distance to interface)
# =============================================================================
print("\nFig 1 — R1 contact trace...")

THRESH = 0.30   # nm, contact threshold (authoritative paper value)
t1  = gdata["R1"]["t"]    # µs
d1  = gdata["R1"]["dmin"] # nm

# detect contact events from gate data
contact = d1 <= THRESH
edges   = np.diff(contact.astype(int))
starts  = list(np.where(edges == 1)[0] + 1)
ends    = list(np.where(edges == -1)[0] + 1)
if contact[0]:  starts.insert(0, 0)
if contact[-1]: ends.append(len(d1))

fig, ax = plt.subplots(figsize=(15, 4.5))
ax.set_facecolor(PLOT_BG)

# shade contact events
for s, e in zip(starts, ends):
    ax.axvspan(t1[s], t1[min(e, len(t1)-1)], color=AMBER, alpha=0.18, zorder=0)

# reference lines
ax.axhline(0.0,   color=TEAL,  lw=1.4, ls="--", alpha=0.85, zorder=2,
           label="Interface (z=0)")
ax.axhline(THRESH, color=AMBER, lw=1.2, ls=":",  alpha=0.90, zorder=2,
           label=f"Contact threshold ({THRESH} nm)")

# data
ax.plot(t1, d1, color=DBLUE, lw=0.6, alpha=0.55, zorder=3, rasterized=True)

# y-axis limits
ax.set_ylim(-0.95, 1.55)
ax.set_xlim(t1[0], t1[-1])

# ── Authoritative stats box (top-right, clear of "In bulk water") ─────────────
stats_text = "R1  │  215 events  │  23.4% frames in contact  │  deepest −0.71 nm"
ax.annotate(stats_text,
            xy=(0.99, 0.97), xycoords="axes fraction",
            ha="right", va="top", fontsize=9, fontweight="bold", color="#0D1B2E",
            bbox=dict(boxstyle="round,pad=0.4", fc=GOLD, ec=GOLD, alpha=0.95))

# ── "In bulk water" label — LEFT side, well clear of stats box ────────────────
ax.text(0.01, 0.82, "In bulk water", transform=ax.transAxes,
        fontsize=8.5, color=SUB, va="top", ha="left", style="italic")

# ── Deepest penetration annotation — ABOVE the minimum point to avoid clipping ─
idx_min = int(np.argmin(d1))
t_min   = t1[idx_min]
d_min   = d1[idx_min]
# xytext placed above and left of minimum (d_min ~ −0.71 nm is near ylim −0.95,
# so text below the point would be clipped; anchor bottom of text at y=−0.45 instead).
# Use paper-verified depth (−0.71 nm from detect_adsorption_contact.py full resolution);
# gate data argmin uses stride 5 frames and may capture a slightly more negative frame.
ax.annotate(f"−0.71 nm  ·  past interface  @  ~{t_min:.2f} µs",
            xy=(t_min, d_min),
            xytext=(t_min - 0.12, -0.45),
            fontsize=8, color=RED,
            ha="center", va="bottom",
            arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.0),
            bbox=dict(boxstyle="round,pad=0.25", fc=PLOT_BG, ec=RED, alpha=0.85, lw=0.7))

ax.set_xlabel("Time (µs)", labelpad=6)
ax.set_ylabel("Distance to interface (nm)", labelpad=6)

# legend — small, upper LEFT, avoids stats box which is upper right
ax.legend(loc="upper left", fontsize=8, framealpha=0.88,
          bbox_to_anchor=(0.01, 0.96))

fig.tight_layout(pad=0.5)
save(fig, "slide_fig1_contact.png")

# =============================================================================
# FIG 2 — Calyx SASA All Four Replicas
# =============================================================================
print("Fig 2 — SASA all replicas...")

P95 = 32.10  # nm²

fig, ax = plt.subplots(figsize=(15, 5.5))
ax.set_facecolor(PLOT_BG)

# Small bottom margin for x-axis label and teal annotation
fig.subplots_adjust(bottom=0.12)

for rep, col in REP_COL.items():
    d = gdata[rep]
    ax.plot(d["t"], d["sasa"], color=col, lw=0.8, alpha=0.75, label=rep)

# p95 dashed line — NO duplicate left-side label; label only in legend
ax.axhline(P95, color=TEXT, lw=1.2, ls="--", alpha=0.7, label=f"p95 = {P95:.1f} nm²")

ax.set_xlabel("Time (µs)", labelpad=6)
ax.set_ylabel("Calyx SASA (nm²)", labelpad=6)
ax.set_title("Calyx SASA — All Four Replicas (PBC-corrected, 4.00 µs total)",
             pad=10, fontsize=12, fontweight="bold")
ax.set_ylim(22, 38.5)
ax.set_xlim(0, 1.0)

# ── Legend INSIDE axes — top-center sparse zone (data ceiling ~36.7 nm², ylim 38.5) ──
ax.legend(loc="upper center", ncol=5,
          fontsize=9, framealpha=0.90, handlelength=1.5)

# ── Summary annotation at figure bottom margin ────────────────────────────────
fig.text(0.5, 0.01,
         "Recurring bursts every ~30–40 ns  │  Stationary stochastic process  │  NOT a one-shot activation",
         ha="center", va="bottom", fontsize=8.5, color=TEAL,
         bbox=dict(boxstyle="round,pad=0.35", fc="#091525", ec=TEAL, alpha=0.90, lw=0.8))

save(fig, "slide_fig2_sasa.png")

# =============================================================================
# FIG 3 — RMSF per residue: CENTER (bulk) vs R1 (near AWI)
# =============================================================================
print("Fig 3 — RMSF comparison...")

BC_LO, BC_HI = 30, 36    # Loop BC residue range
CD_LO, CD_HI = 57, 61    # Loop CD/EF residue range

fig, ax = plt.subplots(figsize=(15, 5.0))
ax.set_facecolor(PLOT_BG)
fig.subplots_adjust(top=0.88)

# shaded loop regions (behind lines)
ax.axvspan(BC_LO, BC_HI, color=GOLD,  alpha=0.12, zorder=0)
ax.axvspan(CD_LO, CD_HI, color=TEAL,  alpha=0.12, zorder=0)

# RMSF lines
ax.plot(rc, fc, color=GOLD, lw=1.6, alpha=0.90, label="CENTER (bulk)", zorder=3)
ax.plot(rr, fr, color=TEAL, lw=1.6, alpha=0.90, label="R1 (near AWI)", zorder=3)

# ── Annotations positioned to AVOID line overlap ──────────────────────────────
# Loop BC peak for CENTER: res 34, RMSF ~0.535 nm
# → label ABOVE the gold peak
ax.annotate("Loop BC\n(bulk dominant)",
            xy=(34, fc[(rc >= BC_LO) & (rc <= BC_HI)].max()),
            xytext=(20, 0.57),
            fontsize=8.5, color=GOLD, ha="right", va="bottom",
            arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=0.9),
            bbox=dict(boxstyle="round,pad=0.25", fc=PLOT_BG, ec=GOLD, alpha=0.85, lw=0.7))

# Loop CD/EF peak for R1: res 59, RMSF ~0.385 nm
# → label BELOW the teal peak (at y=0.22, pointing up)
ax.annotate("Loop CD/EF\n(AWI dominant)",
            xy=(59, fr[(rr >= CD_LO) & (rr <= CD_HI)].max()),
            xytext=(76, 0.20),
            fontsize=8.5, color=TEAL, ha="left", va="top",
            arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=0.9),
            bbox=dict(boxstyle="round,pad=0.25", fc=PLOT_BG, ec=TEAL, alpha=0.85, lw=0.7))

# "Interface proximity" summary — upper right; legend anchored below it to avoid overlap
ax.text(0.99, 0.98,
        "Interface proximity\nshifts dominant loop",
        transform=ax.transAxes, fontsize=8.5, color=TEXT,
        ha="right", va="top", style="italic",
        bbox=dict(boxstyle="round,pad=0.3", fc=PLOT_BG, ec=SUB, alpha=0.90, lw=0.6))

ax.set_xlabel("Residue number", labelpad=6)
ax.set_ylabel("RMSF (nm)", labelpad=6)
ax.set_title("RMSF per Residue — Bulk (CENTER) vs Near Interface (R1)",
             pad=10, fontsize=12, fontweight="bold")
ax.set_xlim(rc.min(), rc.max())
ax.set_ylim(0.0, 0.65)

# legend — upper right but anchored below the summary text box (~15% headroom)
ax.legend(loc="upper right", fontsize=9, framealpha=0.90, handlelength=1.8,
          bbox_to_anchor=(0.99, 0.78))

save(fig, "slide_fig3_rmsf.png")

# =============================================================================
# FIG 4 — SASA vs Orientation Scatter (all replicas)
# =============================================================================
print("Fig 4 — SASA vs orientation scatter...")

fig, ax = plt.subplots(figsize=(8.5, 7.5))
ax.set_facecolor(PLOT_BG)

# scatter per replica — small alpha to show density
for rep, col in REP_COL.items():
    d = gdata[rep]
    ax.scatter(d["angle"], d["sasa"], s=4, color=col, alpha=0.25,
               rasterized=True, zorder=2)

# reference lines
ax.axhline(P95, color=TEXT, lw=1.0, ls="--", alpha=0.65, zorder=3)
ax.axvline(30,  color=SUB,  lw=0.9, ls=":",  alpha=0.70, zorder=3)

# ── Stats box — top right (sparse data area above p95 and right of θ=120) ─────
stats = "Pearson r = +0.006\n95% CI: [−0.09, +0.11]\nNo coupling"
ax.text(0.98, 0.98, stats,
        transform=ax.transAxes, fontsize=10, fontweight="bold",
        color=GOLD, ha="right", va="top",
        bbox=dict(boxstyle="round,pad=0.45", fc="#0D1B2E", ec=GOLD, alpha=0.95, lw=1.2))

# ── Legend — UPPER LEFT (θ<30°, SASA>35 nm² region is nearly empty) ──────────
handles = [
    mpatches.Patch(color=REP_COL["CENTER"], label="CENTER"),
    mpatches.Patch(color=REP_COL["R1"],     label="R1"),
    mpatches.Patch(color=REP_COL["R2"],     label="R2"),
    mpatches.Patch(color=REP_COL["R3"],     label="R3"),
    plt.Line2D([0], [0], color=TEXT,  lw=1.2, ls="--", label=f"p95 = {P95:.1f} nm²"),
    plt.Line2D([0], [0], color=SUB,   lw=0.9, ls=":",  label="θ = 30° (old threshold)"),
]
ax.legend(handles=handles, loc="upper left", fontsize=8.5,
          framealpha=0.92, handlelength=2.0,
          bbox_to_anchor=(0.01, 0.85))

ax.set_xlabel("Calyx orientation θ (°)",    labelpad=6)
ax.set_ylabel("Calyx SASA (nm²)",           labelpad=6)
ax.set_xlim(0, 180)
ax.set_ylim(22, 39)

fig.tight_layout(pad=0.8)
save(fig, "slide_fig4_scatter.png")

print("\nAll done. 4 figures in slides/COMFHA_Talk_May2026/figures/")
