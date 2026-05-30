"""
build_presentation.py
=====================
Builds presentation.pptx using Marp PPTX as Keynote-compatible base,
replacing image slides with editable text + embedded figures.

Usage: python3 slides/build_presentation.py
"""
import zipfile, subprocess, shutil
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

ROOT = Path(__file__).resolve().parent.parent
FIGS = ROOT / "slides" / "figures"
BASE = ROOT / "slides" / "slides_base.pptx"
OUT  = ROOT / "slides" / "presentation.pptx"
MAC_HOST = "cp@100.118.196.110"
MAC_PATH = "/Users/cp/Documents/CP/COMFHA_Talk_May2026/presentation.pptx"

NAVY  = RGBColor(0x1A, 0x27, 0x44)
GOLD  = RGBColor(0xC9, 0xA8, 0x4C)
BLUE  = RGBColor(0x44, 0x72, 0xC4)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GRAY  = RGBColor(0x9C, 0xA3, 0xAF)
RED   = RGBColor(0xDC, 0x26, 0x26)
GREEN = RGBColor(0x16, 0xA3, 0x4A)

W = Inches(13.333); H = Inches(7.5)
BAR = Inches(1.1);  MAR = Inches(0.55); BW = W - MAR * 2

prs = Presentation(str(BASE))
prs.slide_width = W; prs.slide_height = H

# Remove all Marp image slides
sldIdLst = prs.slides._sldIdLst
for el in list(sldIdLst): sldIdLst.remove(el)
LAYOUT = prs.slide_layouts[0]

def S(): return prs.slides.add_slide(LAYOUT)

def bar(slide, title):
    from pptx.util import Emu
    sp = slide.shapes.add_shape(1, 0, 0, W, BAR)
    sp.fill.solid(); sp.fill.fore_color.rgb = NAVY; sp.line.fill.background()
    sp2 = slide.shapes.add_shape(1, 0, BAR, W, Pt(5))
    sp2.fill.solid(); sp2.fill.fore_color.rgb = GOLD; sp2.line.fill.background()
    tb = slide.shapes.add_textbox(MAR, Inches(0.12), BW, BAR - Inches(0.2))
    tf = tb.text_frame; tf.word_wrap = True
    r = tf.paragraphs[0].add_run()
    r.text = title; r.font.size = Pt(28); r.font.bold = True
    r.font.color.rgb = WHITE; r.font.name = "Helvetica Neue"

def dark(slide):
    sp = slide.shapes.add_shape(1, 0, 0, W, H)
    sp.fill.solid(); sp.fill.fore_color.rgb = NAVY; sp.line.fill.background()

def num(slide, n):
    tb = slide.shapes.add_textbox(W-Inches(1.1), H-Inches(0.32), Inches(1.0), Inches(0.28))
    r = tb.text_frame.paragraphs[0].add_run()
    r.text = f"{n}/20"; r.font.size = Pt(13); r.font.color.rgb = GRAY
    r.font.name = "Helvetica Neue"
    tb.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT

def txt(slide, text, l, t, w, h, size=20, color=NAVY, bold=False, align=PP_ALIGN.LEFT):
    tb = slide.shapes.add_textbox(l, t, w, h)
    tb.word_wrap = True; tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.alignment = align
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.color.rgb = color; r.font.bold = bold
    r.font.name = "Helvetica Neue Bold" if bold else "Helvetica Neue"

def fig(slide, path, caption=None):
    top = BAR + Pt(10)
    max_h = H - top - (Inches(0.45) if caption else Inches(0.15))
    if path.exists():
        pic = slide.shapes.add_picture(str(path), Inches(0.15), top, width=W-Inches(0.3))
        if pic.height > max_h:
            r = max_h / pic.height; pic.height = int(pic.height*r); pic.width = int(pic.width*r)
        pic.left = int((W - pic.width) / 2)
    else:
        txt(slide, f"[ {path.name} ]", MAR, top, BW, max_h, size=18, color=GRAY, align=PP_ALIGN.CENTER)
    if caption:
        txt(slide, caption, MAR, H-Inches(0.42), BW, Inches(0.38), size=13, color=GRAY)

def buls(slide, items, extra=Inches(0)):
    top = BAR + Pt(18); h = H - top - Inches(0.35) - extra
    tb = slide.shapes.add_textbox(MAR, top, BW, h)
    tb.word_wrap = True; tf = tb.text_frame; tf.word_wrap = True
    first = True
    for text, bold, color in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.space_before = Pt(3)
        r = p.add_run(); r.text = ("" if bold else "- ") + text
        r.font.size = Pt(19 if bold else 18); r.font.color.rgb = color
        r.font.bold = bold
        r.font.name = "Helvetica Neue Bold" if bold else "Helvetica Neue"

def hi(slide, text):
    from pptx.util import Emu
    y = H - Inches(0.82)
    sp = slide.shapes.add_shape(1, MAR-Inches(0.1), y, BW+Inches(0.2), Inches(0.65))
    sp.fill.solid(); sp.fill.fore_color.rgb = RGBColor(0xEE,0xF2,0xFF); sp.line.fill.background()
    sp2 = slide.shapes.add_shape(1, MAR-Inches(0.1), y, Pt(5), Inches(0.65))
    sp2.fill.solid(); sp2.fill.fore_color.rgb = GOLD; sp2.line.fill.background()
    txt(slide, text, MAR+Pt(8), y+Inches(0.1), BW-Pt(8), Inches(0.5),
        size=17, color=NAVY, bold=True, align=PP_ALIGN.CENTER)

# ── S1 Title ──────────────────────────────────────────────────────────────────
s=S(); dark(s)
txt(s,"Contact without Commitment",MAR,Inches(1.0),BW,Inches(2.0),size=52,color=WHITE,bold=True)
txt(s,"Atomistic Characterisation of beta-Lactoglobulin Adsorption Dynamics at the Air-Water Interface",
    MAR,Inches(2.9),BW,Inches(0.9),size=20,color=RGBColor(0xCB,0xD5,0xE1))
txt(s,"Chalakon Pornjariyawatch  |  Prapasiri Pongprayoon",MAR,Inches(3.85),BW,Inches(0.5),size=19,color=WHITE,bold=True)
txt(s,"COMFHA -- Kasetsart University  |  Lab Group Seminar  |  May 2026",MAR,Inches(4.35),BW,Inches(0.4),size=15,color=GRAY)
num(s,1)

# ── S2 Story ──────────────────────────────────────────────────────────────────
s=S(); bar(s,"Today's Story")
buls(s,[("THE PROBLEM",True,GOLD),("BLG: key foam stabiliser -- how does it recognise the interface?",False,NAVY),
    ("Kinetic barrier measured for decades; mechanism unknown at atomic scale",False,NAVY),
    ("OUR APPROACH",True,GOLD),("First unbiased atomistic MD of native BLG at AWI -- 4.00 us",False,NAVY),
    ("KEY FINDINGS",True,GOLD),("Contact frequent (613 events); commitment absent (0 of 613)",False,NAVY),
    ("Calyx mobile; Loop CD/EF interface-induced; SASA perp orientation",False,NAVY)],extra=Inches(0.85))
hi(s,"Four acts:  Problem  ->  Approach  ->  Findings  ->  Implications"); num(s,2)

# ── S3 Foam ───────────────────────────────────────────────────────────────────
s=S(); bar(s,"Why Milk Foam?")
buls(s,[("beta-Lactoglobulin (BLG): dominant whey protein in bovine milk (~3 g/L)",False,NAVY),
    ("Principal stabiliser of milk foam -- forms viscoelastic film at the AWI",False,NAVY),
    ("Adsorption is slow: seconds to minutes from bulk solution",False,NAVY),
    ("Kinetic barrier distinguishes BLG from more flexible proteins",False,NAVY),
    ("Classical model (Graham & Phillips 1979): surface tension -> global unfolding",False,GRAY),
    ("Assumed but never directly observed at atomic resolution",False,BLUE)],extra=Inches(0.85))
hi(s,"How does a folded, water-soluble protein recognise and populate the AWI?"); num(s,3)

# ── S4 Gap ────────────────────────────────────────────────────────────────────
s=S(); bar(s,"The Atomistic Gap")
buls(s,[("Experiments (tensiometry, ellipsometry, neutron reflectometry):",True,NAVY),
    ("-> Time-averaged surface properties. No individual molecular events.",False,GRAY),
    ("Prior MD studies of BLG at interfaces:",True,NAVY),
    ("-> Oil-water only (not AWI)",False,NAVY),
    ("-> Pre-positioned near interface -- not starting from bulk",False,NAVY),
    ("-> <= 100 ns -- far below seconds-to-minutes adsorption timescale",False,NAVY),
    ("This work: first unbiased atomistic simulation of native BLG at AWI",True,GOLD)]); num(s,4)

# ── S5 System ─────────────────────────────────────────────────────────────────
s=S(); bar(s,"System: 12x12x35 nm Slab -- 4.00 us Cumulative")
fig(s,FIGS/"PAPER_FIG2_CONTACT_AB.png",
    "SET 1A: CENTER bulk-start (1000 ns)  |  SET 1B: R1, R2, R3 near-interface (1000 ns each)  |  CHARMM36m + TIP3P"); num(s,5)

# ── S6 Metric ─────────────────────────────────────────────────────────────────
s=S(); bar(s,"Contact Metric: Why Nearest-Atom Distance")
buls(s,[("BLG monomer is ~4 nm in diameter",False,NAVY),
    ("Centre-of-mass stays 2-3 nm from interface even while touching it",False,GRAY),
    ("-> CoM distance is BLIND to actual surface contact",True,RED),
    ("Nearest-atom <= 0.3 nm: detects real surface touch",True,GOLD),
    ("-> Recovers 613 contact events vs. ~0 with CoM threshold",False,NAVY),
    ("Penetration depth resolved to 0.01 nm precision",False,NAVY)],extra=Inches(0.85))
hi(s,"Switching to nearest-atom distance reveals BLG visits the interface constantly"); num(s,6)

# ── S7 Frequent ───────────────────────────────────────────────────────────────
s=S(); bar(s,"Contact is Frequent -- CENTER + R1")
fig(s,FIGS/"PAPER_FIG2_CONTACT_AB.png",
    "CENTER: 97 events (12.5% of frames)  |  R1: 215 events (23.4%)  |  Penetration up to 0.71 nm"); num(s,7)

# ── S8 Rare ───────────────────────────────────────────────────────────────────
s=S(); bar(s,"Commitment is Rare -- R2 + R3")
fig(s,FIGS/"PAPER_FIG2_CONTACT_CD.png",
    "R2: 156 events  |  R3: 145 events  |  Total 613 -- only 6 sustain >= 10 ns  |  None commits"); num(s,8)

# ── S9 Table ──────────────────────────────────────────────────────────────────
s=S(); bar(s,"The 6 Long-Residency Events: All Non-Activated")
buls(s,[("Replica | Duration | Event-mean SASA | Angle | Committed?",True,NAVY),
    ("CENTER  |  ~10 ns  |  28.8 nm2  |  ~52 deg  |  No",False,NAVY),
    ("R1      |  59 ns   |  29.1 nm2  |  ~63 deg  |  No  <- longest event",True,GOLD),
    ("R1      |  ~12 ns  |  28.5 nm2  |  ~68 deg  |  No",False,NAVY),
    ("R1      |  ~11 ns  |  30.5 nm2  |  ~44 deg  |  No",False,NAVY),
    ("R1      |  ~10 ns  |  28.9 nm2  |  ~75 deg  |  No",False,NAVY),
    ("R3      |  ~10 ns  |  30.1 nm2  |  ~56 deg  |  No",False,NAVY)],extra=Inches(0.6))
txt(s,"All 6 events: SASA 28.5-30.5 nm2  |  zero activation frames  |  59 ns contact without commitment",
    MAR,H-Inches(0.9),BW,Inches(0.5),size=15,color=BLUE); num(s,9)

# ── S10-14 Figures ────────────────────────────────────────────────────────────
s=S(); bar(s,"Global Fold Preserved -- Never Unfolds in 4 us")
fig(s,FIGS/"PAPER_FIG3_ACTIVATION.png","Rg = 1.496 +/- 0.009 nm -- flat  |  beta-barrel RMSD 0.21-0.24 nm"); num(s,10)

s=S(); bar(s,"Calyx Breathes -- Stationary Stochastic Process")
fig(s,FIGS/"PAPER_FIG3_ACTIVATION.png","SASA: 24-37 nm2 (PBC-corrected)  |  Recurring fluctuations ~30-40 ns"); num(s,11)

s=S(); bar(s,"Interface Shifts Which Loop Dominates")
fig(s,FIGS/"PAPER_FIG3_ACTIVATION.png","Bulk: Loop BC dominant, RMSF 0.54 nm  |  Near-AWI: Loop CD/EF rises to 0.39 nm"); num(s,12)

s=S(); bar(s,"SASA Distribution: All Four Replicas")
fig(s,FIGS/"Fig4_optionA.png","All replicas: SASA 24-37 nm2  |  p95 = 32.1 nm2  |  No distinct activated regime"); num(s,13)

s=S(); bar(s,"Orientation: Uniform and Independent of SASA")
fig(s,FIGS/"Fig4_optionA.png","Pearson r = +0.006  |  No quadrant clustering  |  Obs/Indep ~1.0 across threshold sweep"); num(s,14)

# ── S15 Bootstrap ─────────────────────────────────────────────────────────────
s=S(); bar(s,"Statistical Robustness: Block Bootstrap")
buls(s,[("Challenge: SASA autocorrelation = 232 ns",True,NAVY),
    ("-> i.i.d. assumption breaks down for standard CIs",False,GRAY),
    ("Block bootstrap:",True,NAVY),("-> Autocorrelation: 81-394 ns per replica",False,NAVY),
    ("-> Block length: 232 ns",False,NAVY),("-> Effective N ~17 independent observations across 4 us",True,NAVY),
    ("Block bootstrap 95% CI:  [-0.09, +0.11]",True,GOLD),
    ("-> Rules out |r| > 0.11 at 95% confidence",True,GOLD)],extra=Inches(0.85))
hi(s,"SASA and calyx orientation are statistically independent on the us timescale"); num(s,15)

# ── S16 PBC ───────────────────────────────────────────────────────────────────
s=S(); bar(s,"Scientific Integrity: The PBC Lesson")
buls(s,[("Found a periodic-boundary artefact during analysis:",True,NAVY),
    ("freeSASA without MDAnalysis unwrap -> atoms split across PBC boundaries",False,GRAY),
    ("Before fix:  SASA 45-62 nm2  |  21 gate-open events",True,RED),
    ("After  fix:  SASA 24-37 nm2  |  0 gate-open events",True,GREEN),
    ("Fix: mda_unwrap applied to all 8006 gate frames",False,NAVY),
    ("Full disclosure in Methods section",False,NAVY),
    ("All results in this talk use PBC-corrected data",True,NAVY)]); num(s,16)

# ── S17 Meaning ───────────────────────────────────────────────────────────────
s=S(); bar(s,"What This Means")
buls(s,[("Prior models assumed:",True,NAVY),
    ("Contact -> global unfolding -> adsorption (Graham & Phillips)",False,GRAY),
    ("OR: brief contacts do not matter",False,GRAY),("What we observe:",True,NAVY),
    ("59 ns contact without commitment -> genuine kinetic bottleneck",False,NAVY),
    ("r = +0.006 -> no simple two-factor coupling as commitment trigger",False,NAVY),
    ("Global fold preserved -> commitment is not global unfolding",False,NAVY),
    ("First characterisation of the pre-commitment contact ensemble",True,GOLD)],extra=Inches(0.85))
hi(s,"Required foundation for designing enhanced-sampling calculations"); num(s,17)

# ── S18 Implications ──────────────────────────────────────────────────────────
s=S(); bar(s,"Implications for Protein Engineering")
buls(s,[("Loop CD/EF: the engineering target",True,GOLD),
    ("Becomes dominant near AWI -- interface-induced conformational preference",False,NAVY),
    ("Calyx flexibility mutations more effective than bulk hydrophobicity",False,NAVY),
    ("Dimer complexity (BLG dominant dimer above ~50 uM):",True,NAVY),
    ("Steric: dimer interface occludes Loop CD/EF region",False,NAVY),
    ("Kinetic: dimer must dissociate before calyx presents unobstructed",False,NAVY),
    ("Orientational: oblate shape alters rotational diffusion",False,NAVY)]); num(s,18)

# ── S19 Next ──────────────────────────────────────────────────────────────────
s=S(); bar(s,"What's Next")
buls(s,[("Paper 1 -- submission pipeline",True,GOLD),
    ("Zenodo upload -> DOI -> JCIS submission (IF ~9)",False,NAVY),
    ("Enhanced sampling -- the clear next step",True,NAVY),
    ("Metadynamics / umbrella sampling along (SASA, theta)",False,NAVY),
    ("Paper 2 -- beta-Casein at AWI",True,NAVY),
    ("AlphaFold2 structure ready; comparison with BLG ensemble",False,NAVY),
    ("BLG dimer + TIP4P/2005 cross-check",False,NAVY)]); num(s,19)

# ── S20 Summary ───────────────────────────────────────────────────────────────
s=S(); dark(s)
txt(s,"Summary",MAR,Inches(0.3),BW,Inches(0.7),size=44,color=WHITE,bold=True)
pts=[("1. Contact without commitment","613 events -- only 6 >= 10 ns, none commits"),
     ("2. Compact globally, loop-mediated locally","Rg stable; Loop CD/EF mediates calyx exposure near AWI"),
     ("3. SASA perp orientation on the us timescale","r = +0.006, CI [-0.09, +0.11] -- rules out |r| > 0.11")]
y=Inches(1.1)
for lb,bd in pts:
    txt(s,lb,MAR,y,BW,Inches(0.4),size=18,color=GOLD,bold=True)
    txt(s,bd,MAR,y+Inches(0.38),BW,Inches(0.45),size=20,color=WHITE)
    y+=Inches(1.05)
txt(s,"4 us of unbiased MD resolves the pre-commitment contact ensemble. Commitment requires enhanced sampling.   |   Thank you -- questions?",
    MAR,H-Inches(0.75),BW,Inches(0.65),size=16,color=GRAY,align=PP_ALIGN.CENTER)
num(s,20)

# ── Save & deduplicate ────────────────────────────────────────────────────────
prs.save(str(OUT))
seen = {}
with zipfile.ZipFile(OUT) as z:
    for item in z.infolist(): seen[item.filename] = z.read(item.filename)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, data in seen.items(): z.writestr(name, data)
print(f"Saved: {OUT.name}  ({OUT.stat().st_size//1024} KB)  {len(prs.slides)} slides")

# ── Push to Mac ───────────────────────────────────────────────────────────────
if shutil.which("rsync"):
    r = subprocess.run(["rsync","-q",str(OUT),f"{MAC_HOST}:{MAC_PATH}"],capture_output=True)
    if r.returncode == 0:
        subprocess.run(["ssh",MAC_HOST,f"chflags nohidden '{MAC_PATH}'"],capture_output=True)
        print(f"Pushed to Mac and unhidden.")
