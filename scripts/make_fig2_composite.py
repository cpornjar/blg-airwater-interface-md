"""
make_fig2_composite.py — publication-quality Fig 2 composite (Langmuir ACS style)
===================================================================================
Assemble the 4-panel Fig 2 contact-tracking composite from pre-generated
individual panel PNGs.

Panel layout (stacked rows, each = one replica):
  (a) CENTER — bulk start, 1000 ns
  (b) R1     — near-interface, 825.5 ns  (stride-5 extended trajectory)
  (c) R2     — near-interface, 1000 ns
  (d) R3     — near-interface, 1000 ns  [annotated: 21.8 ns gate-ABSENT event]

NOTE: regenerate R1 panel (b) from R1_825ns_s5_adsorption_contact.png.
      After R1 reaches 1000 ns, re-run detect_adsorption_contact.py for R1
      and update SOURCES["b"] to R1_1000ns_adsorption_contact.png.

Output: results/figures/PAPER_FIG2_CONTACT_4PANEL.png
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT    = Path(__file__).resolve().parent.parent
FIG_DIR = ROOT / "results" / "figures"
ADI_DIR = FIG_DIR / "adsorption"
OUT     = FIG_DIR / "PAPER_FIG2_CONTACT_4PANEL.png"

# ── Panel source files and label-bar text ─────────────────────────────────────
SOURCES = [
    {
        "letter":   "a",
        "replica":  "SET 1A — bulk start",
        "duration": "1000 ns",
        "stats":    "12.5% contact  |  97 events  |  deepest −0.47 nm",
        "note":     None,
        "file":     ADI_DIR / "CENTER_1000ns_adsorption_contact.png",
    },
    {
        "letter":   "b",
        "replica":  "R1 — near-interface",
        "duration": "1000 ns",
        "stats":    "23.4% contact  |  215 events  |  deepest −0.71 nm",
        "note":     None,
        "file":     ADI_DIR / "R1_1000ns_full_adsorption_contact.png",
    },
    {
        "letter":   "c",
        "replica":  "R2 — near-interface",
        "duration": "1000 ns",
        "stats":    "7.1% contact  |  156 events  |  deepest −0.50 nm",
        "note":     None,
        "file":     ADI_DIR / "R2_1000ns_adsorption_contact.png",
    },
    {
        "letter":   "d",
        "replica":  "R3 — near-interface",
        "duration": "1000 ns",
        "stats":    "10.9% contact  |  145 events  |  deepest −0.48 nm",
        "note":     "★  21.8 ns gate-ABSENT event (120–142 ns) — SASA activated, calyx misaligned",
        "file":     ADI_DIR / "R3_1000ns_adsorption_contact.png",
    },
]

# ── Layout constants ──────────────────────────────────────────────────────────
TARGET_W   = 2126          # 180 mm @ 300 dpi (Langmuir double-column)
LABEL_H    = 72            # label bar height (px)
SEP_H      = 4             # separator height (px)
TITLE_CROP = 50            # px to crop from top of each source PNG (removes matplotlib suptitle)

# Colors
BG_LABEL   = (248, 249, 250)
BG_NOTE    = (253, 246, 246)   # warm tint for R3 note
SEP_COLOR  = (200, 200, 205)
TEXT_COLOR = (25, 25, 25)
NOTE_COLOR = (160, 30, 30)
DPI_META   = 300


def _font(size, bold=False):
    candidates_bold = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates = [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in (candidates_bold if bold else candidates):
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            pass
    return ImageFont.load_default()


def load_panel(path):
    img = Image.open(path).convert("RGB")
    img = img.crop((0, TITLE_CROP, img.width, img.height))
    if img.width != TARGET_W:
        h = int(img.height * TARGET_W / img.width)
        img = img.resize((TARGET_W, h), Image.LANCZOS)
    return img


def make_label_bar(panel):
    has_note = panel["note"] is not None
    bar_h = LABEL_H + (30 if has_note else 0)
    bar   = Image.new("RGB", (TARGET_W, bar_h), BG_LABEL)
    draw  = ImageDraw.Draw(bar)

    f_letter  = _font(32, bold=True)
    f_replica = _font(22, bold=True)
    f_stats   = _font(18)
    f_note    = _font(17)

    # panel letter
    draw.text((14, 10), f"({panel['letter']})", font=f_letter, fill=TEXT_COLOR)

    # replica name + duration on one line
    draw.text((78, 8),
              f"{panel['replica']} — {panel['duration']}",
              font=f_replica, fill=TEXT_COLOR)

    # stats below
    draw.text((78, 38), panel["stats"], font=f_stats, fill=(80, 80, 90))

    # optional note (R3 gate-absent annotation)
    if has_note:
        note_y = LABEL_H + 4
        draw.rectangle([(0, LABEL_H), (TARGET_W, bar_h)], fill=BG_NOTE)
        draw.text((14, note_y), panel["note"], font=f_note, fill=NOTE_COLOR)

    return bar


def add_gate_annotation(panel_img):
    """Overlay a translucent bracket on R3 marking the 21.8 ns gate-absent event."""
    img  = panel_img.copy()
    draw = ImageDraw.Draw(img, "RGBA")
    W, H = img.size

    # empirical axis margins from detect_adsorption_contact.py output (1000 ns x-axis)
    x_left_frac  = 0.093
    x_right_frac = 0.955
    y_bot_frac   = 0.48   # top of lower sub-panel
    y_top_frac   = 0.96   # bottom of lower sub-panel

    t_start, t_end, t_max = 120.6, 142.4, 1000.0

    x0 = int(W * (x_left_frac + (t_start / t_max) * (x_right_frac - x_left_frac)))
    x1 = int(W * (x_left_frac + (t_end   / t_max) * (x_right_frac - x_left_frac)))
    y0 = int(H * y_bot_frac)
    y1 = int(H * y_top_frac)

    draw.rectangle([x0, y0, x1, y1], fill=(200, 30, 30, 45))
    for lw in range(2):
        draw.rectangle([x0+lw, y0+lw, x1-lw, y1-lw],
                       outline=(160, 20, 20, 200))

    f = _font(16, bold=True)
    label = "21.8 ns\ngate-absent"
    try:
        bbox = draw.textbbox((0, 0), label, font=f)
        tw = bbox[2] - bbox[0]
    except AttributeError:
        tw = 70
    tx = max(x0, min(x0 - tw // 2 + (x1 - x0) // 2, W - tw - 4))
    ty = max(y0 - 44, 4)
    draw.text((tx + 1, ty + 1), label, font=f, fill=(255, 255, 255, 180))
    draw.text((tx, ty), label, font=f, fill=(140, 20, 20, 220))

    return img.convert("RGB")


def main():
    panels = []
    for p in SOURCES:
        print(f"  Loading ({p['letter']}) {p['file'].name}")
        panel_img = load_panel(p["file"])

        if p["letter"] == "d":
            panel_img = add_gate_annotation(panel_img)

        bar = make_label_bar(p)
        sep = Image.new("RGB", (TARGET_W, SEP_H), SEP_COLOR)
        panels.extend([bar, panel_img, sep])

    panels = panels[:-1]   # drop trailing separator

    total_h = sum(img.height for img in panels)
    canvas  = Image.new("RGB", (TARGET_W, total_h), (255, 255, 255))
    y = 0
    for img in panels:
        canvas.paste(img, (0, y))
        y += img.height

    canvas.save(str(OUT), dpi=(DPI_META, DPI_META))
    print(f"\n✓ Saved → {OUT}")
    print(f"  {canvas.size[0]}×{canvas.size[1]} px  "
          f"({canvas.size[0]/DPI_META*25.4:.0f}×{canvas.size[1]/DPI_META*25.4:.0f} mm @ {DPI_META} dpi)")


if __name__ == "__main__":
    main()
