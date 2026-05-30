---
marp: true
theme: default
paginate: true
size: 16:9
style: |
  /* ── Base ─────────────────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  :root {
    --navy:  #1A2744;
    --gold:  #C9A84C;
    --blue:  #4472C4;
    --white: #FFFFFF;
    --gray:  #9CA3AF;
    --bg:    #FFFFFF;
  }

  section {
    font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;
    background: var(--bg);
    color: var(--navy);
    font-size: 22px;
    line-height: 1.5;
    padding: 48px 60px 40px;
  }

  /* ── Title bar on all content slides ──────────────────────────── */
  h1 {
    background: var(--navy);
    color: var(--white);
    font-size: 30px;
    font-weight: 700;
    margin: -48px -60px 32px;
    padding: 20px 60px;
    border-bottom: 4px solid var(--gold);
    letter-spacing: 0.02em;
  }

  h2 { color: var(--navy); font-size: 22px; font-weight: 600; margin: 0 0 8px; }
  h3 { color: var(--blue); font-size: 18px; font-weight: 600; }

  ul { margin: 8px 0 0 0; padding-left: 1.4em; }
  li { margin-bottom: 10px; }
  li::marker { color: var(--gold); }

  strong { color: var(--gold); font-weight: 700; }
  em     { color: var(--blue);  font-style: normal; font-weight: 600; }

  table {
    width: 100%; border-collapse: collapse; font-size: 19px;
    margin-top: 16px;
  }
  th {
    background: var(--navy); color: var(--white);
    padding: 8px 14px; text-align: left;
  }
  td { padding: 7px 14px; border-bottom: 1px solid #E2E8F0; }
  tr:nth-child(even) td { background: #F8FAFC; }

  /* ── Slide number ──────────────────────────────────────────────── */
  section::after {
    font-size: 13px; color: var(--gray);
    bottom: 14px; right: 24px;
  }

  /* ── Special classes ───────────────────────────────────────────── */
  section.title-slide {
    background: var(--navy);
    color: var(--white);
    display: flex;
    flex-direction: column;
    justify-content: center;
    text-align: left;
    padding: 60px 80px;
  }
  section.title-slide h1 {
    background: none;
    margin: 0 0 12px;
    padding: 0;
    font-size: 42px;
    border-bottom: 3px solid var(--gold);
    padding-bottom: 16px;
  }
  section.title-slide h2 {
    color: #CBD5E1;
    font-size: 22px;
    font-weight: 400;
    margin: 0 0 28px;
  }
  section.title-slide p {
    color: #94A3B8;
    font-size: 18px;
    margin: 4px 0;
  }

  section.figure-slide { padding: 36px 40px 32px; }
  section.figure-slide h1 { margin: -36px -40px 20px; }
  section.figure-slide img { max-height: 75vh; max-width: 96%; display: block; margin: 0 auto; }

  section.section-break {
    background: var(--navy);
    color: var(--white);
    justify-content: center;
    text-align: center;
  }
  section.section-break h1 {
    background: none; margin: 0; padding: 0;
    font-size: 44px; border: none;
  }
  section.section-break p { color: #94A3B8; font-size: 20px; margin-top: 16px; }

  .two-col { display: flex; gap: 40px; }
  .col      { flex: 1; }

  .highlight-box {
    background: #EEF2FF; border-left: 4px solid var(--gold);
    padding: 14px 18px; border-radius: 4px; margin-top: 16px;
    font-size: 20px;
  }
---

<!-- _class: title-slide -->
<!-- _paginate: false -->

# Contact without Commitment

## Atomistic Characterisation of β-Lactoglobulin Adsorption Dynamics at the Air–Water Interface

Chalakon Pornjariyawatch · Prapasiri Pongprayoon

COMFHA — Computational Modelling in Food, Health and Agriculture
Department of Chemistry, Kasetsart University

*Lab Group Seminar · May 2026*

---

# Today's Story

<div class="two-col">
<div class="col">

**The problem**
BLG stabilises milk foam — but *how* does it recognise the interface?

**Our approach**
First unbiased atomistic MD of native BLG at the air–water interface — 4 µs cumulative

</div>
<div class="col">

**Key findings**
Contact is frequent; commitment is rare.
Calyx mobile but globally compact.
SASA and orientation: independent.

**What it means**
Pre-commitment ensemble characterised.
Enhanced sampling is the clear next step.

</div>
</div>

<div class="highlight-box">
Four acts: <strong>Problem</strong> → <strong>Approach</strong> → <strong>Findings</strong> → <strong>Implications</strong>
</div>

---

# Why Milk Foam?

- **β-Lactoglobulin (BLG)**: dominant whey protein in bovine milk (~3 g/L)
- Principal stabiliser of milk foam — forms viscoelastic film at air–water interface

- Adsorption is **slow**: seconds to minutes from bulk
- A **kinetic energy barrier** distinguishes BLG from more flexible whey proteins
- Classical model (Graham & Phillips 1979): surface tension induces *global unfolding*
  — assumed but **never directly observed** at atomic scale

<div class="highlight-box">
Central question: <em>how does a folded, water-soluble protein recognise and populate the AWI?</em>
</div>

---

# The Atomistic Gap

<div class="two-col">
<div class="col">

**What experiments give us**
- Time-averaged surface properties (tensiometry, ellipsometry, NR)
- Phenomenology: adsorption rate, partial unfolding in adsorbed state
- No individual molecular events

</div>
<div class="col">

**What prior MD gives us**
- BLG at *oil–water* only (not AWI)
- Starting positions: pre-placed near interface
- Duration: ≤100 ns — far below the µs adsorption timescale
- No native-fold BLG at AWI

</div>
</div>

<div class="highlight-box">
<strong>This work:</strong> first unbiased atomistic simulation of native BLG at the air–water interface
</div>

---

<!-- _class: figure-slide -->

# System: Slab Geometry — 4 µs Cumulative

![](figures/PAPER_FIG2_CONTACT_AB.png)

> **Box**: 12 × 12 × 35 nm · **Force field**: CHARMM36m + TIP3P · **SET 1A**: CENTER bulk-start (1000 ns) · **SET 1B**: R1, R2, R3 near-interface replicas (1000 ns each)

---

# Contact Metric: Why It Matters

- A BLG monomer is **~4 nm** in diameter
- Centre-of-mass distance stays **2–3 nm** from the interface even when an atom is touching it
- CoM threshold: **blind to actual surface contact**

| Metric | Contact events detected | Penetration resolved? |
|--------|------------------------|----------------------|
| CoM distance | ~0 | No |
| **Nearest-atom ≤ 0.3 nm** | **613** | **Yes — to 0.01 nm** |

<div class="highlight-box">
Switching to nearest-atom distance reveals that BLG visits the interface <strong>constantly</strong>
</div>

---

<!-- _class: figure-slide -->

# Contact is Frequent — CENTER + R1

![](figures/PAPER_FIG2_CONTACT_AB.png)

> **CENTER**: **97** events (12.5% of frames) · **R1**: **215** events (23.4% of frames) · Single atoms penetrate up to **0.71 nm** past the interface plane

---

<!-- _class: figure-slide -->

# Commitment is Rare — R2 + R3

![](figures/PAPER_FIG2_CONTACT_CD.png)

> **R2**: 156 events · **R3**: 145 events · **Total: 613 events** — only **6 sustain ≥ 10 ns**, and **none commits**

---

# Long-Residency Events: All Non-Activated

| # | Replica | Duration | Event-mean SASA | Angle | Committed? |
|---|---------|---------|----------------|-------|-----------|
| 1 | CENTER | ~10 ns | 28.8 nm² | ~52° | **No** |
| 2 | R1 | **59 ns** | 29.1 nm² | ~63° | **No** |
| 3 | R1 | ~12 ns | 28.5 nm² | ~68° | **No** |
| 4 | R1 | ~11 ns | 30.5 nm² | ~44° | **No** |
| 5 | R1 | ~10 ns | 28.9 nm² | ~75° | **No** |
| 6 | R3 | ~10 ns | 30.1 nm² | ~56° | **No** |

All 6 events: SASA **28.5–30.5 nm²**, zero frames satisfying activation criterion (SASA ≥ 32.1 nm²)

*The protein sustains 59 ns of interfacial contact — still doesn't commit*

---

<!-- _class: figure-slide -->

# Global Compactness: The Protein Never Unfolds

![](figures/PAPER_FIG3_ACTIVATION.png)

> **Rg = 1.496 ± 0.009 nm** (R1) — no trend · β-barrel RMSD: 0.21–0.24 nm across all replicas · α-helix RMSD ≤ 0.137 nm · **Under 4 µs unbiased dynamics: zero global unfolding events**

---

<!-- _class: figure-slide -->

# Calyx Breathes — Stationary Stochastic Process

![](figures/PAPER_FIG3_ACTIVATION.png)

> **SASA**: 24–37 nm² (PBC-corrected) · Recurring fluctuations every **~30–40 ns** · Not a one-shot pre-adsorption event — calyx exposure is a *continuous, ongoing process*

---

<!-- _class: figure-slide -->

# Interface Shifts Which Loop Dominates

![](figures/PAPER_FIG3_ACTIVATION.png)

<div class="two-col">
<div class="col">

**Bulk (CENTER)**
Loop BC dominant
RMSF max **0.54 nm** (residues 30–35)

</div>
<div class="col">

**Near-AWI (R1)**
Loop CD/EF rises to **0.39 nm** (residues 57–60)
Loop BC falls to **0.25 nm**

</div>
</div>

> Loop CD/EF sits **directly above the hydrophobic calyx** — interface selects calyx-opening motions

---

<!-- _class: figure-slide -->

# SASA Distribution: All Four Replicas

![](figures/Fig4_optionA.png)

> All replicas confined to **24–37 nm²** · p95 = **32.1 nm²** (distribution-based threshold) · No replica reaches a distinct "activated" SASA regime · Distributions are consistent across replicas

---

<!-- _class: figure-slide -->

# Orientation: Uniform and Independent of SASA

![](figures/Fig4_optionA.png)

> **Pearson r = +0.006** · No quadrant clustering — all calyx angles equally populated at any SASA level · Obs/Indep ≈ 1.0 across SASA threshold sweep (27–33 nm²)

---

# Statistical Robustness: Block Bootstrap

**The challenge**: SASA autocorrelation = **232 ns** → i.i.d. assumption breaks down

| Quantity | Value |
|---------|-------|
| Autocorrelation length | **232 ns** (range 81–394 ns per replica) |
| Block bootstrap length | 232 ns |
| Effective N | **≈ 17** independent observations |
| Block bootstrap 95% CI | **[−0.09, +0.11]** |
| Conclusion | Rules out \|r\| > 0.11 at 95% confidence |

<div class="highlight-box">
SASA and calyx orientation are <strong>statistically independent</strong> on the µs timescale
</div>

---

# Scientific Integrity: The PBC Lesson

**What we found during analysis**

| | Before fix | After fix |
|--|-----------|----------|
| Method | freeSASA (no unwrap) | freeSASA + MDAnalysis `mda_unwrap` |
| SASA range | **45–62 nm²** ← artifact | **24–37 nm²** ← corrected |
| Gate-open frames | 21 events | **0 events** |
| 3.3× suppression | Appeared real | Entirely artifact |

- PBC-split atoms inflated SASA across periodic boundaries
- Full disclosure in Methods section of the paper
- **All results in this talk are from PBC-corrected analysis**

---

# What This Means

**Prior models assumed:**
> Contact → immediate unfolding → adsorption (Graham & Phillips)
> OR: brief contacts don't matter

**What we observe:**
- Contact is common; 59 ns contact without commitment — **genuine kinetic bottleneck**, not sampling artefact
- SASA and orientation statistically independent — **no simple two-factor coupling** as commitment trigger
- Global fold preserved — commitment mechanism is *something else*, not global unfolding

<div class="highlight-box">
First characterisation of the <strong>pre-commitment contact ensemble</strong> — the required foundation for designing enhanced-sampling calculations
</div>

---

# Implications for Protein Engineering

**Loop CD/EF: the engineering target**
- Becomes dominant near AWI (interface-induced conformational preference)
- Mutations increasing *calyx flexibility* likely more effective than those increasing bulk hydrophobicity

**Dimer complexity** (BLG dominant dimer at neutral pH, >50 µM)
- *Steric*: dimer interface occludes Loop CD/EF region
- *Kinetic*: must dissociate before calyx can present unobstructed
- *Orientational*: oblate shape alters rotational diffusion and θ distribution

**Lipocalin family baseline**
Quantitative SASA/orientation baseline for comparing BLG mutants and other lipocalins

---

# What's Next

<div class="two-col">
<div class="col">

**Paper 1 pipeline (this work)**
- Zenodo upload → DOI (blocker)
- P.P. sign-off
- Submit to JCIS (IF ~9)

**Paper 2**
β-Casein at AWI
AlphaFold2 structure ready

</div>
<div class="col">

**Enhanced sampling**
Metadynamics / umbrella sampling along (SASA, θ)
SET 1D data = baseline

**BLG dimer**
Full dimer contact ensemble

**TIP4P/2005 cross-check**
Quantitative surface tension correction

</div>
</div>

---

<!-- _class: title-slide -->
<!-- _paginate: false -->

# Summary

**1. Contact without commitment**
613 events across 4 µs — only 6 sustain ≥ 10 ns, **none commits**

**2. Compact globally, loop-mediated locally**
Rg stable, β-barrel intact — Loop CD/EF mediates calyx exposure near AWI

**3. SASA ⊥ orientation on the µs timescale**
r = +0.006, block bootstrap CI [−0.09, +0.11] — rules out |r| > 0.11

---

**4 µs of unbiased MD resolves the pre-commitment contact ensemble.
Commitment requires enhanced sampling to characterise.**

*Thank you — questions?*

*Chalakon Pornjariyawatch · COMFHA, Kasetsart University*
