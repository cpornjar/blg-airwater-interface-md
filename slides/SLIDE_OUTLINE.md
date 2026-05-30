# Slide Outline — Contact without Commitment
## COMFHA Lab Group Presentation

**Talk type**: Oral — 20 min + Q&A  
**Audience**: Lab group (familiar with MD, GROMACS, protein simulation)  
**Style**: ACADEMIC_NAVY  
**Format**: Keynote (via PPTX + Marp)  
**Slides**: 20  
**Figures available**: Fig 2 AB/CD (contact panels), Fig 3 (activation PDF), Fig 4 (SASA/orientation PDF)

---

| # | Title | Key points | Figure | Time | Cumulative |
|---|-------|-----------|--------|------|-----------|
| 1 | **Contact without Commitment** | Authors, COMFHA/KU, May 2026 | — | 0:30 | 0:30 |
| 2 | **Today's story** | 4 acts: Problem → Approach → Findings → Implications | — | 0:30 | 1:00 |
| 3 | **Why milk foam?** | BLG = dominant stabiliser; adsorbs over seconds-to-minutes; kinetic barrier measured, mechanism unknown | — | 1:00 | 2:00 |
| 4 | **The atomistic gap** | Experiments: time-averaged ensembles. Prior MD: oil-water only, pre-positioned, ≤100 ns. First unbiased AWI simulation = this work | — | 1:00 | 3:00 |
| 5 | **System: slab geometry** | 12×12×35 nm box; 4 µs cumulative; CENTER bulk-start + R1/R2/R3 near-interface replicas; CHARMM36m + TIP3P | Fig 2 (Z-position panel as system schematic) | 1:00 | 4:00 |
| 6 | **Contact metric: why it matters** | CoM distance blind for 4 nm protein; nearest-atom ≤0.3 nm = real surface touch; recovers 613 events vs ~0 with CoM | — | 0:45 | 4:45 |
| 7 | **Contact is frequent** | 613 events; 7.1–23.4% of frames per trajectory; penetration up to 0.71 nm; Fig 2 panels show repeated excursions | Fig 2 AB (CENTER + R1) | 1:15 | 6:00 |
| 8 | **Commitment is rare** | Only 6 events ≥10 ns (one 59 ns!); **zero** commit; 607/613 terminate within 10 ns | Fig 2 CD (R2 + R3) | 1:00 | 7:00 |
| 9 | **Long-event table** | 6 events: SASA 28.5–30.5 nm²; angle 44–75°; all non-activated; contact ≠ adsorption | — | 0:45 | 7:45 |
| 10 | **Global compactness: never unfolds** | Rg = 1.496±0.009 nm, flat; β-barrel RMSD ~0.21 nm; α-helix intact; 4 µs of stable fold near the AWI | Fig 3(b) Rg panel | 1:00 | 8:45 |
| 11 | **Calyx breathes — stationary process** | Fig 3(a): SASA 24–37 nm², recurring ~30–40 ns; not a one-shot pre-adsorption event | Fig 3(a) SASA panel | 1:00 | 9:45 |
| 12 | **Interface shifts which loop dominates** | Fig 3(c): RMSF; Bulk: Loop BC peak (0.54 nm); AWI: Loop CD/EF rises (0.39 nm); activation is loop-mediated, calyx-localised | Fig 3(c) RMSF panel | 1:15 | 11:00 |
| 13 | **SASA distribution: all replicas** | Fig 4(a) KDE; 24–37 nm² for all 4 replicas; p95 = 32.1 nm²; SASA never reaches "gate-open" | Fig 4(a) KDE | 1:00 | 12:00 |
| 14 | **Orientation: uniform and independent** | Fig 4(b) 2D joint; no quadrant clustering; r = +0.006; Obs/Indep ≈ 1.0 across threshold sweep | Fig 4(b) heatmap | 1:15 | 13:15 |
| 15 | **Statistics: block bootstrap** | SASA autocorrelation 232 ns; N_eff ≈ 17; 95% CI [−0.09, +0.11] — rules out \|r\| > 0.11 | — | 1:00 | 14:15 |
| 16 | **Scientific integrity: PBC lesson** | Original SASA: 45–62 nm² (freeSASA without unwrap); corrected: 24–37 nm²; MDAnalysis unwrap; 0 gate-open frames | — | 0:45 | 15:00 |
| 17 | **What this means** | Pre-commitment ensemble characterised; kinetic bottleneck is real (59 ns contact without commitment); this baseline is required before enhanced sampling | — | 1:30 | 16:30 |
| 18 | **Implications** | Loop CD/EF = engineering target; calyx flexibility > bulk hydrophobicity for mutant design; dimer adds steric/kinetic/orientational complexity | — | 1:00 | 17:30 |
| 19 | **What's next** | Enhanced sampling along (SASA, θ); β-casein (Paper 2); BLG dimer; TIP4P/2005 cross-check | — | 0:30 | 18:00 |
| 20 | **Summary + Q&A** | 3 takeaways: (1) Contact frequent, commitment rare (2) Compact globally, loop-mediated calyx (3) SASA ⊥ orientation on µs scale | — | 1:00 | 19:00 |

*Q&A buffer: 5–10 min*

---

## Time Budget

```
Slides 1–2   Framing      1:00
Slides 3–4   Motivation   2:00
Slides 5–6   Approach     1:45
Slides 7–9   Contact      3:00   ← longest block; this is the main claim
Slides 10–12 Calyx        3:15
Slides 13–15 Statistics   3:15
Slide  16    Integrity     0:45
Slides 17–20 Discussion   3:00
─────────────────────────────
Total                     18:00  (+ 2 min buffer, then Q&A)
```

## Figure Plan

| Figure file | Used in slide | How used |
|-------------|---------------|---------|
| `PAPER_FIG2_CONTACT_AB.png` | Slide 7 | Full-width: CENTER + R1 contact panels |
| `PAPER_FIG2_CONTACT_CD.png` | Slide 8 | Full-width: R2 + R3 contact panels |
| `PAPER_FIG3_ACTIVATION.pdf` | Slides 10–12 | Individual panels extracted: (a) SASA, (b) Rg, (c) RMSF |
| `Fig4_optionA.pdf` | Slides 13–14 | Individual panels: (a) KDE, (b) 2D joint |

## Keynote Output Plan

```
slides/
├── slides.md              # Marp markdown (portable, browser/PDF preview)
├── generate_pptx.py       # python-pptx script → presentation.pptx
├── presentation.pptx      # PPTX optimised for Keynote import
├── speaker_notes.md       # Full per-slide speaker notes
├── TALK_SCRIPT.md         # Word-for-word script + Q&A prep
├── SLIDE_OUTLINE.md       # This file
├── SLIDES_STATE.json      # State persistence
└── figures/               # Figure copies (PNG, PDF)
```

**To convert to Keynote on Mac:**  
Open `presentation.pptx` in Keynote → it imports natively → File → Save as → `.key`
