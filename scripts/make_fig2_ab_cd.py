"""
make_fig2_ab_cd.py
==================
Assemble publication-quality Fig 2 contact panels for JCIS submission.

Outputs two separate figures (as used in paper):
  PAPER_FIG2_CONTACT_AB.png  — panels (a) CENTER + (b) R1
  PAPER_FIG2_CONTACT_CD.png  — panels (c) R2   + (d) R3

Sources: pre-generated panel PNGs in results/figures/adsorption/
No trajectory required — pure PIL assembly.

Usage:
    source ~/research-env/bin/activate
    python3 scripts/make_fig2_ab_cd.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT    = Path(__file__).resolve().parent.parent
ADI_DIR = ROOT / "results" / "figures" / "adsorption"
OUT_DIR = ROOT / "results" / "figures"

DPI_META   = 300
TARGET_W   = 2126   # 180 mm @ 300 DPI — double-column JCIS width
LABEL_H    = 72
SEP_H      = 4
TITLE_CROP = 0      # no baked-in suptitle to remove (panels have no ax.set_title)

BG_LABEL  = (248, 249, 250)
SEP_COLOR = (200, 200, 205)
TEXT_COLOR = (25, 25, 25)

PANELS = [
    {
        "letter":   "a",
        "replica":  "SET 1A — bulk start",
        "duration": "1000 ns",
        "stats":    "12.5% contact  |  97 events  |  deepest −0.47 nm",
        "file":     ADI_DIR / "CENTER_1000ns_adsorption_contact.png",
    },
    {
        "letter":   "b",
        "replica":  "R1 — near-interface",
        "duration": "1000 ns",
        "stats":    "23.4% contact  |  215 events  |  deepest −0.71 nm",
        "file":     ADI_DIR / "R1_1000ns_full_adsorption_contact.png",
    },
    {
        "letter":   "c",
        "replica":  "R2 — near-interface",
        "duration": "1000 ns",
        "stats":    "7.1% contact  |  156 events  |  deepest −0.52 nm",
        "file":     ADI_DIR / "R2_1000ns_adsorption_contact.png",
    },
    {
        "letter":   "d",
        "replica":  "R3 — near-interface",
        "duration": "1000 ns",
        "stats":    "10.9% contact  |  145 events  |  deepest −0.38 nm",
        "file":     ADI_DIR / "R3_1000ns_adsorption_contact.png",
    },
]


def _font(size, bold=False):
    candidates = [
        # macOS (Arial — available in /System/Library/Fonts/Supplemental/)
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # Linux (Liberation / DejaVu)
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            pass
    return ImageFont.load_default()


def load_panel(path):
    img = Image.open(path).convert("RGB")
    img = img.crop((0, TITLE_CROP, img.width, img.height))  # remove baked-in suptitle
    if img.width != TARGET_W:
        h = int(img.height * TARGET_W / img.width)
        img = img.resize((TARGET_W, h), Image.LANCZOS)
    return img


def make_label_bar(panel):
    bar = Image.new("RGB", (TARGET_W, LABEL_H), BG_LABEL)
    draw = ImageDraw.Draw(bar)
    draw.text((14, 10),  f"({panel['letter']})", font=_font(32, bold=True),  fill=TEXT_COLOR)
    draw.text((78, 8),   f"{panel['replica']} — {panel['duration']}",
              font=_font(22, bold=True), fill=TEXT_COLOR)
    draw.text((78, 38),  panel["stats"], font=_font(18), fill=(80, 80, 90))
    return bar


def assemble(panel_defs, out_path):
    rows = []
    for p in panel_defs:
        print(f"  Loading ({p['letter']}) {p['file'].name}")
        bar   = make_label_bar(p)
        panel = load_panel(p["file"])
        sep   = Image.new("RGB", (TARGET_W, SEP_H), SEP_COLOR)
        rows.extend([bar, panel, sep])
    rows = rows[:-1]   # drop trailing separator

    total_h = sum(r.height for r in rows)
    canvas  = Image.new("RGB", (TARGET_W, total_h), (255, 255, 255))
    y = 0
    for r in rows:
        canvas.paste(r, (0, y))
        y += r.height

    canvas.save(str(out_path), dpi=(DPI_META, DPI_META))
    w_mm = canvas.size[0] / DPI_META * 25.4
    h_mm = canvas.size[1] / DPI_META * 25.4
    print(f"  -> {out_path.name}  {canvas.size[0]}x{canvas.size[1]}px  "
          f"({w_mm:.0f}x{h_mm:.0f} mm @ {DPI_META} DPI)")


def main():
    print("Fig 2 AB — CENTER + R1:")
    assemble(PANELS[:2], OUT_DIR / "PAPER_FIG2_CONTACT_AB.png")

    print("\nFig 2 CD — R2 + R3:")
    assemble(PANELS[2:], OUT_DIR / "PAPER_FIG2_CONTACT_CD.png")

    print("\nDone.")


if __name__ == "__main__":
    main()
