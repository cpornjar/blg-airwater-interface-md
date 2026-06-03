# BLG at the Air-Water Interface — Plain Language Summary
*COMFHA Lab, Kasetsart University | Chalakon Pornjariyawatch & Prapasiri Pongprayoon*

---

## What is this research about?

Milk foam — the froth on a cappuccino or whipped cream — is stabilised by proteins from milk. The most important of these is **β-Lactoglobulin (BLG)**, the dominant whey protein in bovine milk. BLG acts as a molecular "foam stabiliser": it travels from the bulk liquid to the air-water interface and forms a thin, elastic film that keeps bubbles from collapsing.

The puzzle is: **this process is known to be slow** (it takes seconds to minutes in experiments), even though BLG is small, soluble, and surface-active. Nobody knew *why* at the molecular level.

---

## What did we do?

We ran the **first atomistic molecular dynamics (MD) simulation of native BLG at the air-water interface** — meaning we tracked every single atom of the protein and water molecules over a combined 4 microseconds (4,000 nanoseconds) of simulated time.

**Setup:**
- 4 independent simulation "replicas" (trajectories), each 1000 ns long
- A realistic water slab (12 × 12 × 35 nm box) with air on both sides
- CHARMM36m protein force field + TIP3P water (standard, validated models)
- Kasetsart University HPC cluster (GPU nodes)

---

## The key discovery: Contact vs. Commitment

Previous studies measured adsorption using the **centre-of-mass distance** between the protein and the interface. This is like measuring whether a basketball player is "near the basket" — it misses all the actual hand contacts.

We instead measured the **nearest single atom** of the protein to the interface. This revealed something completely invisible with the old method:

> **BLG touches the air-water interface 613 times across 4 µs — but almost never stays.**

- 613 discrete contact events detected
- 607 of 613 end within 10 nanoseconds (the protein touches and bounces back)
- Only **6 events** sustain contact longer than 10 ns
- **None of the 6 commits to stable adsorption**

This is the **contact/commitment dichotomy**: contact is common and fast; commitment is rare and never observed in unbiased simulation.

---

## Why doesn't the protein stay? What we found about the calyx

BLG has a hydrophobic pocket called the **calyx** — a barrel-shaped cavity that normally binds fatty acids and hydrophobic ligands. The calyx is the obvious candidate for driving adsorption: hydrophobic surfaces are attracted to the air-water interface.

We measured two things about the calyx during contact:

1. **SASA** (Solvent Accessible Surface Area) — how much of the calyx is exposed to water. Higher SASA = more exposed = more "ready" for adsorption. Corrected for simulation artefacts (see below), the calyx SASA stays in the range **24–37 nm²** throughout all simulations.

2. **Orientation angle θ** — whether the calyx is pointing toward the interface (θ near 0°) or away (θ near 180°).

**The key result:** SASA and orientation are **statistically independent** of each other (Pearson r = +0.006; block bootstrap 95% CI [−0.09, +0.11]; rules out |r| > 0.11). And neither one is higher during long-contact events than during ordinary transient contacts.

**What this means:** Even when the protein is sitting at the interface for tens of nanoseconds, its calyx is not more exposed and not better oriented than average. The step that converts contact into commitment is not captured by these two coordinates — and is not sampled at all in 4 µs of unbiased simulation.

---

## An important correction we made (transparency)

Early in the project, a **periodic boundary condition (PBC) artefact** was discovered in our SASA calculations. The software we used (freeSASA) was not PBC-aware, meaning it sometimes split the protein across the simulation box boundaries and calculated a falsely inflated SASA.

**Old (wrong) values:** SASA peaks of 45–62 nm²  
**Corrected values:** SASA confined to 24–37 nm², zero gate-open events

We corrected this fully (using MDAnalysis `unwrap` transformation) and re-analysed all data. The entire paper is based on the corrected analysis.

---

## What does the protein do structurally?

Even though the protein never commits, its structural dynamics near the interface are interesting:

- **Globally compact**: Radius of gyration = 1.496 ± 0.009 nm, stable throughout. The protein **never globally unfolds** in preparation for adsorption — contradicting the classical "surface denaturation" hypothesis (Graham & Phillips 1979).

- **Loop shift**: In bulk solution, Loop BC (residues 30–35) is the most flexible part of the protein. Near the interface, the dominant flexible loop shifts to **Loop CD/EF (residues 57–60)** — the loop that sits directly above the hydrophobic calyx. This interface-induced shift suggests proximity to the air-water surface selects for calyx-opening motions.

- **Patch RMSD**: The hydrophobic patch residues themselves don't drift — they explore a structurally defined neighbourhood (RMSD ~0.24 nm) without progressive opening.

---

## What does this paper contribute?

1. **First atomistic MD of native BLG at the air-water interface** on µs timescales
2. **Resolution of the contact/commitment distinction**: 613 events contact; 6 linger; 0 commit — all from single-atom distance measurement that CoM distance misses entirely
3. **Quantitative characterisation of the pre-commitment contact ensemble**: calyx SASA 24–37 nm², orientation uniform and independent of SASA, loop CD/EF becomes dominant near interface

The paper is honest about its boundary: the molecular mechanism of commitment (what actually drives the transition from transient contact to stable adsorption) is **not resolved** by unbiased simulation. Enhanced sampling methods (metadynamics, REST2) are needed to cross that barrier — and this work defines exactly what baseline they need to improve on.

---

## What comes next?

- **Paper 2**: β-Casein at the air-water interface (AlphaFold2 structure, already in preparation)
- **Paper 3**: Calcium bridge effects (BLG + β-Casein + Ca²⁺)
- **Paper 4**: Fat interaction (triglycerides, free fatty acids)
- **Enhanced sampling**: Metadynamics along (SASA, θ) to resolve the commitment free energy barrier

---

## Glossary

| Term | Meaning |
|------|---------|
| MD simulation | Molecular dynamics — simulating atom motion using Newton's laws |
| Atomistic | Every atom explicitly represented (vs. coarse-grained models) |
| SASA | Solvent Accessible Surface Area — how much surface is exposed to water |
| Calyx | The hydrophobic barrel pocket of BLG that binds fatty acids |
| PBC | Periodic Boundary Condition — the simulation box repeats infinitely; needs careful handling |
| CHARMM36m | A standard force field (set of interaction parameters) for proteins |
| RMSF | Root Mean Square Fluctuation — how much a residue wiggles over time |
| Rg | Radius of gyration — measure of overall protein compactness |
| TIP3P | A widely used 3-site water model |
| µs | Microsecond (10⁻⁶ seconds) — very long for atomistic MD |

---

## Current Status (June 3, 2026)

**Paper 1 is READY for submission to JCIS.**

- Auto-review Round 12: **10/10 READY** (Gemini 2.5 Flash) ✓
- Citation audit complete (June 2): 42 entries verified, 2 wrong-context citations corrected, TIP3P surface tension fixed ("one-third" → "half", i.e. ~36 mN/m not ~50 mN/m)
- LaTeX: clean compile, 19 pages, zero warnings
- Presentation: 15-slide deck finalised (COMFHA_Talk_May2026/presentation_final.key)

**Remaining before submission:**
1. P.P. co-author review (sign-off on title, SET 1D removal, scope claim framing)
2. Zenodo upload → get DOI → replace placeholder in main.tex Data Availability section
3. JCIS submission at editorialmanager.com/jcis
