# Paper 1 — Expansion Plan: BLG + β-Casein Comparative Study

**Decision locked:** 2026-06-09  
**Trigger:** P.P. meeting, June 9, 2026  
**Scope change:** Paper 1 expands from BLG-only to BLG vs β-Casein comparative. Submission on hold.

---

## P.P. Meeting Notes — June 9, 2026

*Captured verbatim from session. Ambiguous items flagged with [CONFIRM WITH P.P.]*

### Direction (overarching)
- Paper should be unbiased and explain lab experiments clearly
- Frame as: computational approach to explain lab experiment → suggest how to modify/improve milk protein adsorption
- Correlation with lab experiment expected [CONFIRM WITH P.P.: which lab experiments? Foam stability? Surface pressure isotherms?]

### 1. About Reporting
- Must report **both BLG and CASEIN** — they are the main milk proteins; reporting only BLG is insufficient
- Showing only R1 is biased
- R2 may need to be cut: SASA trend in R2 is down/stable while R1 and R3 trend upward — inconsistency is a problem [→ see Open Decision 1 below]
- β-Casein: simulate as BLG environment, **2 replicas** (saves cluster time; β-Casein is larger)

### 2. Figure Plan (4 Figures)

**Figure 1 — Schematic / Cartoon**
- Panel A (top): BLG and CASEIN side by side
  - Highlight key structural features: calyx (BLG), hydrophobic N-terminal patch (CAS)
  - Clear labels on each feature
- Panel B (bottom): 3D simulation box schematic
  - Layout: VACUUM | MOLECULE | WATER | VACUUM
  - 3D view, no angle/perspective distortion — make it maximally clear
  - Should show both proteins (one per box, or combined?)  [CONFIRM WITH P.P.]

**Figure 2 — Structural Dynamics**
- RMSD, RMSF, Rg for both proteins
- Show replica average (not just R1 — removes bias)
- BLG baseline: Rg 1.496 ± 0.009 nm, RMSD ~0.24 nm (stable)
- CAS expected: much higher RMSD (IDP — document, do not "fix")
- [CONFIRM WITH P.P.: show BLG and CAS as separate subpanels, or overlaid?]

**Figure 3 — Interface Density / PCA**
- Water density × Protein density along Z axis
- → PC1 vs PC2 scatter (dimensionality reduction of the density profiles)
- Purpose: show mechanistically how each protein distributes relative to the interface

**Figure 4 — Quantitative Comparison Table + Key Observables**
- DSSP (secondary structure — table or heatmap) [CONFIRM WITH P.P.: table vs figure?]
- Surface tension (from pressure tensor)
- SASA (PBC-corrected)
- HB contacts:
  - H2O–H2O
  - H2O–protein
  - Protein self-interaction

### 3. Advisor-Recommended Analyses (raw notes from P.P.)

| Raw note | Interpretation | Status |
|----------|---------------|--------|
| Density Protein × Density Water | Z-density profile for both atoms types | [CONFIRM WITH P.P.] |
| Cluster 100 frames → properties | gmx cluster → representative frames → per-cluster analysis | [CONFIRM WITH P.P.: cluster on what metric? RMSD? Calyx orientation?] |
| Proj (GROMACS command?) → PC1 PC2 | `gmx covar` + `gmx anaeig -proj` → PC1/PC2 scatter | confirmed |
| PCA | Same as above | confirmed |
| secondary dasa | Secondary-structure SASA? Or DSSP + per-residue SASA? | [CONFIRM WITH P.P.] |
| Calyx → Cluster | Cluster calyx-region conformations specifically (not whole protein) | [CONFIRM WITH P.P.] |
| DSSP | `gmx do_dssp` or MDAnalysis secondary structure | confirmed |
| Surface tension water | From .edr pressure tensor: γ = (Lz/2)·[(Pxx+Pyy)/2 − Pzz] | confirmed |
| SASA | Already done for BLG; needed for CAS | confirmed |
| CONTACT | Already done for BLG (613 events); needed for CAS | confirmed |
| Improve/fix Calyx SASA + Orientation — too messy | Refactor orientation figure; cluster calyx conformations | confirmed |

---

## Open Decisions (not yet settled — must decide before analysis)

### Open Decision 1 — R2 Replica (bring to team)

**Situation:** R2 SASA trend is downward/stable. R1 and R3 trend upward. Three options:

| Option | What it means | Risk |
|--------|--------------|------|
| A — Drop R2 from all analysis | Use R1+R3 only; compute new headline numbers | **Outcome-based exclusion** — JCIS reviewer will ask why R2 was dropped. Paper's credibility is built on honesty about limits. This is the highest-risk approach unless there's a mechanistic reason R2 differs. |
| B — R2 in supplement, R1+R3 in main | Acknowledge R2 as "non-committing trajectory" in supplement | Valid if we can state a mechanism (e.g., R2 never approached interface). Needs checking. |
| C — Keep all 3, explain R2 in text | Report R1+R2+R3 average; note R2 shows stable SASA = non-adsorbing pathway sampled | Strongest scientific case; allows statement "adsorption is stochastic even at µs scale" |

⚠ **Critical constraint:** Headline numbers (613 contacts, SASA 24–37 nm², Pearson r +0.006) were computed across CENTER + R1 + R2 + R3. Dropping R2 means **all headline numbers recompute** and all existing figures change. Verify whether R2 moves the numbers before deciding.

**Recommended team position:** Check R2 contact count and SASA mean. If R2 has significantly fewer contacts and lower SASA mean, it may genuinely represent a "did not commit" trajectory — which is actually scientifically interesting. If so, Option B is defensible. If R2's contact count is similar to R1/R3, Option C is more honest.

**Action before deciding:** `grep "R2" results/gate_analysis/` — look at R2 contact events and SASA mean.

### Open Decision 2 — Applied Claim Scope

**P.P.'s direction:** Paper should suggest "how to modify/improve milk protein adsorption."

**Tension with current data:** BLG data shows pre-commitment ensemble — no gate-open events, no adsorption commitment within µs. The data characterizes what happens *before* commitment, not commitment itself. We cannot prescribe "do X to improve adsorption" from trajectories where adsorption didn't complete.

**What the data CAN support:** Comparative mechanism — "BLG (calyx, structured) vs CAS (disordered, hydrophobic N-terminus) have fundamentally different interface interaction modes, suggesting disorder promotes faster commitment." This *implies* the applied direction without overclaiming.

**Recommended framing:** "The structural contrast between BLG and β-Casein at the molecular level illuminates design principles for interfacially active proteins: intrinsic disorder and surface-exposed hydrophobic patches lower the kinetic barrier to adsorption."

[CONFIRM WITH P.P.: Is this the kind of applied conclusion they have in mind, or do they want explicit modification recommendations?]

---

## New Paper Architecture

### Working Title
"Molecular Mechanism of Milk Protein Adsorption at the Air–Water Interface: A Comparative Study of β-Lactoglobulin and β-Casein"

*Previous title preserved:* "Contact without Commitment: Atomistic Characterisation of β-Lactoglobulin Adsorption Dynamics at the Air–Water Interface" (BLG-only framing)

### New Framing
> BLG (folded, calyx-driven) vs β-Casein (disordered, hydrophobic N-terminal patch) at the same slab air-water interface. Comparative µs MD reveals how protein structural character governs adsorption mode at the molecular scale.

---

## Analysis Pipeline

### BLG (trajectories exist: CENTER + R1 + R2 + R3)

| Analysis | Status | Script | Notes |
|----------|--------|--------|-------|
| Contact events | ✓ done | `detect_adsorption_contact.py` | 613 total, 6 long events ≥10 ns |
| SASA (PBC-corrected) | ✓ done | `gate_analysis_all_replicas.py` | 24–37 nm², mean 28.95 nm² |
| RMSF | ✓ cached | `precompute_rmsf.py` | CENTER + R1 cached |
| RMSD, Rg | ✓ exists | needs R3 + average | recompute with R2 decision made |
| **Z-density profile** | ✗ needed | write `blg_density.py` | `gmx density` or MDAnalysis |
| **PCA** | ✗ needed | write `blg_pca.py` | `gmx covar` → `gmx anaeig -proj` |
| **DSSP** | ✗ needed | write `blg_dssp.py` | `gmx do_dssp` or MDAnalysis |
| **Surface tension** | ✗ needed | write `blg_surface_tension.py` | from `.edr`: γ = (Lz/2)·[(Pxx+Pyy)/2 − Pzz] |
| **HB counts** | ✗ needed | write `blg_hbonds.py` | `gmx hbond` — 3 groups: wat-wat, wat-prot, prot-prot |
| **Clustering** | ✗ needed | write `blg_cluster.py` | `gmx cluster` — 100 representative frames |
| **Calyx orientation** | ✗ refactor | improve existing | current figure "too messy" per P.P. |

### β-Casein (no trajectories — prep + submit first)

| Step | Status | Command | Notes |
|------|--------|---------|-------|
| pdb2gmx | ✗ | `/cas-prep 1` | CHARMM36m, CASEIN.pdb |
| editconf | ✗ | `/cas-prep 2` | same slab geometry as BLG |
| solvate | ✗ | `/cas-prep 3` | |
| genion | ✗ | `/cas-prep 4` | 150 mM NaCl |
| EM | ✗ | `/cas-prep 5` | Fmax < 1000 kJ/mol/nm |
| NVT | ✗ | `/cas-prep 6` | no NPT |
| Production mdp | ✗ | `/cas-prep 7` | 2 replicas |
| SLURM submit | ✗ | `/cas-prep 8` | explicit "yes" required |
| **All BLG analyses above** | ✗ | `cas_*.py` variants | mirror after trajectories arrive |

---

## Figure Code Management

The `scripts/figures/` directory is the home for all figure scripts (reorganized June 8).

**Proposed naming convention** (user to confirm):
```
scripts/figures/
  blg_fig1_schematic.py        # cartoon + box (shared — may be combined_)
  blg_fig2_dynamics.py         # RMSD/RMSF/Rg — BLG panels
  cas_fig2_dynamics.py         # RMSD/RMSF/Rg — CAS panels
  combined_fig3_density_pca.py # density profiles + PCA (BLG + CAS overlaid)
  combined_fig4_comparison.py  # DSSP/surface tension/SASA/HB table
  utils.py                     # shared MDAnalysis setup, colour palette, style
```

**Current scripts to migrate/refactor:**
- `make_fig2_ab_cd.py` → `blg_fig2_contact.py` (contact events — Fig 2 in old BLG paper)
- `make_fig3_activation.py` → `blg_fig3_activation.py`
- `make_fig4_optionA.py` → `blg_fig4_scatter.py`
- New scripts: density, PCA, DSSP, surface_tension, hbonds, cluster

This is the user's refactor to lead — propose structure, don't unilaterally rename.

---

## Timeline (rough)

| Week | Work |
|------|------|
| June 9–13 | Confirm open decisions with P.P. | BLG new analyses (density, PCA, DSSP, surface tension, HB) | β-Casein prep → submit cluster |
| June 15–20 | β-Casein equilibration monitoring | BLG clustering + calyx refactor | Draft figure outlines |
| June–August | β-Casein production trajectories (2 × 1 µs) |
| August | CAS analysis (mirror BLG pipeline) |
| Sept | Combined figures + paper rewrite |
| Oct–Nov | Target JCIS submission (revised) |

---

## Status Trail

- June 2, 2026: BLG Paper 1 scored 10/10 READY (Gemini 2.5 Flash). Citation audit clean. LaTeX clean.
- June 9, 2026: Scope expanded to BLG + CAS comparative per P.P. Submission on hold.

*BLG core remains valid — do not discard any existing results. Expansion adds CAS + new analyses.*
