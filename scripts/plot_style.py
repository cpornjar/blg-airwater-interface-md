"""
plot_style.py
=============
Shared publication-quality style for all COMFHA analysis figures.
Target: JCIS (Elsevier) / Langmuir (ACS) — 300 DPI, Arial, no grid, clean axes.

Usage:
    from plot_style import apply_style, COLORS, col_width, double_width, savefig, savefig_pdf
    apply_style()
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── Column widths — JCIS (Elsevier) / ACS Langmuir (inches) ─────────────────
col_width    = 3.35   # single column  (JCIS: 8.5 cm; Langmuir: 3.25 in)
double_width = 6.85   # double column  (JCIS: 17.4 cm; Langmuir: 6.75 in)

# ── Color palette (consistent across all scripts) ────────────────────────────
COLORS = {
    "backbone"   : "#2166AC",   # blue
    "beta"       : "#1B7837",   # green
    "helix"      : "#D6604D",   # red-orange
    "patch"      : "#B35806",   # amber
    "total_sasa" : "#2166AC",
    "hydrophob"  : "#D6604D",
    "hydrophil"  : "#1B7837",
    "calyx"      : "#B35806",
    "z_protein"  : "#1B7837",
    "interface"  : "#2166AC",
    "distance"   : "#D6604D",
    "activation" : "#F4A582",   # light salmon for shaded activation windows
    "rg"         : "#B35806",
    "replica1"   : "#D6604D",
    "replica2"   : "#2166AC",
    "replica3"   : "#1B7837",
    "center"     : "#5E4FA2",   # purple for CENTER run
    "smoothed"   : None,        # use same color as raw, full opacity
}

# ── Known activation windows in CENTER run (ns) ──────────────────────────────
ACTIVATION_WINDOWS = [
    (250, 270),    # t ~ 259 ns spike
    (750, 790),    # t ~ 759-779 ns
    (930, 950),    # t ~ 940 ns (largest)
]

ADSORPTION_THRESHOLD_NM = 0.5   # definition used in paper


def apply_style():
    """Apply publication-quality rcParams. Call once at top of each script."""
    plt.rcParams.update({
        # Font
        "font.family"         : "sans-serif",
        "font.sans-serif"     : ["Arial", "Helvetica Neue", "DejaVu Sans"],
        "font.size"           : 8,
        "axes.labelsize"      : 9,
        "axes.titlesize"      : 9,
        "xtick.labelsize"     : 8,
        "ytick.labelsize"     : 8,
        "legend.fontsize"     : 7.5,
        "legend.framealpha"   : 0.85,
        "legend.edgecolor"    : "0.8",

        # Lines & axes
        "lines.linewidth"     : 1.2,
        "axes.linewidth"      : 0.8,
        "patch.linewidth"     : 0.6,

        # Ticks — inward, on all 4 sides (journal standard)
        "xtick.direction"     : "in",
        "ytick.direction"     : "in",
        "xtick.top"           : True,
        "ytick.right"         : True,
        "xtick.major.width"   : 0.8,
        "ytick.major.width"   : 0.8,
        "xtick.minor.width"   : 0.5,
        "ytick.minor.width"   : 0.5,
        "xtick.major.size"    : 3.5,
        "ytick.major.size"    : 3.5,
        "xtick.minor.size"    : 2.0,
        "ytick.minor.size"    : 2.0,
        "xtick.minor.visible" : True,
        "ytick.minor.visible" : True,

        # Resolution & saving
        "figure.dpi"          : 150,    # screen preview
        "savefig.dpi"         : 300,    # publication output
        "savefig.bbox"        : "tight",
        "savefig.pad_inches"  : 0.05,
        "figure.facecolor"    : "white",
        "axes.facecolor"      : "white",

        # Grid — off (JCIS / Elsevier standard: no grid in figures)
        "axes.grid"           : False,
    })


def add_activation_windows(ax, windows=None, alpha=0.15, label=True):
    """Shade known activation windows on a time-axis plot."""
    windows = windows or ACTIVATION_WINDOWS
    for i, (t0, t1) in enumerate(windows):
        ax.axvspan(t0, t1, alpha=alpha, color=COLORS["activation"],
                   label="Activation window" if (label and i == 0) else "")


def add_adsorption_line(ax, horizontal=True):
    """Draw the adsorption threshold line (0.5 nm)."""
    if horizontal:
        ax.axhline(ADSORPTION_THRESHOLD_NM, color="black",
                   lw=0.8, ls="--", alpha=0.6,
                   label=f"Adsorption threshold ({ADSORPTION_THRESHOLD_NM} nm)")
    else:
        ax.axvline(ADSORPTION_THRESHOLD_NM, color="black",
                   lw=0.8, ls="--", alpha=0.6,
                   label=f"Adsorption threshold ({ADSORPTION_THRESHOLD_NM} nm)")


def savefig(fig, path, close=True):
    """Save as PNG at 300 DPI and close."""
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.05)
    print(f"    Saved → {path}")
    if close:
        plt.close(fig)


def savefig_pdf(fig, path, close=True):
    """Save as PDF (vector) — preferred for JCIS LaTeX submission.

    For figures with rasterized elements (pcolormesh, imshow), matplotlib
    embeds those as high-DPI bitmaps inside the PDF automatically.
    Use this for Fig3, Fig4 where line art should be vector.
    """
    from pathlib import Path
    pdf_path = Path(str(path).replace(".png", ".pdf"))
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight", pad_inches=0.05)
    print(f"    Saved PDF → {pdf_path}")
    # Also save PNG at 300 DPI as fallback / preview
    png_path = Path(str(path).replace(".pdf", ".png"))
    fig.savefig(png_path, dpi=300, bbox_inches="tight", pad_inches=0.05)
    print(f"    Saved PNG → {png_path}")
    if close:
        plt.close(fig)


def smooth_sg(data, window=21, poly=3):
    """Savitzky-Golay smoothing — better edge preservation than rolling mean."""
    from scipy.signal import savgol_filter
    w = min(window, len(data))
    if w % 2 == 0:
        w -= 1
    if w < poly + 1:
        return data.copy()
    return savgol_filter(data, window_length=w, polyorder=poly)
