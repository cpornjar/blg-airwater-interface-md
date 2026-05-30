"""
render_slides_pdf.py — render all 20 slides as a multi-page PDF
================================================================
Uses matplotlib only. No browser required. Output is a proper
vector/raster PDF that can be:
  - Presented directly in Preview (fullscreen)
  - Imported into Keynote: Insert → Choose → [select pages individually]
  - Opened in any PDF viewer

Usage:  python3 slides/render_slides_pdf.py
Output: slides/slides.pdf  (20 pages, 16:9, navy academic theme)
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
from pathlib import Path
import textwrap
import numpy as np

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
FIGS = ROOT / "figures"
OUT  = ROOT / "slides.pdf"

# ── Theme ──────────────────────────────────────────────────────────────────────
NAVY  = "#1A2744"
GOLD  = "#C9A84C"
BLUE  = "#4472C4"
WHITE = "#FFFFFF"
LGRAY = "#E2E8F0"
GRAY  = "#9CA3AF"
BGBLUE= "#EEF2FF"

W, H = 13.333, 7.5   # inches, 16:9

plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["DejaVu Sans", "Arial", "Helvetica"],
    "figure.facecolor": WHITE,
    "axes.facecolor":   WHITE,
    "savefig.facecolor": WHITE,
})


# ── Layout helpers ─────────────────────────────────────────────────────────────

def new_slide():
    fig = plt.figure(figsize=(W, H), facecolor=WHITE)
    return fig


def title_bar(fig, title_text, bar_frac=0.13):
    """Navy title bar across full width."""
    ax_bar = fig.add_axes([0, 1 - bar_frac, 1, bar_frac])
    ax_bar.set_facecolor(NAVY)
    ax_bar.set_xlim(0, 1); ax_bar.set_ylim(0, 1)
    ax_bar.axis("off")
    # Gold accent line at bottom of bar
    ax_bar.axhline(0, color=GOLD, linewidth=4, xmin=0, xmax=1)
    ax_bar.text(0.035, 0.5, title_text,
                color=WHITE, fontsize=22, fontweight="bold",
                va="center", ha="left", transform=ax_bar.transAxes)
    return ax_bar


def body_ax(fig, top_frac=0.87, bottom_frac=0.05):
    ax = fig.add_axes([0.04, bottom_frac, 0.92, top_frac - bottom_frac])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    return ax


def bullet_list(ax, items, y_start=0.92, line_h=0.12, fontsize=16):
    y = y_start
    for item in items:
        if item.get("spacer"):
            y -= line_h * 0.5
            continue
        text  = item.get("text", "")
        bold  = item.get("bold", False)
        color = item.get("color", NAVY)
        level = item.get("level", 0)
        size  = item.get("size", fontsize)
        indent = 0.025 + level * 0.03
        weight = "bold" if bold else "normal"
        # bullet marker (skip for bold section headers)
        if not bold and text:
            marker_color = item.get("marker_color", GOLD)
            ax.text(indent, y, "•", color=marker_color,
                    fontsize=size - 1, va="top", ha="left",
                    transform=ax.transAxes)
        ax.text(indent + (0.02 if not bold else 0), y, text,
                color=color, fontsize=size, fontweight=weight,
                va="top", ha="left", transform=ax.transAxes,
                wrap=False)
        y -= line_h
    return y


def highlight_box(ax, text, y, h=0.12, fontsize=15):
    rect = mpatches.FancyBboxPatch(
        (0.01, y - h), 0.98, h,
        boxstyle="round,pad=0.01",
        linewidth=2, edgecolor=GOLD,
        facecolor=BGBLUE,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(rect)
    ax.text(0.5, y - h / 2, text, color=NAVY, fontsize=fontsize,
            fontweight="bold", va="center", ha="center",
            transform=ax.transAxes)


def embed_figure(fig, img_path, rect=(0.03, 0.07, 0.94, 0.72)):
    """Embed a PNG/PDF image in the slide body area."""
    if not img_path.exists():
        return
    try:
        img = mpimg.imread(str(img_path))
    except Exception:
        return
    ax_img = fig.add_axes(rect)
    ax_img.imshow(img, aspect="equal")
    ax_img.axis("off")


def caption_text(fig, text, y=0.055):
    ax_cap = fig.add_axes([0.04, 0.01, 0.92, 0.07])
    ax_cap.set_xlim(0, 1); ax_cap.set_ylim(0, 1)
    ax_cap.axis("off")
    ax_cap.text(0.5, 0.5, text, color=GRAY, fontsize=11,
                style="italic", va="center", ha="center",
                transform=ax_cap.transAxes, wrap=False)


def slide_number(fig, n, total=20):
    ax_n = fig.add_axes([0.94, 0, 0.06, 0.04])
    ax_n.set_xlim(0, 1); ax_n.set_ylim(0, 1); ax_n.axis("off")
    ax_n.text(0.9, 0.5, f"{n}/{total}", color=GRAY, fontsize=10,
              va="center", ha="right")


# ── Slides ─────────────────────────────────────────────────────────────────────

with PdfPages(str(OUT)) as pdf:

    # ── 1: Title ────────────────────────────────────────────────────────────────
    fig = new_slide()
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0.06, 0.08, 0.88, 0.84])
    ax.set_facecolor(NAVY); ax.axis("off")
    # Gold line
    ax.axhline(0.55, color=GOLD, linewidth=3, xmin=0, xmax=1)
    ax.text(0, 0.92, "Contact without Commitment",
            color=WHITE, fontsize=36, fontweight="bold",
            va="top", ha="left", transform=ax.transAxes)
    ax.text(0, 0.68,
            "Atomistic Characterisation of β-Lactoglobulin\n"
            "Adsorption Dynamics at the Air–Water Interface",
            color="#CBD5E1", fontsize=20,
            va="top", ha="left", transform=ax.transAxes, linespacing=1.4)
    ax.text(0, 0.44, "Chalakon Pornjariyawatch · Prapasiri Pongprayoon",
            color=WHITE, fontsize=17, fontweight="bold",
            va="top", ha="left", transform=ax.transAxes)
    ax.text(0, 0.33, "COMFHA — Computational Modelling in Food, Health and Agriculture",
            color="#94A3B8", fontsize=14,
            va="top", ha="left", transform=ax.transAxes)
    ax.text(0, 0.23, "Kasetsart University · Lab Group Seminar · May 2026",
            color="#94A3B8", fontsize=14,
            va="top", ha="left", transform=ax.transAxes)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 2: Today's Story ────────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Today's Story")
    ax = body_ax(fig)
    items = [
        {"text": "THE PROBLEM", "bold": True, "color": GOLD},
        {"text": "BLG is the key foam stabiliser in milk — how does it recognise the interface?"},
        {"text": "Kinetic energy barrier measured for decades; mechanism unknown at atomic scale"},
        {"spacer": True},
        {"text": "OUR APPROACH", "bold": True, "color": GOLD},
        {"text": "First unbiased atomistic MD of native BLG at the air–water interface — 4.00 µs"},
        {"spacer": True},
        {"text": "KEY FINDINGS", "bold": True, "color": GOLD},
        {"text": "Contact frequent (613 events); commitment absent (0 of 613)"},
        {"text": "Calyx mobile; Loop CD/EF interface-induced; SASA ⊥ orientation"},
    ]
    bullet_list(ax, items, y_start=0.92, line_h=0.10)
    highlight_box(ax, "Four acts:  Problem  →  Approach  →  Findings  →  Implications",
                  y=0.13, h=0.10)
    slide_number(fig, 2)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 3: Why Milk Foam? ───────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Why Milk Foam?")
    ax = body_ax(fig)
    items = [
        {"text": "β-Lactoglobulin (BLG): dominant whey protein in bovine milk (~ 3 g/L)"},
        {"text": "Principal stabiliser of milk foam — forms viscoelastic film at the AWI"},
        {"spacer": True},
        {"text": "Adsorption is slow: seconds to minutes from bulk solution"},
        {"text": "A kinetic energy barrier distinguishes BLG from more flexible proteins"},
        {"text": "Classical model (Graham & Phillips 1979): surface tension → global unfolding",
         "color": GRAY},
        {"text": "→ Assumed but never directly observed at atomic resolution",
         "color": BLUE, "level": 1},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.11)
    highlight_box(ax,
        "Central question: how does a folded, water-soluble protein recognise and populate the AWI?",
        y=0.13, h=0.10)
    slide_number(fig, 3)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 4: The Atomistic Gap ────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "The Atomistic Gap")
    ax = body_ax(fig)
    items = [
        {"text": "Experiments (tensiometry, ellipsometry, neutron reflectometry):",
         "bold": True, "color": NAVY},
        {"text": "→ Time-averaged surface properties. No individual molecular events.",
         "color": GRAY, "level": 1},
        {"spacer": True},
        {"text": "Prior MD studies of BLG at interfaces:", "bold": True, "color": NAVY},
        {"text": "→ Oil-water only (not AWI)", "level": 1},
        {"text": "→ Pre-positioned near interface — not starting from bulk", "level": 1},
        {"text": "→ ≤ 100 ns — far below seconds-to-minutes adsorption timescale", "level": 1},
        {"spacer": True},
        {"text": "This work: first unbiased atomistic simulation of native BLG at AWI",
         "bold": True, "color": GOLD},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.10)
    slide_number(fig, 4)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 5: System ───────────────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "System: 12×12×35 nm Slab — 4.00 µs Cumulative")
    embed_figure(fig, FIGS / "PAPER_FIG2_CONTACT_AB.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "SET 1A: CENTER bulk-start (1000 ns)  ·  SET 1B: R1, R2, R3 near-interface (1000 ns each)  ·  CHARMM36m + TIP3P")
    slide_number(fig, 5)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 6: Contact Metric ───────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Contact Metric: Why Nearest-Atom Distance")
    ax = body_ax(fig)
    items = [
        {"text": "BLG monomer is ~ 4 nm in diameter"},
        {"text": "Centre-of-mass stays 2–3 nm from interface even while touching it",
         "color": GRAY},
        {"text": "→ CoM distance is BLIND to actual surface contact",
         "bold": True, "color": "#DC2626"},
        {"spacer": True},
        {"text": "Nearest-atom ≤ 0.3 nm: detects real surface touch",
         "bold": True, "color": GOLD},
        {"text": "→ Recovers 613 contact events vs. ~ 0 with CoM threshold"},
        {"spacer": True},
        {"text": "Penetration depth resolved to 0.01 nm precision"},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.11)
    highlight_box(ax,
        "Switching to nearest-atom distance reveals that BLG visits the interface constantly",
        y=0.13, h=0.10)
    slide_number(fig, 6)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 7: Contact Frequent ─────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Contact is Frequent — CENTER + R1")
    embed_figure(fig, FIGS / "PAPER_FIG2_CONTACT_AB.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "CENTER: 97 events (12.5% of frames)  ·  R1: 215 events (23.4%)  ·  Penetration up to 0.71 nm past interface")
    slide_number(fig, 7)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 8: Commitment Rare ──────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Commitment is Rare — R2 + R3")
    embed_figure(fig, FIGS / "PAPER_FIG2_CONTACT_CD.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "R2: 156 events  ·  R3: 145 events  ·  Total 613 events — only 6 sustain ≥ 10 ns  ·  None commits")
    slide_number(fig, 8)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 9: Long-Event Table ─────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "The 6 Long-Residency Events: All Non-Activated")
    ax = body_ax(fig, top_frac=0.84, bottom_frac=0.07)
    # Draw table
    rows = [
        ("CENTER",  "~10 ns",  "28.8 nm²",  "~52°",  "No"),
        ("R1",      "59 ns",   "29.1 nm²",  "~63°",  "No"),
        ("R1",      "~12 ns",  "28.5 nm²",  "~68°",  "No"),
        ("R1",      "~11 ns",  "30.5 nm²",  "~44°",  "No"),
        ("R1",      "~10 ns",  "28.9 nm²",  "~75°",  "No"),
        ("R3",      "~10 ns",  "30.1 nm²",  "~56°",  "No"),
    ]
    headers = ["Replica", "Duration", "Event-mean SASA", "Angle", "Committed?"]
    col_x   = [0.03, 0.19, 0.35, 0.59, 0.73]
    col_w   = [0.16, 0.16, 0.24, 0.14, 0.25]
    row_h   = 0.105
    y0      = 0.88
    # Header
    for ci, (hdr, cx, cw) in enumerate(zip(headers, col_x, col_w)):
        rect = mpatches.FancyBboxPatch((cx, y0 - row_h), cw - 0.005, row_h,
            boxstyle="square,pad=0", facecolor=NAVY, edgecolor=WHITE, lw=0.5,
            transform=ax.transAxes, clip_on=False)
        ax.add_patch(rect)
        ax.text(cx + cw/2 - 0.0025, y0 - row_h/2, hdr,
                color=WHITE, fontsize=13, fontweight="bold",
                va="center", ha="center", transform=ax.transAxes)
    # Data rows
    for ri, row in enumerate(rows):
        y_row = y0 - row_h * (ri + 2)
        bg = BGBLUE if ri % 2 == 0 else WHITE
        for ci, (cell, cx, cw) in enumerate(zip(row, col_x, col_w)):
            rect = mpatches.FancyBboxPatch((cx, y_row), cw - 0.005, row_h,
                boxstyle="square,pad=0", facecolor=bg, edgecolor=LGRAY, lw=0.5,
                transform=ax.transAxes, clip_on=False)
            ax.add_patch(rect)
            is_highlight = (ri == 1 and ci == 1)  # 59 ns
            color = GOLD if is_highlight else NAVY
            weight = "bold" if is_highlight else "normal"
            ax.text(cx + cw/2 - 0.0025, y_row + row_h/2, cell,
                    color=color, fontsize=13, fontweight=weight,
                    va="center", ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.04,
        "All 6 events: SASA 28.5–30.5 nm²  ·  zero activation-criterion frames in every event\n"
        "The protein sustains 59 ns of contact — still doesn't commit",
        color=BLUE, fontsize=13, style="italic",
        va="center", ha="center", transform=ax.transAxes)
    slide_number(fig, 9)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 10: Global Compactness ──────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Global Fold Preserved — Never Unfolds in 4 µs")
    embed_figure(fig, FIGS / "PAPER_FIG3_ACTIVATION.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "Rg = 1.496 ± 0.009 nm (R1) — no trend  ·  β-barrel RMSD 0.21–0.24 nm  ·  α-helix RMSD ≤ 0.137 nm")
    slide_number(fig, 10)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 11: Calyx Breathes ──────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Calyx Breathes — Stationary Stochastic Process")
    embed_figure(fig, FIGS / "PAPER_FIG3_ACTIVATION.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "SASA: 24–37 nm² (PBC-corrected)  ·  Recurring fluctuations ~30–40 ns  ·  Not a one-shot event")
    slide_number(fig, 11)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 12: RMSF Loop Shift ─────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Interface Shifts Which Loop Dominates")
    embed_figure(fig, FIGS / "PAPER_FIG3_ACTIVATION.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "Bulk (CENTER): Loop BC dominant, RMSF 0.54 nm  ·  Near-AWI (R1): Loop CD/EF rises to 0.39 nm")
    slide_number(fig, 12)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 13: SASA Distribution ───────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "SASA Distribution: All Four Replicas")
    embed_figure(fig, FIGS / "Fig4_optionA.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "All replicas: SASA 24–37 nm²  ·  p95 = 32.1 nm² (distribution-based)  ·  No distinct activated regime")
    slide_number(fig, 13)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 14: Orientation Independent ────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Orientation: Uniform and Independent of SASA")
    embed_figure(fig, FIGS / "Fig4_optionA.png",
                 rect=(0.01, 0.10, 0.98, 0.74))
    caption_text(fig,
        "Pearson r = +0.006  ·  No quadrant clustering  ·  Obs/Indep ≈ 1.0 across threshold sweep (27–33 nm²)")
    slide_number(fig, 14)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 15: Block Bootstrap ─────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Statistical Robustness: Block Bootstrap")
    ax = body_ax(fig)
    items = [
        {"text": "Challenge: SASA autocorrelation = 232 ns", "bold": True},
        {"text": "→ i.i.d. assumption breaks down for standard CIs", "color": GRAY, "level": 1},
        {"spacer": True},
        {"text": "Block bootstrap approach:", "bold": True, "color": NAVY},
        {"text": "→ Autocorrelation: 81–394 ns per replica", "level": 1},
        {"text": "→ Block length: 232 ns (conservative)", "level": 1},
        {"text": "→ Effective N ≈ 17 independent observations across 4 µs",
         "level": 1, "bold": True},
        {"spacer": True},
        {"text": "Block bootstrap 95% CI: [−0.09, +0.11]",
         "bold": True, "color": GOLD},
        {"text": "→ Rules out |r| > 0.11 at 95% confidence",
         "bold": True, "color": GOLD},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.10)
    highlight_box(ax,
        "SASA and calyx orientation are statistically independent on the µs timescale",
        y=0.13, h=0.10)
    slide_number(fig, 15)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 16: PBC Lesson ─────────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Scientific Integrity: The PBC Lesson")
    ax = body_ax(fig)
    items = [
        {"text": "During analysis we found a periodic-boundary artefact:",
         "bold": True, "color": NAVY},
        {"text": "freeSASA without MDAnalysis unwrap → atoms split across PBC boundaries",
         "color": GRAY},
        {"spacer": True},
        {"text": "Before fix:  SASA 45–62 nm²  ·  21 gate-open events",
         "bold": True, "color": "#DC2626"},
        {"text": "After  fix:  SASA 24–37 nm²  ·  0 gate-open events",
         "bold": True, "color": "#16A34A"},
        {"spacer": True},
        {"text": "Fix: mda_unwrap transformation in MDAnalysis — applied to all 8006 gate frames"},
        {"text": "Full disclosure in Methods section of the paper"},
        {"spacer": True},
        {"text": "All results in this talk use PBC-corrected data", "bold": True},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.10)
    slide_number(fig, 16)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 17: What This Means ─────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "What This Means")
    ax = body_ax(fig)
    items = [
        {"text": "Prior models assumed:", "bold": True, "color": NAVY},
        {"text": "Contact → global unfolding → adsorption (Graham & Phillips)",
         "color": GRAY, "level": 1},
        {"text": "OR: brief contacts don't matter", "color": GRAY, "level": 1},
        {"spacer": True},
        {"text": "What we observe:", "bold": True, "color": NAVY},
        {"text": "59 ns contact without commitment → genuine kinetic bottleneck"},
        {"text": "r = +0.006 → no simple two-factor coupling as commitment trigger"},
        {"text": "Global fold preserved → commitment is not global unfolding"},
        {"spacer": True},
        {"text": "First characterisation of the pre-commitment contact ensemble",
         "bold": True, "color": GOLD},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.10)
    highlight_box(ax,
        "Required foundation for designing enhanced-sampling calculations",
        y=0.13, h=0.10)
    slide_number(fig, 17)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 18: Implications ────────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "Implications for Protein Engineering")
    ax = body_ax(fig)
    items = [
        {"text": "Loop CD/EF: the engineering target", "bold": True, "color": GOLD},
        {"text": "Becomes dominant near AWI — interface-induced conformational preference",
         "level": 1},
        {"text": "Calyx flexibility mutations likely more effective than bulk hydrophobicity",
         "level": 1},
        {"spacer": True},
        {"text": "Dimer complexity (BLG dominant dimer above ~50 µM):",
         "bold": True, "color": NAVY},
        {"text": "Steric: dimer interface occludes Loop CD/EF region", "level": 1},
        {"text": "Kinetic: dimer must dissociate before calyx presents unobstructed", "level": 1},
        {"text": "Orientational: oblate shape alters rotational diffusion and θ distribution",
         "level": 1},
        {"spacer": True},
        {"text": "Lipocalin family: quantitative SASA/orientation baseline for mutant comparison"},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.10)
    slide_number(fig, 18)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 19: What's Next ─────────────────────────────────────────────────────────
    fig = new_slide()
    title_bar(fig, "What's Next")
    ax = body_ax(fig)
    items = [
        {"text": "Paper 1 (this work) — submission pipeline", "bold": True, "color": GOLD},
        {"text": "Zenodo upload → DOI → JCIS submission (IF ~9)", "level": 1},
        {"spacer": True},
        {"text": "Enhanced sampling — the clear next step", "bold": True, "color": NAVY},
        {"text": "Metadynamics / umbrella sampling along (SASA, θ)", "level": 1},
        {"text": "SET 1D data available as baseline starting conformations", "level": 1},
        {"spacer": True},
        {"text": "Paper 2 — β-Casein at AWI", "bold": True, "color": NAVY},
        {"text": "AlphaFold2 structure ready; comparison with BLG ensemble", "level": 1},
        {"spacer": True},
        {"text": "BLG dimer + TIP4P/2005 cross-check", "level": 1},
    ]
    bullet_list(ax, items, y_start=0.90, line_h=0.10)
    slide_number(fig, 19)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

    # ── 20: Summary ─────────────────────────────────────────────────────────────
    fig = new_slide()
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0.06, 0.06, 0.88, 0.88])
    ax.set_facecolor(NAVY); ax.axis("off")
    ax.text(0.0, 0.98, "Summary", color=WHITE, fontsize=30, fontweight="bold",
            va="top", ha="left", transform=ax.transAxes)
    ax.axhline(0.90, color=GOLD, linewidth=2.5, xmin=0, xmax=1)
    pts = [
        ("1. Contact without commitment",
         "613 events across 4 µs — only 6 sustain ≥ 10 ns, none commits to adsorption"),
        ("2. Compact globally, loop-mediated locally",
         "Rg stable; β-barrel intact; Loop CD/EF mediates calyx exposure near AWI"),
        ("3. SASA ⊥ orientation on the µs timescale",
         "r = +0.006, CI [−0.09, +0.11] — rules out |r| > 0.11 coupling"),
    ]
    y = 0.84
    for label, body in pts:
        ax.text(0.0, y, label, color=GOLD, fontsize=16, fontweight="bold",
                va="top", ha="left", transform=ax.transAxes)
        ax.text(0.0, y - 0.07, body, color=WHITE, fontsize=15,
                va="top", ha="left", transform=ax.transAxes)
        y -= 0.22
    ax.axhline(0.14, color=GOLD, linewidth=1.5, xmin=0, xmax=1)
    ax.text(0.5, 0.08,
        "4 µs of unbiased MD resolves the pre-commitment contact ensemble.\n"
        "Commitment requires enhanced sampling to characterise.   |   Thank you — questions?",
        color="#CBD5E1", fontsize=14, style="italic",
        va="center", ha="center", transform=ax.transAxes, linespacing=1.5)
    slide_number(fig, 20)
    pdf.savefig(fig, bbox_inches="tight", dpi=150); plt.close()

print(f"Saved: {OUT}  ({OUT.stat().st_size // 1024} KB)  —  20 slides")
print()
print("Options:")
print("  • Present directly: open slides.pdf in Preview → View → Enter Full Screen → arrow keys")
print("  • Import into Keynote: drag slides.pdf into a Keynote presentation")
print("  • Browser slides: open slides.html in Safari/Chrome")
