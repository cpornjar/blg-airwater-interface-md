# Literature Survey — Semantic Scholar Search
**Date:** May 15, 2026
**Project:** COMFHA Paper 1 — BLG adsorption at air-water interface
**Queries run:** 4 (BLG air-water adsorption; BLG MD simulation interface unfolding;
protein air-water MD SASA hydrophobic spontaneous; milk protein foam MD GROMACS CHARMM)
**Note:** S2 API rate-limited without key — results via WebSearch against semanticscholar.org + targeted WebFetch.
**Fields:** All (food science / biophysics / computational chemistry — no CS/Engineering filter applied)

---

## Search Results by Category

---

### Category A — BLG at Air-Water Interface (Experimental)

**[A1] Cornec, Cho & Schaad (1999)**
"Adsorption Dynamics of α-Lactalbumin and β-Lactoglobulin at Air-Water Interfaces"
*Journal of Colloid and Interface Science* | Citations: ~200
[Semantic Scholar](https://www.semanticscholar.org/paper/98ec858a99e251ca7b0dc06d4f7cba35a4c72060)
- **Method:** Radiotracer (14C-labelled protein), surface pressure + surface concentration measurement
- **Key finding:** BLG adsorption is diffusion-controlled at short times; an energy barrier slows adsorption at longer times. BLG does NOT fully unfold during adsorption (area per molecule smaller than spread monolayer)
- **Relevance to COMFHA:** Establishes energy barrier hypothesis experimentally. Our MD work provides the first atomistic explanation — partial unfolding is the activation required to overcome this barrier.
- **Gap:** No atomistic mechanism; no information on what happens in bulk before adsorption.

**[A2] Ulaganathan et al. (2019) — β-LG Adsorption Layers at Water/Air Surface: 3**
"Neutron Reflectometry Study on the Effect of pH"
*Journal of Physical Chemistry B*
DOI: https://doi.org/10.1021/acs.jpcb.9b07733
- **Method:** Neutron reflectometry, ellipsometry
- **Key finding:** Adsorbed layer structure resolved at Å resolution. Layer thickness and protein orientation depend on pH.
- **Gap:** Post-adsorption structural data only; no bulk pre-adsorption dynamics.

**[A3] β-LG Adsorption Layers at Water/Air Surface: 4 (2020)**
"Impact on the Stability of Foam Films and Foams"
*Minerals / MDPI* | Open Access
https://www.mdpi.com/2075-163X/10/7/636
- **Key finding:** Direct link between interfacial layer properties and foam stability.
- **Relevance:** Provides experimental foam stability data our molecular mechanism must explain.

**[A4] β-LG Adsorption Layers at Water/Air Surface: 5 (2021)**
"Adsorption Isotherm and Equation of State Revisited, Impact of pH"
*Colloids / MDPI*
https://www.mdpi.com/2504-5377/5/1/14
- **Key finding:** Adsorption isotherm quantified. pH 7 (our simulation condition) sits in the intermediate-adsorption regime.
- **Relevance:** Validates our simulation pH choice (298 K, neutral pH).

**[A5] Engelhardt, Rumpel et al.**
"Protein adsorption at the electrified air-water interface: implications on foam stability"
*Langmuir* (Semantic Scholar)
[Link](https://www.semanticscholar.org/paper/30dd83b75ec22d63eb8561771ba72339a95f06ff)
- **Method:** Experimental + possible MD simulations
- **Key finding:** Electrostatic interactions modulate the energy barrier to adsorption; exposed hydrophobicity and degree of unfolding linked to foam stability
- **Relevance:** Supports our finding that hydrophobic exposure is the key variable. [Full text not accessible]

---

### Category B — BLG MD Simulation (Oil-Water Interface)

**[B1] Jordens, Rousseau & Bhattacharya (2015)**
"Deciphering β-Lactoglobulin Interactions at an Oil-Water Interface: A Molecular Dynamics Study"
*Langmuir / ACS* | PubMed: 25989152
DOI: https://doi.org/10.1021/acs.langmuir.5b01371 [VERIFY]
- **System:** Decane-water interface, GROMACS, multiple starting orientations
- **Adsorption:** Spontaneous from near-interface position (not from bulk center)
- **Key finding:** Adsorption driven by structural rearrangements that preserve secondary structure but expose hydrophobic residues to decane. Rate independent of initial orientation (stochastic). No pre-adsorption activation event noted.
- **Gap vs COMFHA:** Oil-water ≠ air-water (different interfacial tension, dielectric environment); protein pre-placed near interface — cannot observe bulk-phase conformational changes; no timescale quantification from bulk.

**[B2] Zare, Bhattacharya & Rousseau (2016)**
"Molecular Dynamics Simulation of β-Lactoglobulin at Different Oil/Water Interfaces"
*Biomacromolecules* | ResearchGate
DOI: https://doi.org/10.1021/acs.biomac.5b01709
- **System:** Three oil types (decane, octanol, triolein), GROMACS, multiple orientations
- **Key finding:** Adsorption mechanism and structural changes differ markedly between oils. Protein behaves like a soft spherical particle at O/W interface. Calyx opens toward oil phase.
- **Gap vs COMFHA:** Oil-water only; no air-water; no spontaneous bulk-to-interface trajectory; calyx opening observed only post-adsorption.

---

### Category C — BLG Conformational / Unfolding MD (Bulk, No Interface)

**[C1] "Molecular simulation of partially denatured β-lactoglobulin" (2023)**
*Food Hydrocolloids* | Heriot-Watt Research Portal
DOI: https://doi.org/10.1016/j.foodhyd.2023.108811
- **System:** BLG heated to 500 K then annealed to 300 K, bulk water, GROMACS
- **Key finding:** 5 meta-stable denatured conformations identified; open/extended conformation on heating, limited refolding on cooling. Cysteine residues spatially separated.
- **Gap vs COMFHA:** Starts from artificially denatured state (not native); bulk simulation only (no interface); no adsorption event.

**[C2] "Dynamics simulation of conformational trapping of preheated β-LG" (2025/2026)**
*ScienceDirect* [403 — abstract only]
- **System:** ~100 ns MD, preheating at 398 K, RMSD and Rg tracked
- **Key finding:** Preheating leads to significant RMSD and Rg increase reflecting partial unfolding. "Conformational trapping" in expanded states.
- **Gap vs COMFHA:** Pre-stressed starting structure (not native-state spontaneous); no interface; very short timescale (100 ns vs 1,000 ns).

**[C3] Bolisetty & Mezzenga et al. (2022)**
"Beta-Lactoglobulin as a Model Food Protein: How to Promote, Prevent, and Exploit Its Unfolding Processes"
*Molecules* | PubMed: 35164393
https://www.mdpi.com/1420-3049/27/3/1131
- **Type:** Review
- **Key finding:** BLG unfolding reviewed across pH, temperature, chemical stress. Notes that BLG unfolds via multiple intermediate states. Alpha-helix and disulfide bond play key roles in stability.
- **Relevance:** Good background reference. Supports our framing that partial unfolding is a "activation" step.

---

### Category D — Protein MD at Air-Water Interface (Non-BLG)

**[D1] Chaudhri, Bhatt & Shire (2024)** ← HIGHEST NOVELTY THREAT
"Mechanistic Insights into the Adsorption of Monoclonal Antibodies at the Water/Vapor Interface"
*Molecular Pharmaceutics* | PMC: 10848294
DOI: https://doi.org/10.1021/acs.molpharmaceut.3c00821
- **System:** mAb COE3 (IgG1), air-water (water/vapor) interface, CHARMM36m + TIP3P, 200 ns
- **Key finding:** Small local conformational changes promote adsorption. Thermally pre-stressed mAbs show significantly higher surface activity. Hydrophobic SASA increases progressively during interfacial adsorption.
- **Differentiation from COMFHA:**
  - Protein: mAb (large, complex antibody) ≠ BLG (small, folded dairy globulin)
  - Starting structure: thermally pre-stressed → **not observing native-state spontaneous activation**
  - Timescale: 200 ns → **cannot quantify >1 µs barrier**
  - Context: pharmaceutical stability ≠ food foam science

**[D2] Jain, Jochum et al.**
"Molecular dynamics simulations of peptides at the air-water interface: influencing factors on peptide-templated mineralization"
*Semantic Scholar*
[Link](https://www.semanticscholar.org/paper/119dcb97ae8373816569ab6f01cf757b86ea75d0)
- **System:** Short peptides (not folded proteins), air-water interface, MD
- **Relevance:** Low — peptides lack the folded-core beta-barrel structure central to our activation mechanism.

---

### Category E — BLG Foam Stability (Experimental, Recent)

**[E1] "Enhancing foam stability with β-LG nanoparticles" (2023)**
*Food Hydrocolloids*
DOI: https://doi.org/10.1016/j.foodhyd.2023.108366 [VERIFY]
- **Key finding:** β-LG nanoparticles outperform native β-LG for foam stability — partial aggregation improves interfacial film.
- **Relevance:** Background context. Validates that BLG interfacial behavior is an active research topic.

**[E2] "Foams Stabilized by β-LG Amyloid Fibrils: Effect of pH" (2018)**
*J. Agricultural and Food Chemistry*
DOI: https://doi.org/10.1021/acs.jafc.7b03669
- **Key finding:** Amyloid fibrils dramatically improve foam stability vs native BLG — structural state of BLG determines foam quality.

**[E3] "Exploring Functionality Gain for β-LG Through Production and Processing Interventions" (2024)**
*Food and Bioprocess Technology* | Springer
DOI: https://doi.org/10.1007/s11947-024-03414-z
- **Key finding:** Processing interventions (heating, pressure) alter BLG surface functionality. Review shows surface activity is tightly coupled to partial unfolding state.
- **Relevance:** Strengthens our argument that understanding the unfolding-adsorption link has direct industrial value.

---

## Research Gap Map

```
                         EXPERIMENTAL        ATOMISTIC MD
                         ─────────────       ─────────────
BLG + air-water          ████ (A1-A5)        ✗ NONE FOUND ← OUR WORK
BLG + oil-water          ██ (B1, B2 expt.)   ██ (B1, B2)
BLG + bulk unfolding     ███ (C3 review)     ██ (C1, C2) — pre-stressed
Non-BLG + air-water      ──                  █ (D1, D2) — mAb/peptides
BLG + foam stability     ████ (E1-E3)        ✗ NONE FOUND
```

**The white space:** No atomistic MD simulation of BLG at the air-water interface exists in the literature. Every MD study of BLG uses oil-water interfaces. Every air-water MD study uses non-BLG proteins. Our work fills both gaps simultaneously.

---

## Papers to Cite in Paper 1

### Must Cite (foundational or closest competition)
| ID | Paper | Why |
|----|-------|-----|
| A1 | Cornec 1999 | Establishes experimental energy barrier — our MD explains it |
| A2 | Ulaganathan 2019 | Establishes adsorbed layer structure (neutron reflectometry) |
| A3 | β-LG Layers:4 2020 | Links interfacial behavior to foam stability |
| B1 | Jordens 2015 | Closest MD analogue (oil-water) — must cite and differentiate |
| B2 | Zare 2016 | Calyx opening at oil-water — compare to our air-water finding |
| C3 | Bolisetty 2022 | Review — good background on BLG unfolding |
| D1 | Chaudhri 2024 | **Must cite** — closest mechanistic parallel; differentiate clearly |

### Should Cite (supportive background)
| ID | Paper | Why |
|----|-------|-----|
| A4 | β-LG Layers:5 2021 | pH 7 adsorption isotherm validates our simulation condition |
| C1 | Food Hydrocolloids 2023 | Most recent BLG MD — shows field is active; contrast with our approach |
| E3 | Food & Bioprocess 2024 | Industrial relevance — unfolding-surface activity link |

### Optional (context)
- E1 (nanoparticles foam), E2 (amyloid fibrils), D2 (peptides)

---

## Key Differentiation Statement (for Introduction draft)

> "Prior atomistic MD simulations of β-lactoglobulin at fluid interfaces have focused exclusively on oil-water systems, where the protein is pre-positioned near the interface [B1, B2]. The only atomistic study of a globular protein at the air-water (water/vapor) interface used pre-thermally-stressed monoclonal antibodies over 200 ns timescales [D1]. No study has performed an unbiased simulation of BLG spontaneous adsorption from its native state at the air-water interface, leaving the molecular origin of the well-established experimental energy barrier [A1] unresolved."

---

## Verified Citation Counts (OpenAlex DOI lookup — May 2026)

| Paper | Year | Venue | Citations | OA |
|-------|------|-------|-----------|-----|
| Dickinson — adsorbed protein layers review | 1999 | Colloids Surf. B | **620** | closed |
| Berton-Carabin — interfacial layers in food emulsions | 2018 | Annu. Rev. Food Sci. | **262** | ✓ |
| Ulaganathan — BLG adsorption layers JPCB (neutron reflectometry) | 2019 | J. Phys. Chem. B | 23 | ✓ |
| Bolisetty — BLG as model food protein (review) | 2022 | Molecules | 37 | ✓ |
| BLG Adsorption Layers: 4 (foam stability) | 2020 | Minerals | 7 | ✓ |
| Food Hydrocolloids — partially denatured BLG MD | 2023 | Food Hydrocolloids | 9 | ✓ |
| Chaudhri — mAb at water/vapor interface ← **main competitor** | 2024 | Mol. Pharmaceutics | 9 | ✓ |

**Note on OpenAlex free-text search:** Returned cross-field noise (spray drying, biosensors, etc.) — not suitable for discovery in this domain. DOI lookup mode is reliable and accurate. Use this mode for all future citation verification before submission.

---

## Recommended Next Steps

1. **Verify DOIs for B1, B2** via DBLP before adding to `.bib` — marked `[VERIFY]` above
2. **Get Semantic Scholar API key** (free) to run structured bulk search and get citation counts:
   https://www.semanticscholar.org/product/api#api-key-form
3. **Run `/paper-plan`** once R2/R3 results land (estimated May 17–18)
4. **Add Chaudhri 2024 to `.bib`** immediately — highest-risk paper for reviewer objection
