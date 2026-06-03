"""
make_slide_long_events.py
=========================
Dark ACADEMIC_NAVY table: The 6 Longest Contact Events (>=10 ns)
Data validated against verify_long_events.py (PBC-corrected).
"""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUT = Path('/Users/mac2022-1/Workspace/MILK_FROTHING/slides/COMFHA_Talk_May2026/figures/slide_long_events.png')
OUT.parent.mkdir(parents=True, exist_ok=True)

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = '#0D1B2E'
PLOT_BG = '#0A1628'
ROW_ALT = '#111F33'
HDR_BG  = '#1C3050'
TEXT    = '#E8EDF5'
SUB     = '#8FA5BC'
GOLD    = '#C9A84C'
TEAL    = '#4ECDC4'
RED_C   = '#E07070'
GREEN_C = '#5BAD8A'
RED_NO  = '#E74C3C'

# ── Verified data (from verify_long_events.py, PBC-corrected) ────────────────
EVENTS = [
    ('R1',     59.0,  29.8, 151, RED_C),
    ('R1',     57.5,  29.3,  39, RED_C),
    ('R1',     34.5,  30.0, 145, RED_C),
    ('R3',     21.8,  28.5,  56, GREEN_C),
    ('R1',     12.5,  29.7, 144, RED_C),
    ('CENTER', 10.5,  30.5, 139, GOLD),
]
HEADERS = ['Replica', 'Duration (ns)', 'Mean SASA (nm²)', 'Mean θ (°)', 'Committed?']
COL_W   = [0.14, 0.20, 0.24, 0.18, 0.18]   # relative widths, must sum to ~1

# ── Layout constants ──────────────────────────────────────────────────────────
FIG_W, FIG_H = 13, 6.2
TITLE_Y  = 0.93
HDR_Y    = 0.78
ROW_H    = 0.095
GAP      = 0.005
LEFT     = 0.06
COL_STARTS = []
x = LEFT
for w in COL_W:
    COL_STARTS.append(x)
    x += w * (1 - 2*LEFT)

STATS_Y  = 0.055

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor=BG)

# Title
fig.text(0.5, TITLE_Y,
         'The 6 Longest Contact Events (≥ 10 ns) — All End Without Commitment',
         ha='center', va='top', fontsize=14, fontweight='bold', color=TEXT,
         fontfamily='sans-serif')

def draw_row(y_top, cells, bg, text_colors=None, bold=False, fontsize=11):
    row_w = 1 - 2*LEFT
    fig.patches.append(mpatches.FancyBboxPatch(
        (LEFT, y_top - ROW_H), row_w, ROW_H - GAP,
        boxstyle='square,pad=0', transform=fig.transFigure,
        fc=bg, ec='none', zorder=1))
    for i, (cell_text, col_x) in enumerate(zip(cells, COL_STARTS)):
        col_w = COL_W[i] * row_w
        cx = col_x + col_w / 2
        cy = y_top - ROW_H / 2
        color = text_colors[i] if text_colors else TEXT
        fig.text(cx, cy, str(cell_text),
                 ha='center', va='center',
                 fontsize=fontsize, color=color,
                 fontweight='bold' if bold else 'normal',
                 fontfamily='sans-serif', zorder=2)

# Header row
draw_row(HDR_Y, HEADERS, HDR_BG,
         text_colors=[SUB]*5, bold=True, fontsize=10)

# Thin gold separator under header
fig.patches.append(mpatches.FancyBboxPatch(
    (LEFT, HDR_Y - ROW_H - 0.003), 1-2*LEFT, 0.003,
    boxstyle='square,pad=0', transform=fig.transFigure,
    fc=GOLD, ec='none', zorder=2))

# Data rows
for idx, (rep, dur, sasa, theta, rep_col) in enumerate(EVENTS):
    row_y = HDR_Y - ROW_H - 0.003 - idx * (ROW_H + GAP)
    bg = PLOT_BG if idx % 2 == 0 else ROW_ALT
    draw_row(row_y,
             [rep, f'{dur:.1f}', f'{sasa:.1f}', str(theta), 'NO'],
             bg,
             text_colors=[rep_col, TEXT, TEXT, TEXT, RED_NO],
             bold=False, fontsize=11)

# Stats bar
fig.text(0.5, STATS_Y,
         '6 events ≥ 10 ns   ·   Longest = 59 ns   ·   '
         'SASA non-activated (< 32.1 nm²)   ·   '
         'Orientation 39°–151°   ·   ZERO commitments',
         ha='center', va='bottom', fontsize=9.5, color=TEAL,
         fontfamily='sans-serif',
         bbox=dict(boxstyle='round,pad=0.4', fc='#091525', ec=TEAL, alpha=0.9, lw=0.8))

fig.savefig(OUT, dpi=200, bbox_inches='tight', facecolor=BG)
print(f'Saved -> {OUT.name}')
