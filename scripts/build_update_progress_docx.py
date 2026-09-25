"""
One-off script: build the editable .docx version of the short
"Update Progress 11 September 2026" report (BLG + CASEIN results only,
VMD figure + SASA bar chart, no executive summary / questions section).
Mirrors progress-reports/update_progress_2026-09-11.tex. Not part of the
regular analysis pipeline -- run once, keep for reference.
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = Path("/Users/mac2022-1/Workspace/MILK_FROTHING")
FIG_RENDER = ROOT / "results/figures/render"
FIG_PAPER = ROOT / "results/figures/paper"
OUT = ROOT / "progress-reports/update_progress_2026-09-11.docx"

doc = Document()

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)

for sec in doc.sections:
    sec.top_margin = Cm(2)
    sec.bottom_margin = Cm(2)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)


def h(text, level=1):
    doc.add_heading(text, level=level)


def para(text, bold=False, italic=False, size=11):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(size)
    return p


def add_table(headers, rows, caption):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, htext in enumerate(headers):
        hdr[i].text = htext
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(10)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            for p in cells[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(10)
    cap = doc.add_paragraph()
    cr = cap.add_run(caption)
    cr.italic = True
    cr.font.size = Pt(10)
    doc.add_paragraph()


def add_image_row(paths_captions, width_cm=7.5):
    table = doc.add_table(rows=2, cols=len(paths_captions))
    table.autofit = True
    for i, (path, cap) in enumerate(paths_captions):
        cell = table.rows[0].cells[i]
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(path), width=Cm(width_cm))
        cap_cell = table.rows[1].cells[i]
        cp = cap_cell.paragraphs[0]
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cp.add_run(cap)
        cr.italic = True
        cr.font.size = Pt(10)
    doc.add_paragraph()


# ============================================================
# Header
# ============================================================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("Update Progress 11 September 2026")
tr.bold = True
tr.font.size = Pt(20)
doc.add_paragraph()

# ============================================================
# Figure 1 - VMD renders (lead figure)
# ============================================================
add_image_row([
    (FIG_RENDER / "blg_calyx_crop.png", "(a) BLG: compact fold, calyx patch (orange)"),
    (FIG_RENDER / "cas_patch_crop.png", "(b) CASEIN: extended chain, N-term (orange)"),
], width_cm=7.5)
para(
    "Figure 1: Structural contrast between the two proteins (VMD renders): BLG's "
    "compact, mostly-buried calyx vs. CASEIN's extended, disordered chain with its "
    "N-terminal region already surface-exposed even in the starting structure.",
    italic=True, size=10,
)
doc.add_paragraph()

# ============================================================
# Section 1 - BLG
# ============================================================
h("1. BLG Results", level=1)

para(
    "Headline numbers (unchanged, PBC-corrected, computed across all 4 replicas): "
    "613 total contact events (97 in CENTER, 516 near-interface across replicas); "
    "6 long contact events (≥10 ns); calyx SASA range 24–37 nm² (mean 28.95 nm²); "
    "Pearson correlation between SASA and orientation angle r = +0.006 (block-bootstrap "
    "95% CI [−0.09, +0.11]) – no coupling detected within these limits. These support the "
    "paper's current framing: BLG's calyx remains accessible throughout, but the protein "
    "does not commit to a bound, reoriented state within the simulated timescale."
)

add_table(
    headers=["Replica", "Rg (nm)*", "RMSD bb (nm)", "RMSD patch (nm)",
             "Calyx SASA (nm²)", "γ (mN/m)*"],
    rows=[
        ["CENTER (1000 ns)", "1.504 ± 0.022", "0.229", "0.198", "3.81 ± 0.46", "51.9 ± 38.5"],
        ["R1", "1.497 ± 0.009", "0.237", "0.347", "3.15 ± 0.34", "52.7 ± 38.7"],
        ["R2", "1.493 ± 0.008", "0.206", "0.254", "3.59 ± 0.32", "52.0 ± 39.0"],
        ["R3", "1.499 ± 0.012", "0.268", "0.276", "3.36 ± 0.48", "52.6 ± 39.4"],
    ],
    caption=(
        "Table 1: BLG per-replica structural summary. *For R1/R2/R3, only Rg and γ "
        "(surface tension) currently reflect the first 500 of 1000 ns each replica "
        "actually ran – a fix to include the remaining trajectory segments for these "
        "two analyses is in progress. RMSD and calyx SASA for R1/R2/R3 already cover "
        "the full 1000 ns (their analysis scripts already include the extension "
        "trajectory segments)."
    ),
)

add_image_row([
    (FIG_PAPER / "PAPER_COMPARATIVE_RMSD.png", ""),
], width_cm=10)
para(
    "Figure 2: BLG RMSD by region, all 4 replicas: whole-backbone (solid) vs. calyx "
    "patch (hatched). R1's patch RMSD is visibly elevated relative to the other "
    "replicas – traced to a long (≥10 ns) contact event unique to R1, not a bug.",
    italic=True, size=10,
)

add_image_row([
    (FIG_PAPER / "PAPER_TIMESERIES_RMSD.png", ""),
], width_cm=14)
para(
    "Figure 2b: BLG RMSD vs. time, all 4 replicas (backbone and calyx patch). The "
    "trend view: R1's patch RMSD (orange, panel b) visibly steps up around 350 ns "
    "and never returns to baseline – the moment of its long contact event – while "
    "CENTER's patch RMSD (purple) stays lowest and flattest throughout.",
    italic=True, size=10,
)

para(
    "Secondary structure content (DSSP) is stable across all 4 replicas: Helix "
    "10.5–12.4%, Sheet 36.0–36.8%, Coil 50.8–52.9%. Hydrogen-bonding (CENTER only so "
    "far): protein-protein 107.3 ± 5.6, protein-water 393.2 ± 13.2, interface "
    "water-water 9539.6 ± 328.4 (mean counts per frame)."
)

# ============================================================
# Section 2 - CASEIN
# ============================================================
h("2. CASEIN (β-casein) Results", level=1)

para(
    "First comparative result with real replication (n=2): N-terminal region "
    "(residues 1–25) solvent accessibility – the CASEIN analogue of BLG's calyx SASA "
    "– is 24.77 ± 1.40 nm² in R1 vs. 25.41 ± 1.97 nm² in CENTER. The two independent "
    "1000 ns runs agree closely, which is good evidence this is a real, reproducible "
    "property of the protein rather than an artifact of one starting structure."
)

add_table(
    headers=["Replica", "N-term SASA (nm²)", "Contact", "γ (mN/m)",
             "Hbonds prot-prot", "Hbonds prot-water"],
    rows=[
        ["CENTER (1000 ns)", "25.41 ± 1.97", "99.5%", "51.4 ± 34.2", "97.8 ± 9.7", "565.5 ± 25.1"],
        ["R1 (1000 ns)", "24.77 ± 1.40", "99.5%", "52.4 ± 34.6", "92.0 ± 8.3", "575.9 ± 24.0"],
    ],
    caption=(
        "Table 2: CASEIN per-replica summary. Both replicas now have all 7 planned "
        "analyses complete. “Contact” is the fraction of frames with a protein-water "
        "minimum distance ≤0.3 nm; R1 shows 1 sustained contact event across the full "
        "1000 ns run."
    ),
)

add_image_row([
    (FIG_PAPER / "PAPER_COMPARATIVE_RG.png", ""),
], width_cm=10)
para(
    "Figure 3: Radius of gyration, BLG vs. CASEIN, all replicas. BLG stays tightly "
    "compact (~1.5 nm, all 4 replicas) while CASEIN settles to a larger, still stable "
    "range (~2.5–2.7 nm) after its initial relaxation from an extended starting "
    "structure.",
    italic=True, size=10,
)

add_image_row([
    (FIG_PAPER / "PAPER_TIMESERIES_RG.png", ""),
], width_cm=14)
para(
    "Figure 3b: Rg vs. time. BLG (panel a) is flat and tightly clustered around 1.5 nm "
    "from t=0 – no relaxation needed, it started compact. CASEIN (panel b) starts "
    "extended (~4 nm, its AlphaFold starting structure) and visibly relaxes down to "
    "~2.5 nm within the first ~100 ns, then stays there – the relaxation transient is "
    "directly visible here, not just summarized as a mean.",
    italic=True, size=10,
)

add_image_row([
    (FIG_PAPER / "PAPER_COMPARATIVE_SASA.png", ""),
], width_cm=13)
para(
    "Figure 4: Accessible surface area, BLG calyx vs. CASEIN N-terminal region "
    "(residues 1–25), all replicas. The ~7-fold size difference is consistent across "
    "every replica of both proteins – not an artifact of any single run.",
    italic=True, size=10,
)

add_image_row([
    (FIG_PAPER / "PAPER_TIMESERIES_SASA.png", ""),
], width_cm=14)
para(
    "Figure 4b: SASA vs. time. BLG's calyx (panel a) fluctuates in a narrow band "
    "(~2–5.5 nm²) throughout, all 4 replicas overlapping closely. CASEIN's "
    "N-terminus (panel b) fluctuates far more broadly (roughly 20–32 nm²) but never "
    "drops anywhere near BLG's range – the size gap holds at every single timepoint, "
    "not just on average.",
    italic=True, size=10,
)

para(
    "CASEIN's near-constant interfacial contact (99.5% of frames in both CENTER and "
    "R1, versus BLG's much more selective, intermittent contact pattern across 4µs) "
    "is a clear "
    "structural contrast that directly supports the comparative title: BLG presents a "
    "small, selectively-accessible calyx, while CASEIN's disordered chain stays "
    "persistently near the interface with its N-terminal region continuously exposed. "
    "Rg for R1 confirms the same relaxation pattern already seen in CENTER: an initial "
    "compaction from the extended AlphaFold starting structure (~2.85 nm in the first "
    "100 ns) settling to a stable range (~2.5 nm) for the remainder of the trajectory – "
    "reassuring that this is a real, reproducible relaxation, not a one-off artifact of "
    "the CENTER run's starting conformation. Hydrogen-bonding is also now complete for "
    "both replicas and agrees closely (protein-protein 92.0–97.8, protein-water "
    "565.5–575.9, interface water-water 12015.6–12750.5 mean counts per frame) – "
    "another independent confirmation that CENTER's behavior was not a one-off."
)

add_image_row([
    (FIG_PAPER / "PAPER_TIMESERIES_CONTACT.png", ""),
], width_cm=14)
para(
    "Figure 5: Signed protein-to-interface gap vs. time (positive = inside the water "
    "bulk, negative = protruding past the water's statistical edge, into the "
    "interfacial/vacuum region). BLG (panel a) sits mostly positive with brief, "
    "distinct negative excursions – these are its 613 discrete contact events. "
    "CASEIN (panel b) sits almost entirely negative throughout both replicas, "
    "averaging around -0.6 nm – it does not just touch the interface, it "
    "persistently protrudes past it for virtually the whole trajectory.",
    italic=True, size=10,
)

doc.save(str(OUT))
print(f"Saved: {OUT}")
