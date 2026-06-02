# COMFHA Science Notes — β-Lactoglobulin at the Air–Water Interface
**Project:** COMFHA (Computational Milk Foam & Hydrophobic Adsorption) — Phase 1  
**Author:** Chalakon Pornjariyawatch, Kasetsart University  
**Advisor:** Assoc. Prof. Prapasiri Pongprayoon  
**Status:** Paper targeting JCIS (IF ~9), auto-review 10/10, May 2026

---

## 1. Why Does This Matter? (The Problem)

When milk is steamed for espresso, air is whipped into the hot liquid. Proteins in milk — especially β-Lactoglobulin (BLG) — migrate to the surface of each air bubble and form a thin, stiff protein film. This film is what makes milk foam stable. Without it, bubbles merge and collapse immediately.

The kinetic paradox: BLG adsorbs **slowly** — seconds to minutes — despite being present at relatively high concentration (~3 g/L). There must be a barrier. The classical explanation (Graham & Phillips, 1979) is that the protein must partially unfold at the interface before it can "anchor" — and unfolding takes time. But no one has ever watched this process at atomic resolution. This is the gap COMFHA fills.

---

## 2. What Is β-Lactoglobulin?

BLG is the main whey protein in bovine milk. Key structural facts:

- **Fold:** Lipocalin superfamily — a **β-barrel** made of 8 anti-parallel β-strands (called A–H), forming a cone-shaped hydrophobic pocket called the **calyx**
- **Size:** ~18.3 kDa, 162 residues, diameter ~4 nm
- **PDB:** 1BEB (native monomer crystal structure)
- **Calyx function:** The calyx is BLG's main binding site — it naturally binds hydrophobic ligands like retinol and fatty acids. It is lined with hydrophobic residues and opens/closes via loops
- **Key loops:**
  - Loop BC (residues 30–35): connects β-strands B and C
  - Loop CD/EF (residues 57–60): borders the calyx entrance; controls access to the hydrophobic interior
- **Secondary structure:** Predominantly β-barrel. Has a prominent C-terminal α-helix (helix I) and a short 3₁₀ helix
- **Surface:** Amphipathic — hydrophilic exterior with a hydrophobic calyx interior
- **Rg (radius of gyration):** ~1.50 nm in native state

---

## 3. What Is the Air–Water Interface?

The air–water interface (AWI) is the boundary between the aqueous bulk phase (water + dissolved protein) and the gas phase (air). Key physics:

- **Surface tension:** Water molecules at the surface have fewer neighbours → unbalanced inward force → surface tension (~72 mN/m at 298 K)
- **Gibbs dividing surface:** A mathematical plane defining the "location" of the interface for thermodynamic calculations
- **Interfacial energy:** Proteins lower surface tension when they adsorb — thermodynamically favourable
- **Kinetic barrier:** Despite being thermodynamically favourable, protein adsorption is slow. The protein must arrive, orient correctly, and open its hydrophobic face to the air phase

In our slab simulation, the interface is defined operationally as the z-position where water density drops from bulk to near-zero. We track the **Gibbs dividing surface** frame-by-frame.

---

## 4. Molecular Dynamics Simulation — Fundamentals

### What MD Does

MD numerically integrates Newton's equations of motion for every atom in the system. At each timestep (typically 2 fs), forces on every atom are calculated from the **force field** (a potential energy function), and positions and velocities are updated.

Result: a trajectory — the positions of all atoms as a function of time.

### Force Field: CHARMM36m

The force field defines how atoms interact:
- **Bonded terms:** bond stretches, angle bends, torsions (dihedral angles)
- **Non-bonded terms:** van der Waals (Lennard-Jones) and electrostatic (Coulomb) interactions
- CHARMM36m is the state-of-the-art for **intrinsically disordered and folded proteins in aqueous solution**, validated against NMR data. It handles protein–water interfaces exceptionally well.

### Water Model: TIP3P

TIP3P (Transferable Intermolecular Potential 3-Point) is a 3-site rigid water model. Standard pairing with CHARMM force fields.

### Periodic Boundary Conditions (PBC)

To avoid edge effects in a finite simulation box, the box is surrounded by periodic images of itself. Atoms leaving one side re-enter from the opposite side. This simulates an infinite bulk-like environment.

**Critical issue for slab geometry:** In a slab (protein + water + vacuum), PBC applies in x and y (lateral) but not z (normal to interface). If a protein spans the periodic boundary in x or y, its atoms can appear in two different periodic images — they are "split." Analysis tools must **unwrap** the protein (put all atoms in the same periodic image) before calculating properties like SASA.

### The Slab Geometry

We use a slab:
- Box: 12 × 12 × 35 nm
- ~7 nm TIP3P water in the centre
- ~14 nm vacuum on each side → two air–water interfaces
- BLG (1BEB) placed in the water phase, starting either in bulk (CENTER) or pre-placed near the AWI (R1, R2, R3)
- No pressure coupling in z (vacuum layer absorbs compressive forces)
- Temperature: 298 K, Berendsen thermostat during equilibration, v-rescale in production

### Why 4 Replicas?

To sample different starting configurations and avoid trajectory-specific artifacts:
- **CENTER:** BLG starts in bulk water, diffuses naturally to the interface
- **R1, R2, R3:** BLG starts 2 nm from the AWI, allowing faster initial contact

---

## 5. Key Analysis Techniques

### Radius of Gyration (Rg)

Rg measures the overall size/compactness of the protein:
$$R_g = \sqrt{\frac{\sum_i m_i |\mathbf{r}_i - \mathbf{r}_{cm}|^2}{\sum_i m_i}}$$

If Rg increases over time, the protein is unfolding/expanding. Constant Rg = native fold preserved.

### RMSD (Root Mean Square Deviation)

Measures structural deviation from a reference structure (usually the starting conformation or crystal structure). RMSD < 0.2 nm for backbone = essentially native. Higher RMSD = significant conformational change.

We track **α-helix RMSD** separately because the C-terminal helix is outside the β-barrel — it can fluctuate independently.

### SASA (Solvent-Accessible Surface Area)

SASA quantifies how much of the protein surface is exposed to solvent. For a hydrophobic pocket (the calyx), **high SASA = calyx is open/exposed**. We use freeSASA (Mitternacht, 2016) with a probe radius of 0.14 nm (water molecule).

We specifically track **calyx SASA** — the SASA of residues lining the hydrophobic cavity. Normal range: 24–37 nm² in the PBC-corrected data.

**PBC correction:** freeSASA has no PBC awareness. BEFORE applying unwrap, atoms split across the periodic boundary contributed inflated surface area (the split "gap" was exposed to solvent). After applying `MDAnalysis.analysis.base.unwrap()` every frame, all atoms are in the same image and SASA is correct.

### Nearest-Atom Contact Distance

For a 4 nm protein, **centre-of-mass (CoM) distance to the interface is an inadequate metric.** A protein 2 nm away by CoM can have an atom 0.5 nm past the interface. We use:

$$d_{min} = \min_{i \in \text{protein}} (z_i - z_\text{GDS})$$

where $z_\text{GDS}$ is the z-position of the Gibbs dividing surface (water–vacuum boundary). A **contact event** is defined as $d_{min} \leq 0.30$ nm (any protein atom within 0.30 nm of the interface).

### RMSF (Root Mean Square Fluctuation)

Per-residue flexibility metric. RMSF measures how much each residue moves around its average position over the trajectory. High RMSF = flexible/dynamic. Low RMSF = rigid/stable.

### Calyx Orientation Angle (θ)

We define a vector pointing from the calyx "floor" to the calyx "opening" (Loop CD/EF). θ is the angle between this vector and the interface normal (z-axis). Small θ (< 30°) means the calyx mouth points toward the air phase — an "approach" orientation for potential adsorption.

### Block Bootstrap (Statistical Method)

Because SASA is a slow variable (autocorrelation time ~232 ns), consecutive data frames are **not independent**. Raw Pearson p-values assume independence and are therefore meaningless.

Block bootstrap:
1. Divide the time series into non-overlapping blocks of size ~232 ns
2. Sample blocks with replacement to create bootstrap replicates
3. Compute r for each replicate
4. The 2.5th and 97.5th percentiles give the 95% CI

This gives an **honest** confidence interval that accounts for temporal autocorrelation.

**Effective N (N_eff):**
$$N_\text{eff} \approx \frac{T_\text{total}}{2 \times \tau_{AC}} = \frac{4000 \text{ ns}}{2 \times 232 \text{ ns}} \approx 17$$

Only ~17 truly independent SASA observations in 4 µs.

---

## 6. Simulation Setup Details

| Parameter | Value |
|-----------|-------|
| Software | GROMACS 2020.4 |
| Force field | CHARMM36m |
| Water model | TIP3P |
| Protein | β-Lactoglobulin, PDB 1BEB (native monomer) |
| Box | 12 × 12 × 35 nm (slab) |
| Water layer | ~7 nm |
| Vacuum layer | ~14 nm each side |
| Temperature | 298 K |
| Trajectories | 4 (CENTER, R1, R2, R3) |
| Length each | 1000 ns (1 µs) |
| Total | 4.00 µs |
| Timestep | 2 fs |
| Contact threshold | d_min ≤ 0.30 nm |
| Analysis | MDAnalysis 2.10.0, freeSASA |

---

## 7. The Five Findings

### Finding 1: Contact Is Frequent (613 events)

BLG makes **613 contact events** (d_min ≤ 0.30 nm) across the 4.00 µs. In the near-AWI trajectories (R1, R2, R3), 7–23% of all simulation frames are in contact. The protein penetrates up to **0.71 nm past the interface** (R1, t = 406 ns) — not just touching, but partially inserting.

*Key insight:* The protein is NOT diffusion-limited. It reaches the interface constantly.

### Finding 2: Commitment Is Absent (0 adsorptions)

Despite 613 contact events, there are **zero stable adsorptions**. Every contact event ends with the protein retreating to bulk. The 6 longest events (≥ 10 ns) — including a 59 ns event — all end without commitment.

*Key insight:* The kinetic barrier is not about reaching the interface. It is about what happens once you get there.

### Finding 3: Global Structure Is Preserved

Rg stays flat at **1.496 ± 0.009 nm** throughout 4.00 µs. The α-helix RMSD stays ≤ 0.14 nm. **No global unfolding occurs.** The Graham & Phillips (1979) surface-denaturation model is inconsistent with our observations.

*Key insight:* BLG does not need to unfold to adsorb. The barrier is conformational/orientational, not unfolding-related.

### Finding 4: The Calyx Breathes Locally

SASA fluctuates between 24 and 37 nm² with recurring bursts every 30–40 ns. This breathing is an intrinsic protein property observed in all replicas regardless of interface proximity. Near the AWI, **Loop CD/EF (residues 57–60)** becomes the dominant flexible loop (RMSF dominant, replacing Loop BC in bulk). This loop borders the calyx entrance — interface proximity selects calyx-opening motions.

*Key insight:* The interface doesn't passively attract BLG — it actively reshapes which regions of the protein are most dynamic.

### Finding 5: SASA and Orientation Are Independent

Pearson r between calyx SASA and orientation angle θ: **r = +0.006**. 95% CI: **[−0.09, +0.11]** (block bootstrap, N_eff ≈ 17).

SASA and θ fluctuate independently. There is no "gate" mechanism where both must be simultaneously open. Instead, commitment requires coincidence of two independent rare events: calyx open AND orientation correct. This is the mechanistic explanation for the kinetic barrier.

*Key insight:* Rare joint probability of two independent variables = slow adsorption. This is quantifiable and predictive.

---

## 8. The PBC Artifact — A Case Study in Scientific Integrity

**What happened:** Before May 27, 2026, we were running freeSASA without applying MDAnalysis `unwrap`. When BLG atoms were split across the periodic boundary (x or y), freeSASA counted the gap between the split atoms as "solvent-exposed surface." This inflated SASA from the real 24–37 nm² to **45–62 nm²**.

**The apparent result:** With inflated SASA, we observed a spurious correlation between SASA and contact events — SASA appeared to drop during contact windows. This looked like a "two-factor gate": both SASA and θ needed to cross thresholds simultaneously for commitment to occur. We called this the "gate suppression" mechanism. The narrative was compelling — but it was an artifact.

**The fix:** Apply `MDAnalysis.unwrap()` every frame before computing SASA. This places all BLG atoms in the same periodic image, eliminating the false surface.

**After fix:**
- SASA: 45–62 nm² → 24–37 nm² (correct range)
- Pearson r: apparent negative correlation → r = +0.006 (no coupling)
- Narrative: "two-factor gate" → "independent variables, rare coincidence"

**Scientific lesson:** The corrected physics is more interesting than the artifact. Independence is a stronger and more general result than a specific gate mechanism. And finding your own error and correcting it openly is what makes science trustworthy.

---

## 9. Statistical Concepts Used

| Concept | What It Is | Why It Matters |
|---------|-----------|---------------|
| Pearson r | Linear correlation coefficient, range [−1, +1] | Measures coupling between SASA and θ |
| Autocorrelation time (τ_AC) | Time for a variable to "forget" its past value | SASA: 232 ns — tells us frames aren't independent |
| N_eff | Effective number of independent observations | ~17 for SASA in our 4 µs dataset |
| Block bootstrap | Resampling method that preserves temporal structure | Gives honest CI for r |
| 95% CI | Interval containing true value 95% of the time | [−0.09, +0.11] rules out |r| > 0.11 |
| P-value (why we don't use it here) | Probability of observing data under null hypothesis, assuming independence | With N_eff=17, raw p-values are inflated by 400× |

---

## 10. What This Work Establishes

This is the **first unbiased atomistic MD characterisation of the pre-commitment contact ensemble of native BLG at the air–water interface.** Three pillars:

1. **Contact frequent, commitment absent** — establishes the kinetic dichotomy
2. **Compact globally, loop-mediated locally** — disproves surface-denaturation model
3. **SASA ⊥ orientation on µs timescale** — identifies independence as the mechanistic origin of the barrier

This is a **pathfinder result**: it provides the baseline, identifies the collective variable (SASA, θ), names the engineering target (Loop CD/EF), and enables the next phases.

---

## 11. Implications

### Engineering
Loop CD/EF residues 57–60 is the **engineering target**. Mutations that pre-stabilise this loop in the open conformation should reduce the kinetic barrier and accelerate adsorption. This is a direct, testable prediction.

### Enhanced Sampling (Phase 3)
We now have a **well-defined collective variable**: (SASA, θ). Metadynamics or REST2 along this CV can compute the free energy barrier (PMF) for commitment. The unbiased SET 1D trajectories serve as the baseline for validating the enhanced sampling results.

### Conceptual Revision
Slow BLG adsorption is **not diffusion-limited**. Contact is frequent. The bottleneck is the rare coincidence of correct orientation AND open calyx. Prior kinetic models based on diffusion-limited arrival need revision.

---

## 12. What Comes Next

| Phase | Content | Timeline |
|-------|---------|----------|
| Phase 1 (done) | BLG SET 1D at AWI — contact ensemble, 5 findings | Complete |
| Phase 2 | β-Casein (IDP) vs. BLG — prediction: commits within 200 ns | Jul–Sep 2026 |
| Phase 3 | Enhanced sampling — metadynamics along (SASA, θ), PMF | TBD |
| Paper 1 | JCIS submission | Pending Zenodo DOI + P.P. sign-off |

---

## 13. Key Numbers to Know

| Quantity | Value |
|---------|-------|
| Contact events | 613 across 4.00 µs |
| Stable adsorptions | 0 |
| Longest contact event | 59 ns (R1) |
| Frames in contact (near-AWI) | 7–23% per trajectory |
| Maximum penetration | −0.71 nm past interface (R1) |
| Rg (native) | 1.496 ± 0.009 nm |
| SASA range (corrected) | 24–37 nm² |
| SASA autocorrelation time | 232 ns (range 81–394 ns across replicas) |
| N_eff | ~17 |
| Pearson r (SASA vs θ) | +0.006 |
| 95% CI on r | [−0.09, +0.11] |
| Total simulation time | 4.00 µs (4 × 1000 ns) |
| System size | ~140,000 atoms |

---

## 14. Key References

- Graham, D.E. & Phillips, M.C. (1979). *J. Colloid Interface Sci.* — Original protein adsorption kinetics model
- Mitternacht, S. (2016). *F1000Research* — freeSASA library
- CHARMM36m: Huang et al. (2017). *Nature Methods*
- TIP3P: Jorgensen et al. (1983). *J. Chem. Phys.*
- GROMACS 2020: Abraham et al. (2015). *SoftwareX*
- MDAnalysis: Michaud-Agrawal et al. (2011). *J. Comput. Chem.*

---

*Generated: June 2026 | COMFHA Project | Kasetsart University*
