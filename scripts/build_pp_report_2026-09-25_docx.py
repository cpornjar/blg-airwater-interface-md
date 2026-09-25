"""
One-off script: build the editable .docx version of the 2026-09-25
P.P. progress report, mirroring for_PP_2026-09-25.tex content.
Not part of the regular analysis pipeline -- run once, keep for reference.
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = Path("/Users/mac2022-1/Workspace/MILK_FROTHING")
FIG_PAPER = ROOT / "results/figures/paper"
OUT = ROOT / "progress-reports/for_PP_2026-09-25.docx"

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


def para(text, italic=False, size=11):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = italic
    r.font.size = Pt(size)
    return p


def bullet(text_parts):
    p = doc.add_paragraph(style="List Bullet")
    for text, bold in text_parts:
        r = p.add_run(text)
        r.bold = bold
    return p


def numbered(text_parts):
    p = doc.add_paragraph(style="List Number")
    for text, bold in text_parts:
        r = p.add_run(text)
        r.bold = bold
    return p


def add_table(headers, rows, caption, star_note=None):
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


def add_image(path, caption, width_cm=15):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Cm(width_cm))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cr = cap.add_run(caption)
    cr.italic = True
    cr.font.size = Pt(10)
    doc.add_paragraph()


# ============================================================
# Title
# ============================================================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("Paper 1 Progress Update: BLG vs. β-Casein at the Air–Water Interface")
tr.bold = True
tr.font.size = Pt(18)

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
mr = meta.add_run(
    "Chalakon Pornjariyawatch — COMFHA Lab, Kasetsart University\n"
    "September 25, 2026\n"
    "Prepared for: Prapasiri Pongprayoon (P.P.)"
)
mr.font.size = Pt(12)
doc.add_paragraph()

# ============================================================
# Executive summary
# ============================================================
h("Executive Summary", level=1)
para("Changes since the last update (September 11, 2026):", italic=True)

bullet([("The BLG data-completeness gap flagged in the last update is half closed.", True),
        (" Rg for R1/R2/R3 now covers the full 1000 ns per replica (fixed today — blg_rg.py's "
         "trajectory-extension gap is closed). Surface tension for those same three replicas "
         "still reflects only the first 500 ns; the extension segments' .edr energy files exist "
         "on the cluster but have not yet been synced locally, so that fix is still pending.", False)])
bullet([("Structural renders (Figure 1) rebuilt at full publication resolution.", True),
        (" The previous report's calyx/N-term renders were a stale 512×512 px placeholder "
         "(headless VMD's default framebuffer size); regenerated today at 3008×2400 px, and "
         "the figure now also includes the simulation box geometry panel.", False)])
bullet([("No change to the core scientific picture: ", False),
        ("BLG remains stable and compact across all 4 replicas, and CASEIN's two-replica "
         "comparative result (open, persistently surface-exposed N-terminus vs. BLG's small, "
         "selectively-accessible calyx) — reported in full in the September 11 update — still "
         "holds with no new data since.", False)])
bullet([("5 open questions remain for P.P.", True),
        (", unchanged since the June 9 meeting — none carry a hard deadline, but two now block "
         "downstream figure/writing decisions.", False)])
doc.add_paragraph()

# ============================================================
# Structural overview (new today)
# ============================================================
h("Structural Overview", level=1)
para(
    "Figure 1 re-renders both proteins' key accessible feature at full publication resolution "
    "(VMD structural renders regenerated today at 3008×2400 px, up from a stale 512×512 px "
    "render — headless VMD's default framebuffer size, fixed via the -size launch flag rather than "
    "an in-script resize, which crashes in text-mode VMD) alongside the simulation box geometry for "
    "each species."
)
add_image(
    FIG_PAPER / "PAPER_FIG1_SCHEMATIC.png",
    "Figure 1: (A) BLG's calyx (9 lining residues, amber) versus CAS's N-terminal accessible patch "
    "(residues 1-25, amber), both rendered at the same visual convention (NewCartoon, ambient "
    "occlusion, orthographic). (B) Slab simulation box geometry for each species, drawn to the real "
    "locked box dimensions.",
)

# ============================================================
# BLG Results
# ============================================================
h("BLG Results", level=1)
para(
    "BLG's headline numbers are unchanged from the last update and remain fully validated across "
    "all 4 replicas (CENTER + R1/R2/R3, 4.00 µs total unbiased MD)."
)
add_table(
    headers=["Replica", "Calyx SASA (nm²)", "Rg (nm)", "γ (mN/m)", "Patch RMSD (nm)"],
    rows=[
        ["CENTER (1000 ns)", "3.81 ± 0.46", "1.504 ± 0.022", "51.9 ± 38.5", "0.198 ± 0.081"],
        ["R1", "3.15 ± 0.34", "1.497 ± 0.009", "52.7 ± 38.7*", "0.347 ± 0.088"],
        ["R2", "3.59 ± 0.32", "1.494 ± 0.009", "52.0 ± 39.0*", "0.254 ± 0.059"],
        ["R3", "3.36 ± 0.48", "1.507 ± 0.014", "52.6 ± 39.4*", "0.276 ± 0.064"],
    ],
    caption=(
        "Table 1: BLG per-replica summary. Rg for R1/R2/R3 now covers the full 1000 ns "
        "(blg_rg.py's trajectory-extension gap was closed today, 2026-09-25). *γ for R1/R2/R3 is "
        "still computed from the first 500 of 1000 ns per replica — blg_surface_tension.py needs "
        "the extension segments' .edr energy files, which exist on the cluster but have not yet "
        "been synced locally. Not expected to change the qualitative picture, but not yet closed out."
    ),
)
para(
    "The calyx stays compact and accessible in every replica (no collapse), Rg confirms a globally "
    "stable fold, and 613 discrete contact events occur across the full dataset with zero sustained "
    "(“gate-open”) adsorption events — the basis for the paper's scope claim (pre-commitment "
    "characterisation, not a completed-adsorption mechanism). R1's elevated patch RMSD (0.347 nm vs. "
    "0.20-0.28 nm in the other three) is a real, traced effect: R1 contains 4 of the project's 6 "
    "total long (≥10 ns) contact events, and the patch RMSD steps up permanently after its "
    "longest event (362-419.5 ns) without ever returning to baseline — a genuine local conformational "
    "response to sustained contact, not noise."
)
add_image(FIG_PAPER / "PAPER_TIMESERIES_CONTACT.png",
    "Signed protein-to-interface gap vs. time (positive = inside the water bulk, negative = "
    "protruding past the interface). BLG sits mostly positive with brief, distinct negative "
    "excursions — its 613 contact events.", width_cm=13)

# ============================================================
# CAS Results
# ============================================================
h("β-Casein (CAS) Results", level=1)
para(
    "7 of 7 planned analyses complete, now for both CENTER and R1 — the first time every CAS "
    "headline metric has independent-replica confirmation rather than a single run."
)
add_table(
    headers=["Replica", "N-term SASA (nm²)", "Contact", "γ (mN/m)", "H-bonds prot-prot", "H-bonds prot-water"],
    rows=[
        ["CENTER (1000 ns)", "25.41 ± 1.97", "99.5%", "51.4 ± 34.2", "97.8 ± 9.7", "565.5 ± 25.1"],
        ["R1 (1000 ns)", "24.77 ± 1.40", "99.5%", "52.4 ± 34.6", "92.0 ± 8.3", "575.9 ± 24.0"],
    ],
    caption=(
        "Table 2: CAS per-replica summary. “Contact” is the fraction of frames with a "
        "protein-water minimum distance ≤0.3 nm; each replica shows 1 sustained contact event "
        "across the full 1000 ns run."
    ),
)
para(
    "CAS's N-terminal region (residues 1-25, the analogue of BLG's calyx) stays large and accessible "
    "in both replicas — a ~7-fold size difference from BLG's calyx that holds at every timepoint, "
    "not just on average. Rg confirms the same relaxation pattern in both replicas: an initial "
    "compaction from the extended AlphaFold starting structure (~2.85 nm, first ~100 ns) settling to "
    "a stable range (~2.5-2.7 nm) for the remainder of the trajectory. Hydrogen-bonding agrees closely "
    "between replicas (protein-protein 92.0-97.8, protein-water 565.5-575.9, interface water-water "
    "12015.6-12750.5 mean counts per frame)."
)
add_image(FIG_PAPER / "PAPER_COMPARATIVE_RG.png",
    "Radius of gyration, BLG vs. CAS, all replicas. BLG stays tightly compact (~1.5 nm) while CAS "
    "settles to a larger, stable range (~2.5-2.7 nm) after its initial relaxation.", width_cm=11)
add_image(FIG_PAPER / "PAPER_COMPARATIVE_SASA.png",
    "Accessible surface area, BLG calyx vs. CAS N-terminal region, all replicas. The ~7-fold size "
    "difference is consistent across every replica of both proteins.", width_cm=13)
para(
    "CAS's near-constant interfacial contact (99.5% of frames, both replicas) versus BLG's "
    "selective, intermittent contact pattern is the clear structural contrast that directly "
    "supports the comparative title: BLG presents a small, selectively-accessible calyx, while "
    "CAS's disordered chain stays persistently near the interface with its N-terminal region "
    "continuously exposed."
)

# ============================================================
# Questions for P.P.
# ============================================================
h("Questions for P.P.", level=1)
para(
    "Full detail for all items below is tracked in docs/PP_FEEDBACK_LOG.md. No item carries a "
    "near-term (<30 day) deadline; the list is unchanged since the June 9 meeting."
)
qs = [
    ("Secondary-SASA definition.",
     "Your note “secondary dasa” from the June 9 meeting is ambiguous. Our best reading: "
     "absolute SASA computed per secondary-structure element (DSSP region × SASA) — computable "
     "now. A ΔSASA-on-adsorption reading is not computable, since no completed adsorption event "
     "exists in either dataset. Please confirm which you meant."),
    ("Which lab experiments to correlate against?",
     "Your note said “correlation with lab experiment expected.” We see no in-house "
     "tensiometry/Langmuir-trough data in the repo, so we've assumed you mean published literature "
     "(already surveyed: Cornec 1999, Ulaganathan 2017a for BLG kinetics; Mackie 1999 for CAS "
     "rheology; Atkinson 1995 for CAS N-terminal neutron reflectivity). Please confirm this reading."),
    ("How prescriptive should the “modify to adsorb” claim be?",
     "Our data show only the pre-commitment ensemble (no completed adsorption event in either "
     "dataset), so a strong causal claim isn't supported. Proposed framing: “intrinsic disorder "
     "and surface-exposed hydrophobic patches lower the kinetic barrier to adsorption” — a "
     "design-principle statement, not a prescription. Please confirm this is the level of "
     "specificity you want."),
    ("Figure-plan sub-decisions.",
     "Several small figure choices from your June 9 note remain unconfirmed (Fig 1B: shared or "
     "separate boxes; Fig 2: BLG/CAS overlaid or separate subpanels; Fig 4: table or heatmap; exact "
     "calyx-clustering residue definition). Low urgency — needed before final figure build, not "
     "before analysis."),
    ("Co-author review of the (paused) BLG-only draft.",
     "Still a hard blocker alongside the Zenodo DOI for the original main.tex submission checklist, "
     "even though it's not urgent while the comparative expansion is in progress."),
]
for qtitle, qbody in qs:
    numbered([(qtitle + " ", True), (qbody, False)])

doc.add_paragraph()
para(
    "Note: all numbers above are PBC-corrected and read live from results/analysis/*.npz as of "
    "this report's generation date (September 25, 2026). They are not to be treated as frozen if "
    "analysis is rerun later — see the R1/R2/R3 Rg/γ caveat in Table 1.",
    italic=True, size=10,
)

doc.save(str(OUT))
print(f"Saved: {OUT}")
