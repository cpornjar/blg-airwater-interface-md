"""
One-off script: build the Thai-language, editable .docx version of the
2026-09-11 P.P. progress report, mirroring for_PP_2026-09-11.tex content.
Not part of the regular analysis pipeline -- run once, keep for reference.
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

ROOT = Path("/Users/mac2022-1/Workspace/MILK_FROTHING")
FIG_RENDER = ROOT / "results/figures/render"
FIG_PAPER = ROOT / "results/figures/paper"
OUT = ROOT / "progress-reports/for_PP_2026-09-11.docx"

doc = Document()

# ---- default font (Thai-capable) ----
style = doc.styles["Normal"]
style.font.name = "TH Sarabun New"
style.font.size = Pt(15)
rpr = style.element.get_or_add_rPr()
rFonts = rpr.find(qn("w:rFonts"))
if rFonts is None:
    rFonts = rpr.makeelement(qn("w:rFonts"), {})
    rpr.append(rFonts)
rFonts.set(qn("w:eastAsia"), "TH Sarabun New")

for sec in doc.sections:
    sec.top_margin = Cm(2)
    sec.bottom_margin = Cm(2)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(2.2)


def h(text, level=1):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "TH Sarabun New"
    return p


def para(text, bold=False, italic=False, size=15):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = "TH Sarabun New"
    return p


def bullet(text_parts):
    """text_parts: list of (text, bold) tuples for one bullet line"""
    p = doc.add_paragraph(style="List Bullet")
    for text, bold in text_parts:
        r = p.add_run(text)
        r.bold = bold
        r.font.name = "TH Sarabun New"
        r.font.size = Pt(14)
    return p


def add_table(headers, rows, caption, col_widths_cm=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    hdr = table.rows[0].cells
    for i, htext in enumerate(headers):
        hdr[i].text = htext
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(11)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
            for p in cells[i].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(11)
    cap = doc.add_paragraph()
    cap_run = cap.add_run(caption)
    cap_run.italic = True
    cap_run.font.size = Pt(11)
    cap_run.font.name = "TH Sarabun New"
    doc.add_paragraph()


def add_image_row(paths_captions, width_cm=7.5):
    """paths_captions: list of (path, sub-caption) shown side by side"""
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
        cr.font.size = Pt(11)
        cr.font.name = "TH Sarabun New"
    doc.add_paragraph()


# ============================================================
# Title
# ============================================================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title.add_run("รายงานความคืบหน้า Paper 1")
tr.bold = True
tr.font.size = Pt(22)
tr.font.name = "TH Sarabun New"

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sub.add_run("การศึกษาเปรียบเทียบ BLG และ β-Casein ที่ผิวสัมผัสอากาศ-น้ำ")
sr.font.size = Pt(15)
sr.font.name = "TH Sarabun New"

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
mr = meta.add_run("โดย Chalakon Pornjariyawatch\n11 กันยายน 2026\nเรียน: อาจารย์ Prapasiri Pongprayoon")
mr.font.size = Pt(13)
mr.font.name = "TH Sarabun New"
doc.add_paragraph()

# ============================================================
# Executive summary
# ============================================================
h("สรุปภาพรวม", level=1)

bullet([
    ("ชุดข้อมูล BLG เสร็จสมบูรณ์และสอดคล้องกันภายใน ", True),
    ("จากทั้ง 4 replica อิสระ (รวม MD แบบไม่มี bias 4.00 ไมโครวินาที) "
     "ทั้ง 4 replica แสดงโครงสร้างที่กระชับและเสถียร (Rg 1.49–1.50 nm) "
     "ไม่มีหลักฐานว่าโปรตีนเปลี่ยนโครงสร้างถาวรเมื่อสัมผัสกับผิวน้ำ-อากาศ", False),
])
bullet([
    ("CASEIN มี replica อิสระตัวที่สอง (R1) เป็นครั้งแรก ", True),
    ("คู่กับ CENTER เดิม วิเคราะห์ครบทั้ง 7 รายการในทั้งสอง replica "
     "พื้นที่ผิวที่เข้าถึงได้ของปลาย N (N-terminal) ให้ค่าใกล้เคียงกันมากในทั้งสอง "
     "replica (24.8–25.4 nm²) เสริมความน่าเชื่อถือของข้อสรุป “open chain”", False),
])
bullet([
    ("ข้อสรุปเปรียบเทียบหลักยังคงแข็งแรงเมื่อมีการทำซ้ำจริง: ", True),
    ("calyx ของ BLG เล็กและเข้าถึงได้แบบเลือกสรร (3.15–3.81 nm²) ขณะที่ปลาย N ของ "
     "CASEIN ใหญ่กว่ามากและแทบจะสัมผัสผิวตลอดเวลา (สัมผัส 99.5% ของเฟรม ทั้งใน CENTER "
     "และ R1) สอดคล้องกับชื่อเปเปอร์ “An Accessible Calyx and an Open Chain”", False),
])
bullet([
    ("แรงตึงผิว (surface tension) ตรวจสอบไขว้กันได้ทั้งระหว่างสปีชีส์และ replica ", True),
    ("(BLG ≈52 mN/m, CAS ≈52 mN/m) ตรงกับค่าอ้างอิงของโมเดลน้ำ TIP3P ในวรรณกรรม "
     "(≈50–52 mN/m) เป็นการตรวจสอบความสอดคล้องภายในที่ดีสำหรับทั้งสอง force field", False),
])
bullet([
    ("พบประเด็นข้อมูลไม่ครบถ้วนหนึ่งจุดและกำลังแก้ไข: ", True),
    ("3 ใน 4 replica ของ BLG ถูกรันแบบแบ่งเป็นหลายช่วง (segment) — เฉพาะ 2 การวิเคราะห์ "
     "(Rg และ surface tension) ที่สคริปต์ปัจจุบันยังอ่านแค่ช่วงแรก (500 จาก 1000 ns) "
     "สำหรับ 3 replica นั้น ส่วน RMSD และ calyx SASA ครบ 1000 ns เต็มแล้วทั้งหมด "
     "ไม่ทำให้ผลที่มีอยู่ผิดพลาด ค่าที่ได้สอดคล้องภายในและตรงกับตัวเลขที่เคยรายงานไว้ "
     "แต่ตารางรายreplica ด้านล่างควรอ่านโดยคำนึงถึงข้อจำกัดนี้จนกว่าจะแก้เสร็จ "
     "(ดูหมายเหตุใต้ตารางที่ 1)", False),
])
doc.add_paragraph()

# ============================================================
# Figure 1 - VMD renders
# ============================================================
add_image_row([
    (FIG_RENDER / "blg_calyx_crop.png", "(a) BLG: โครงสร้างกระชับ, calyx patch (สีส้ม)"),
    (FIG_RENDER / "cas_patch_crop.png", "(b) CASEIN: สายโซ่ยืด, ปลาย N (สีส้ม)"),
], width_cm=7.0)
para(
    "รูปที่ 1: ความแตกต่างเชิงโครงสร้างระหว่างโปรตีนทั้งสอง (ภาพเรนเดอร์จาก VMD) "
    "โครงสร้างกระชับของ BLG ที่ calyx ถูกซ่อนอยู่เกือบทั้งหมด เทียบกับสายโซ่ยืดของ "
    "CASEIN ที่ไม่มีโครงสร้างแน่นอน โดยบริเวณปลาย N ถูกเปิดเผยตั้งแต่โครงสร้างเริ่มต้น",
    italic=True, size=11,
)
doc.add_paragraph()

# ============================================================
# Section 1 - BLG
# ============================================================
h("1. ผลการวิเคราะห์ BLG", level=1)

para(
    "ตัวเลขหลัก (ไม่เปลี่ยนแปลง ผ่านการแก้ไข PBC แล้ว คำนวณจากทั้ง 4 replica): "
    "เหตุการณ์สัมผัส (contact events) รวม 613 ครั้ง (97 ใน CENTER, 516 ใกล้ผิวสัมผัส"
    "ใน replica อื่นๆ); เหตุการณ์สัมผัสยาว (≥10 ns) 6 ครั้ง; ช่วง SASA ของ calyx "
    "24–37 nm² (ค่าเฉลี่ย 28.95 nm²); ค่าสหสัมพันธ์เพียร์สันระหว่าง SASA กับมุมการวางตัว "
    "r = +0.006 (ช่วงความเชื่อมั่น 95% จาก block-bootstrap [−0.09, +0.11]) "
    "ไม่พบความสัมพันธ์กันภายในขอบเขตนี้ ผลเหล่านี้สนับสนุนกรอบแนวคิดปัจจุบันของเปเปอร์: "
    "calyx ของ BLG ยังคงเข้าถึงได้ตลอด แต่โปรตีนไม่ได้ “ผูกมัด” เข้าสู่สถานะที่จับยึด"
    "และหมุนตัวถาวรภายในช่วงเวลาที่จำลอง"
)
para(
    "โครงสร้างทุติยภูมิ (DSSP) คงที่ในทั้ง 4 replica: Helix 10.5–12.4%, "
    "Sheet 36.0–36.8%, Coil 50.8–52.9% พันธะไฮโดรเจน (เฉพาะ CENTER ในตอนนี้): "
    "protein-protein 107.3 ± 5.6, protein-water 393.2 ± 13.2, "
    "interface water-water 9539.6 ± 328.4 (ค่าเฉลี่ยจำนวนต่อเฟรม)"
)

add_table(
    headers=["Replica", "Rg (nm)*", "RMSD backbone (nm)", "RMSD patch (nm)",
             "Calyx SASA (nm²)", "γ (mN/m)*"],
    rows=[
        ["CENTER (1000 ns)", "1.504 ± 0.022", "0.229", "0.198", "3.81 ± 0.46", "51.9 ± 38.5"],
        ["R1", "1.497 ± 0.009", "0.237", "0.347", "3.15 ± 0.34", "52.7 ± 38.7"],
        ["R2", "1.493 ± 0.008", "0.206", "0.254", "3.59 ± 0.32", "52.0 ± 39.0"],
        ["R3", "1.499 ± 0.012", "0.268", "0.276", "3.36 ± 0.48", "52.6 ± 39.4"],
    ],
    caption=(
        "ตารางที่ 1: สรุปโครงสร้างของ BLG รายreplica *เฉพาะ Rg และ γ (surface tension) "
        "ของ R1/R2/R3 ที่ยังสะท้อนแค่ 500 จาก 1000 ns แรกที่แต่ละ replica รันจริง "
        "การแก้ไขให้รวมช่วงที่เหลือของ 2 การวิเคราะห์นี้กำลังดำเนินการอยู่ ส่วน RMSD และ "
        "calyx SASA ของ R1/R2/R3 ครบ 1000 ns เต็มแล้ว (สคริปต์วิเคราะห์รวม extension "
        "trajectory ไว้แล้ว)"
    ),
)

# ============================================================
# Section 2 - CASEIN
# ============================================================
h("2. ผลการวิเคราะห์ CASEIN (β-casein)", level=1)

para(
    "ผลเปรียบเทียบแรกที่มีการทำซ้ำจริง (n=2): พื้นที่ผิวที่เข้าถึงได้ของบริเวณปลาย N "
    "(residue 1-25) ซึ่งเทียบเท่ากับ calyx SASA ของ BLG คือ 24.77 ± 1.40 nm² ใน R1 "
    "เทียบกับ 25.41 ± 1.97 nm² ใน CENTER การรันอิสระ 1000 ns ทั้งสองครั้งให้ผลใกล้เคียง"
    "กันมาก เป็นหลักฐานที่ดีว่านี่เป็นคุณสมบัติจริงของโปรตีนที่ทำซ้ำได้ ไม่ใช่ความบังเอิญจาก"
    "โครงสร้างเริ่มต้นเดียว"
)

add_table(
    headers=["Replica", "N-term SASA (nm²)", "Contact", "γ (mN/m)",
             "Hbonds prot-prot", "Hbonds prot-water"],
    rows=[
        ["CENTER (1000 ns)", "25.41 ± 1.97", "99.5%", "51.4 ± 34.2", "97.8 ± 9.7", "565.5 ± 25.1"],
        ["R1 (1000 ns)", "24.77 ± 1.40", "99.5%", "52.4 ± 34.6", "92.0 ± 8.3", "575.9 ± 24.0"],
    ],
    caption=(
        "ตารางที่ 2: สรุปผล CASEIN รายreplica ทั้งสอง replica วิเคราะห์ครบทั้ง 7 "
        "รายการแล้ว การวิเคราะห์พันธะไฮโดรเจนของ R1 เสร็จล่าสุด “Contact” คือ "
        "สัดส่วนเฟรมที่ระยะห่างต่ำสุดระหว่างโปรตีนกับน้ำ ≤0.3 nm; R1 พบเหตุการณ์สัมผัส"
        "ต่อเนื่อง 1 ครั้งตลอด 1000 ns"
    ),
)

add_image_row([
    (FIG_PAPER / "PAPER_COMPARATIVE_SASA.png", ""),
], width_cm=11)
para(
    "รูปที่ 2: พื้นที่ผิวที่เข้าถึงได้ (SASA) เทียบระหว่าง calyx ของ BLG กับบริเวณปลาย N "
    "ของ CASEIN (residue 1-25) ทุก replica ความแตกต่างขนาด ~7 เท่าสอดคล้องกันในทุก "
    "replica ของทั้งสองโปรตีน ไม่ใช่ความบังเอิญจากการรันครั้งใดครั้งหนึ่ง",
    italic=True, size=11,
)

para(
    "การสัมผัสผิวแทบตลอดเวลาของ CASEIN (99.5% ของเฟรม ทั้งใน CENTER และ R1 เทียบกับรูปแบบการสัมผัส"
    "ของ BLG ที่เลือกสรรและไม่ต่อเนื่องตลอด 4µs) เป็นความแตกต่างเชิงโครงสร้างที่ชัดเจน"
    "ซึ่งสนับสนุนชื่อเรื่องเปรียบเทียบโดยตรง: BLG มี calyx ขนาดเล็กที่เข้าถึงได้แบบเลือกสรร "
    "ขณะที่สายโซ่ไร้ระเบียบของ CASEIN อยู่ใกล้ผิวสัมผัสอย่างต่อเนื่องโดยบริเวณปลาย N ถูก"
    "เปิดเผยตลอดเวลา ค่า Rg ของ R1 ยืนยันรูปแบบการคลายตัว (relaxation) แบบเดียวกับที่"
    "เห็นใน CENTER: การหดตัวเริ่มต้นจากโครงสร้างเริ่มต้นแบบยืดของ AlphaFold (~2.85 nm "
    "ใน 100 ns แรก) จนคงที่ในช่วง (~2.5 nm) ตลอดที่เหลือของ trajectory เป็นเรื่องน่าอุ่นใจ"
    "ว่านี่คือการคลายตัวที่แท้จริงและทำซ้ำได้ ไม่ใช่ความบังเอิญของโครงสร้างเริ่มต้นเฉพาะการรัน"
    "ของ CENTER พันธะไฮโดรเจนวิเคราะห์เสร็จครบทั้งสอง replica แล้วเช่นกัน และให้ค่าใกล้เคียง"
    "กัน (protein-protein 92.0–97.8, protein-water 565.5–575.9, interface "
    "water-water 12015.6–12750.5 ค่าเฉลี่ยต่อเฟรม) เป็นการยืนยันอิสระอีกชุดว่าพฤติกรรม"
    "ที่เห็นใน CENTER ไม่ใช่ความบังเอิญ"
)

# ============================================================
# Section 3 - Questions
# ============================================================
h("3. คำถามสำหรับอาจารย์", level=1)

qs = [
    ("IFSC2026 (เร่งด่วนเรื่องเวลา)",
     "วันปิดรับบทคัดย่อคือ 25 กันยายน 2026 เหลืออีก 14 วันนับจากวันที่รายงานนี้ "
     "ยังไม่มีการยืนยันว่าจะเข้าร่วมงานนี้จริงหรือไม่ หรือรูปแบบใด (BLG อย่างเดียวเป็น"
     "เรื่องราวที่สมบูรณ์ vs BLG+CAS ที่ยังดำเนินการอยู่) ที่อาจารย์อยากให้ใช้สำหรับ"
     "โปสเตอร์ ต้องการคำตอบภายในสัปดาห์นี้เพื่อให้มีเวลาเขียนบทคัดย่อ"),
    ("คำนิยาม “Secondary SASA”",
     "บันทึกวันที่ 9 มิถุนายนของอาจารย์คลุมเครือระหว่างการตีความแบบ SASA ต่อ "
     "secondary-structure-element (คำนวณได้ตอนนี้) กับ ΔSASA เมื่อเกิดการดูดซับ "
     "(คำนวณไม่ได้ เพราะไม่มีเหตุการณ์ดูดซับที่สมบูรณ์ในชุดข้อมูลทั้งสอง) เราขอเสนอแบบแรก "
     "ขอคำยืนยันสั้นๆ จากอาจารย์เพื่อให้เราสร้างมันได้"),
    ("การเทียบกับผลการทดลองในห้องแล็บ",
     "การเปรียบเทียบ “correlation with lab experiment” ควรเทียบกับวรรณกรรมที่"
     "ตีพิมพ์แล้ว (สำรวจไว้แล้ว) หรือข้อมูลจากห้องแล็บภายใน (in-house)? เราไม่พบหลักฐานว่า"
     "กลุ่มวิจัยมีศักยภาพด้าน tensiometry ภายใน จึงสันนิษฐานว่าเป็นวรรณกรรม ขอความกรุณา"
     "ยืนยัน"),
    ("ข้อความ “modify to adsorb” ควรมีความชัดเจน/เจาะจงแค่ไหน?",
     "เรามีข้อมูลสนับสนุนข้อความแบบหลักการออกแบบที่นุ่มนวล (ความไม่เป็นระเบียบ + "
     "hydrophobic patch ที่เปิดเผย ช่วยลดพลังงานกระตุ้นสำหรับการดูดซับ) แต่ไม่ใช่ข้อความ"
     "เชิงเหตุ-ผลที่หนักแน่น เพราะไม่มีชุดข้อมูลใดแสดงเหตุการณ์ดูดซับที่สมบูรณ์ ขอให้อาจารย์"
     "ยืนยันว่านี่คือระดับข้อความที่เหมาะสมสำหรับ Paper 1"),
    ("การตรวจทานร่างต้นฉบับ BLG-only โดยอาจารย์ร่วม",
     "ยังคงเป็นอุปสรรคหลักที่ขวางการส่งตีพิมพ์ เมื่อใดที่อาจารย์มีเวลาตรวจทาน เราพร้อมแล้ว"),
]
for i, (qtitle, qbody) in enumerate(qs, start=1):
    bullet([(f"{i}. {qtitle} — ", True), (qbody, False)])

doc.add_paragraph()
para(
    "หมายเหตุ: ตัวเลขทั้งหมดข้างต้นผ่านการแก้ไข PBC แล้ว และอ่านโดยตรงจากไฟล์ผลลัพธ์"
    "ปัจจุบัน ณ วันที่สร้างรายงานนี้ ถือเป็นค่าปัจจุบัน ไม่ใช่ค่าตายตัว หากมีการรัน analysis "
    "ใหม่ในภายหลัง",
    italic=True, size=11,
)

doc.save(str(OUT))
print(f"Saved: {OUT}")
