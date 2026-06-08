# Paper 2 Plan — β-Casein at Air-Water Interface

**Created:** 2026-06-08  
**Protein:** β-Casein (intrinsically disordered, IDP)  
**Input structure:** `inputs_CAS/CASEIN.pdb` (AlphaFold2) + `inputs_CAS/topol.top`  
**Template:** BLG simulation pipeline in `outputs_BLG/CENTER/`

---

## Scientific Context

β-Casein is the counterpart to BLG — disordered where BLG is globular. This changes everything:

| Property | BLG (Paper 1) | β-Casein (Paper 2) |
|---|---|---|
| Structure | Folded β-barrel, Rg ~1.5 nm | Intrinsically disordered (IDP) |
| RMSD behaviour | Flat ~0.24 nm — stable | High, fluctuating — normal |
| AlphaFold confidence | High pLDDT | Low pLDDT — one low-confidence conformation |
| Expected contact | Non-activated, pre-commitment | Likely faster, more flexible adsorption |
| Key analysis | SASA, orientation, contact events | Same + DSSP (secondary structure at interface) |

**Story:** BLG = "contact without commitment" (folded protein can't unfold to adsorb at µs scale). β-Casein = disordered → can it commit? This is the comparison Paper 2 makes.

---

## Phase 0 — Literature Foundation (week of June 8)

**Task L1 — Read & annotate (4 papers, Endnote):**

1. **Dickinson 2001** — "Milk protein interfacial layers and the relationship to emulsion stability"  
   Note: (a) what they measure, (b) what simulation resolves, (c) one number to compare against

2. **Mackie et al. 1999** — "Orogenic displacement of protein from the air/water interface by competitive adsorption"  
   Note: benchmark experiment for β-Casein at AWI

3. **Euston et al. 2013** — MD of β-Casein at oil-water interface  
   Note: closest prior simulation — what did they do differently? What did they NOT measure?

4. **Holt & Sawyer 1993** — β-Casein sequence and structure  
   Note: know the protein. Which regions are hydrophobic? Where are the phosphoserines?

**Task L2 — Know your protein:**
- What does AlphaFold2 give you for a disordered protein?
  Answer: one low-confidence conformation, NOT the ensemble. pLDDT < 70 for most residues.
- What RMSD should we expect? Much higher than BLG's 0.24 nm — this is fine, document it.
- β-Casein has a strongly amphipathic N-terminal region — this likely drives interfacial contact.

---

## Phase 1 — System Design (week of June 15)

**Task S1 — Decide simulation parameters (discuss with Claude before touching cluster):**

| Parameter | BLG choice | β-Casein proposal |
|---|---|---|
| Box geometry | Slab, 15×15×10 nm | Same — discuss |
| Force field | CHARMM36m | CHARMM36m (optimised for IDPs ✓) |
| Water model | TIP3P | TIP3P |
| Simulation length | 1 µs × 4 replicas | TBD — 1 µs × 3? |
| Starting orientation | Random | TBD — discuss with P.P. |
| NPT equilibration | SKIPPED (slab geometry) | Same rule applies |

**Task S2 — Study BLG mdp files before writing β-Casein inputs:**
```bash
cat ~/Workspace/MILK_FROTHING/mdp/minim.mdp    # energy minimisation
cat ~/Workspace/MILK_FROTHING/mdp/nvt_slab.mdp # NVT equilibration for slab
cat ~/Workspace/MILK_FROTHING/mdp/md.mdp        # production
```
Before we write a single β-Casein mdp, explain each parameter in your own words.
Key ones to understand: `integrator`, `nsteps`, `dt`, `tcoupl`, `pcoupl`, `constraints`, `ewald-rtol`.

---

## Phase 2 — System Preparation (GROMACS, step by step)

Work through each step together. Do NOT proceed to the next step without verifying the output.

1. **`pdb2gmx`** — apply CHARMM36m to `inputs_CAS/CASEIN.pdb`
   - Check: correct number of atoms? Any missing residues?

2. **`editconf`** — build slab simulation box (same geometry as BLG)

3. **`solvate`** — fill box with TIP3P water

4. **`genion`** — add Na⁺/Cl⁻ to 150 mM ionic strength (physiological)

5. **`grompp` + `mdrun` (EM)** — energy minimisation
   - Check: Fmax < 1000 kJ/mol/nm before proceeding

6. **`grompp` + `mdrun` (NVT)** — slab equilibration (skip NPT — same rule as BLG)

7. **Production mdp** — write together, you explain each parameter before I finalize

8. **SLURM script** — you understand every line before we `sbatch`

---

## Phase 3 — Production & Analysis

**Analysis pipeline (extends BLG pipeline):**
- RMSD/RMSF — expect higher values; not a problem for IDP
- Contact analysis — same `detect_adsorption_contact.py` logic, compare to BLG 613 events
- SASA — same `gate_analysis_all_replicas.py` + `mda_unwrap` (non-negotiable)
- **New: DSSP (secondary structure)** — does β-Casein form transient secondary structure at interface?
- **New: hydrophobic patch tracking** — N-terminal region residues 1–25

**Key questions to answer:**
1. Does β-Casein contact the interface more readily than BLG?
2. Does disorder enable faster commitment (irreversible adsorption)?
3. What structural changes accompany contact events?

---

## Immediate Next Steps (June 8)

- [ ] Read Task L1 papers 1 & 2 (Dickinson 2001 + Mackie 1999)
- [ ] Read Task S2 mdp files — be able to explain each parameter
- [ ] Come back and discuss system design decisions (Task S1) before touching cluster
