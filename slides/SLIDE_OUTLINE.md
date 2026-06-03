# Slide Outline — Contact without Commitment
## COMFHA Lab Group Presentation

**Talk type**: Oral — 20 min + Q&A
**Audience**: Lab group (familiar with MD, GROMACS, protein simulation)
**Style**: ACADEMIC_NAVY
**Format**: Keynote (presentation_final.key / .pptx)
**Slides**: 15
**Figures available**: Fig 2 AB/CD, Fig 3 (activation PDF), Fig 4 (SASA/orientation PDF)

---

| # | Title | Key points | Time | Cumulative |
|---|-------|-----------|------|-----------|
| 1 | **Contact without Commitment** | Authors, COMFHA/KU, May 2026; Paper 10/10 READY → JCIS | 0:30 | 0:30 |
| 2 | **Today's Story** | 4 acts: Problem → Approach → Findings → Implications | 0:30 | 1:00 |
| 3 | **The Problem** | BLG dominant stabiliser; slow adsorption; no unbiased AWI MD; CoM metric blind | 2:00 | 3:00 |
| 4 | **Our Approach** | 12×12×35 nm slab; 4 × 1000 ns; CENTER + R1/R2/R3; nearest-atom → 613 events | 1:45 | 4:45 |
| 5 | **Finding 1 — Contact Is Frequent** | 613 events; 7–23% frames; 0.71 nm penetration; touch-and-retreat | 1:15 | 6:00 |
| 6 | **Finding 2 — Commitment Is Absent** | 6 events ≥10 ns; longest 59 ns; 0 stable adsorptions; long-event SASA 28.5–30.5 nm² | 1:45 | 7:45 |
| 7 | **Finding 3 — Compact Globally, Breathing Locally** | Rg 1.496±0.009 nm flat; β-barrel intact; SASA 24–37 nm² recurring ~30–40 ns bursts | 2:00 | 9:45 |
| 8 | **Finding 4 — Interface Shifts Which Loop Opens** | Bulk: Loop BC 0.54 nm; AWI: Loop CD/EF 0.39 nm; Loop CD/EF = engineering target | 1:15 | 11:00 |
| 9 | **Finding 5 — SASA and Orientation Are Independent** | KDE 24–37 nm² all replicas; 2D joint uniform; r = +0.006; threshold sweep Obs/Indep ≈ 1.0 | 2:15 | 13:15 |
| 10 | **The Statistics Behind the Independence Claim** | Autocorrelation 232 ns; N_eff ≈ 17; block bootstrap CI [−0.09, +0.11] | 1:00 | 14:15 |
| 11 | **Scientific Integrity — We Found and Fixed Our Own Error** | freeSASA without unwrap → 45–62 nm²; MDAnalysis unwrap → 24–37 nm²; 0 gate-open frames | 0:45 | 15:00 |
| 12 | **What This Work Establishes** | First pre-commitment ensemble characterisation; 3 findings; baseline for enhanced sampling | 1:30 | 16:30 |
| 13 | **Implications for the Field** | Loop CD/EF = engineering target; (SASA, θ) = CV; contact/commitment reframes kinetics | 1:00 | 17:30 |
| 14 | **What Comes Next** | β-Casein Paper 2 (Jul–Sep 2026); metadynamics; Paper 1 pending Zenodo + P.P. | 0:30 | 18:00 |
| 15 | **Summary** | (1) Contact frequent, commitment absent (2) Compact globally, loop-mediated (3) SASA ⊥ orientation | 1:00 | 19:00 |

*Q&A buffer: 5–10 min*

---

## Time Budget

```
Slides 1–2   Framing        1:00
Slide  3     Problem        2:00
Slide  4     Approach       1:45
Slides 5–6   Contact        3:00   <- contact/commitment dichotomy
Slides 7–8   Structure      3:15   <- calyx + loop findings
Slide  9     Independence   2:15   <- SASA vs orientation
Slide  10    Statistics     1:00
Slide  11    Integrity      0:45
Slides 12–13 Discussion     2:30
Slides 14–15 Close          1:30
Total                      19:00   (+ 1 min buffer, then Q&A)
```

## Figure Plan

| Figure file | Slide | How used |
|-------------|-------|---------|
| PAPER_FIG2_CONTACT_AB.png | 5 | CENTER + R1 contact panels |
| PAPER_FIG2_CONTACT_CD.png | 6 | R2 + R3 contact panels |
| PAPER_FIG3_ACTIVATION.pdf | 7–8 | Panels: (a) SASA, (b) Rg, (c) RMSF |
| Fig4_optionA.pdf | 9 | Panels: (a) KDE, (b) 2D joint |

## Active Files

- **Use**: `slides/COMFHA_Talk_May2026/presentation_final.pptx` / `.key` (15 slides)
- **Support**: `speaker_notes.md`, `TALK_SCRIPT.md`, `PRESENTATION_CHEATSHEET.md`
- **Legacy**: `slides.md` (Marp source, 20-slide structure — do not use for talks)
