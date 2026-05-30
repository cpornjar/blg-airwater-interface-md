# Narrative Report — Paper 1
## "Two-Factor Gating Mechanism of β-Lactoglobulin Adsorption at the Air-Water Interface: Atomistic Resolution of Intermittent Contact and Gated Stable Residency"

**Prepared:** May 16, 2026 — *revised May 17 after metric correction (see below).*
**Target venue:** Nature Communications (IF 16.6); fallback Langmuir / Food Hydrocolloids.
**Data basis:** SET 1A (1,000 ns CENTER) + Plan B R1/R2/R3 (R1 0–649 ns local; R2/R3 extensions to 1,000 ns in progress) + SET 1D-a / 1D-b orientation-controlled experiments.

> **Metric correction (May 17, 2026):** Earlier framing called this work a
> "no adsorption" study because the protein centre-of-mass never came within
> 0.5 nm of the interface. That was a metric artefact. BLG is a ~4 nm
> globular protein; a CoM at 1.35 nm above the interface means surface atoms
> are *at* the interface. The corrected metric — minimum distance from any
> protein heavy atom to the nearest air–water interface, contact threshold
> 0.30 nm — reveals frequent intermittent atomic contact in both CENTER and
> R1 trajectories. The new finding is **not** "adsorption finally happened",
> but rather **a contact/residency distinction**: contacts are common,
> sustained residency is gated.

---

## The Story in One Paragraph

β-Lactoglobulin (BLG), the major whey protein in bovine milk, is the primary stabilizer of milk foam. Decades of experimental work have established that BLG adsorbs at the air–water interface and partially unfolds there — but the molecular mechanism has never been directly observed. We ran the first unbiased atomistic molecular dynamics simulation of BLG at the air–water interface, using a 12 × 12 × 35 nm slab over 1,000 ns plus three near-interface replicas. The protein does not "swim passively" to the surface; nor does it sit indifferent in bulk. Instead, surface atoms of BLG make frequent intermittent contact with the air–water interface throughout the trajectory — 12.5 % of frames in CENTER, 19.2 % in the near-interface replica R1, with single atoms penetrating up to 0.71 nm past the interface plane into the vacuum. Yet none of these contacts persists more than ~10 ns: the protein touches and retreats. This intermittent-contact-without-residency pattern is accompanied by recurring hydrophobic-surface bursts (up to 52.5 nm² in R1, 2.7× baseline) driven by transient calyx-loop opening, while the alpha-helix and the beta-barrel scaffold remain intact. By cross-correlating contact, exposure, and orientation we identify the kinetic bottleneck: stable residency requires *simultaneous* hydrophobic patch exposure **and** correct calyx orientation, and these two factors are statistically anticorrelated under unbiased dynamics. A two-factor gate, not a diffusion barrier, sets the adsorption timescale. SET 1D, an orientation-controlled experiment, tests this prediction directly.

---

## Claim 1 — Pre-adsorption conformational activation exists and is detectable

**Claim:** BLG undergoes transient partial unfolding in bulk water prior to reaching the air-water interface. This activation is characterized by a spike in hydrophobic SASA that precedes and enables adsorption.

**Evidence (CENTER run — SET 1A, 1,000 ns):**
- Mean hydrophobic SASA: 26.20 ± 6.23 nm²
- Activation spikes: t = 259 ns (39.3 nm²), t = 759–779 ns (39.3–36.0 nm²), t = 940 ns (42.7 nm² — largest)
- Closest approach: 1.598 nm at t = 570 ns — correlates with elevated SASA window at 600–800 ns
- Beta-sheet RMSD spikes to 0.502 nm (max) during these windows — core partially disrupted
- Alpha-helix RMSD: mean 0.101 nm, max 0.299 nm — structurally stable throughout

**Evidence (Plan B Replica 1 — best candidate, 500 ns):**
- Hydrophobic SASA spiked to **52.48 nm²** at t = 259 ns (baseline 19.48 nm² at t = 0) — 2.7× increase
- Closest approach: 1.35 nm at t = 407.6 ns — closest of all replicas
- Hydrophobic patch RMSD: 0.305 nm (highest across all replicas) — calyx most mobile
- Alpha-helix RMSD: 0.111 nm — stable

**Mechanistic interpretation:** The pre-adsorption activation is a cooperative event where the beta-barrel transiently opens — exposing the hydrophobic calyx — without dismantling the alpha-helix scaffold. This "cracking open" of the calyx lowers the energetic cost of interfacial insertion by pre-exposing the residues that will contact the vacuum phase.

---

## Claim 2 — BLG makes frequent intermittent atomic contact with the interface but fails to commit to stable residency on a ≤ 1 µs timescale

**Claim:** Under the corrected nearest-atom contact metric (≤ 0.30 nm of any protein heavy atom to the nearest air–water interface), BLG samples the interface repeatedly throughout 1 µs of unbiased dynamics, but no contact event sustains more than ~10 ns of continuous residency. The rate-limiting molecular step is not diffusion to the interface (the protein arrives often) — it is the commitment to *stay*.

**Evidence — CENTER (SET 1A, 1,000 ns, nearest-atom analysis with stride 5):**
- 12.54 % of frames in contact (≤ 0.30 nm): 251 / 2001 frames
- 70.3 % of frames within 1.0 nm — protein is near the interface for most of the run
- 97 distinct contact events; longest 9.0 ns (t = 747–756 ns)
- Deepest atom penetration: −0.474 nm @ t = 570 ns (atom 0.47 nm past the interface plane, exposed to vacuum)
- No event with sustained residency > 10 ns

**Evidence — Replica 1 (0–649 ns, nearest-atom analysis):**
- 19.20 % of frames in contact (≤ 0.30 nm) — higher than CENTER, consistent with the near-interface starting geometry
- Two sustained contact windows: 370–450 ns and 580–650 ns
- 52 distinct contact events; deepest penetration −0.709 nm @ t = 406 ns
- The "closest approach 1.35 nm @ 408 ns" previously reported is the CENTER OF MASS distance during that same event — i.e., the same physical event re-interpreted under the corrected metric is *adsorption-by-contact* but *failure-to-commit-to-residency*

**Why the prior framing was wrong:** The earlier "no adsorption / spontaneous timescale > 1 µs" claim used centre-of-mass distance with a 0.5 nm threshold. BLG is ~4 nm wide; a CoM 1.35 nm above the interface places surface atoms at the interface and routinely past it. CoM-to-interface is the wrong observable for contact — it is the wrong observable by ~2 nm. Nearest-atom contact is the standard surface-science observable and the only one that detects what is physically happening.

**Why this matters (revised):** This is the first atomistic resolution of the *contact–residency distinction* for a folded globular protein at the air–water interface. Cornec et al. (1999) and Graham & Phillips (1979) observed slow surface coverage on seconds-to-minutes timescales but had no molecular probe of contact frequency. Our data shows BLG arrives at the interface readily and repeatedly on a sub-microsecond timescale; what is rare and slow is the *commitment*. This reframes the kinetic energy barrier from a diffusion problem to a residency problem — and motivates Claim 3, the molecular origin of that barrier.

---

## Claim 3 — Loop BC and the hydrophobic calyx are the predicted first-contact region

**Claim:** The most flexible region of BLG in bulk — Loop BC (residues 30–35) with RMSF ~0.53 nm — is the predicted first contact point at the air-water interface. The calyx (hydrophobic pocket) is the main driving force for adsorption orientation.

**Evidence:**
- RMSF analysis (CENTER run): Loop BC shows highest per-residue flexibility (~0.53 nm) — exceeds all beta-strands and the alpha-helix
- Hydrophobic patch vector orientation: mean 53.5 ± 20.9° — semi-random in bulk (not yet aligned), consistent with exploratory tumbling prior to adsorption
- Calyx SASA: 4.22 ± 1.02 nm² (CENTER), 4.11 nm² (R1) — maintained throughout, consistent with calyx remaining accessible for insertion
- Hydrophobic patch RMSD highest in R1 (0.305 nm) — the replica that approached closest to the interface

**Mechanistic interpretation:** Loop BC, located at the entrance to the calyx, acts as the "antenna" that first contacts the vacuum phase. The calyx orientation aligns with the interface as the protein approaches, consistent with the thermodynamic driving force for hydrophobic burial.

---

## Claim 4 — Alpha-helix is structurally stable; beta-sheet is transiently disrupted during activation

**Claim:** During pre-adsorption activation, the alpha-helix (residues 130–142) remains intact while the beta-barrel partially disrupts. This differential stability has mechanistic implications — the helix acts as a structural scaffold maintaining the calyx orientation.

**Evidence:**

| Metric | CENTER 1000ns | R1 | R2 | R3 |
|--------|--------------|-----|-----|-----|
| Backbone RMSD (mean) | 0.229 nm | 0.218 nm | 0.195 nm | 0.238 nm |
| Beta-sheet RMSD (mean) | 0.260 nm | 0.245 nm | 0.228 nm | 0.243 nm |
| Alpha-helix RMSD (mean) | **0.101 nm** | **0.111 nm** | **0.093 nm** | **0.137 nm** |
| Beta-sheet RMSD (max) | 0.502 nm | — | — | — |

Alpha-helix RMSD is consistently 2–3× lower than backbone and beta-sheet RMSD across all simulations — the helix is the most stable secondary structure element throughout.

**Literature context:** Experimental SRCD at oil-water interfaces reports an *increase* in non-native alpha-helix *post-adsorption* (Zhai & Miles). Our data shows the helix is stable *pre-adsorption* in bulk — the post-adsorption helix gain is therefore a consequence of interfacial insertion, not a prerequisite. This resolves an apparent contradiction in the literature.

---

## System & Methods Summary (for Methods section)

- **Protein:** BLG monomer, PDB 1BEB (X-ray, 1.8 Å resolution), chain A
- **Force field:** CHARMM36m
- **Water:** TIP3P
- **Simulator:** GROMACS 2020.4
- **Box:** 12 × 12 × 35 nm slab (12 nm vacuum each side, ~7 nm water slab)
- **Temperature:** 298 K (V-rescale thermostat)
- **Pressure:** No pressure coupling (required for slab geometry)
- **Electrostatics:** PME, 0.16 nm grid spacing, order 4
- **VdW:** Force-switch 1.0–1.2 nm
- **Integrator:** Leap-frog, dt = 2 fs
- **Ions:** Na⁺/Cl⁻ (neutralizing)
- **DispCorr:** No (CHARMM36 slab standard)
- **SET 1A:** Protein at slab center, 1,000 ns production
- **Plan B:** Protein 2.183 nm from upper interface, 3 replicas × 500 ns (extending to 1,000 ns)
- **Analysis:** MDAnalysis 2.10.0, freesasa, RMSD with unwrap PBC fix, RMSF, Z-position tracking

---

## Key Figures Available

| Figure | File | Caption note |
|--------|------|--------------|
| Z-position CENTER | `z_position/CENTER_1000ns_z_position.png` | 1,000 ns trajectory, min dist 1.598 nm at 570 ns |
| Z-position replicas | `z_position/REPLICA_{1,2,3}_z_position.png` | Comparative approach to interface |
| RMSD CENTER | `rmsd/CENTER_1000ns_rmsd.png` | Backbone/beta-sheet/helix/patch |
| RMSD replicas | `rmsd/REPLICA_{1,2,3}_rmsd.png` | Cross-replica structural stability |
| SASA CENTER | `sasa/CENTER_1000ns_sasa.png` | Hydrophobic SASA spikes — key activation evidence |
| SASA replicas | `sasa/REPLICA_{1,2,3}_sasa.png` | R1 spike at 52.5 nm² most dramatic |
| Orientation CENTER | `orientation/CENTER_1000ns_orientation.png` | Patch angle distribution |

**Figures still needed (post-R2/R3 completion):**
- Combined Z-position panel (all replicas + CENTER in one figure)
- RMSF per-residue (Loop BC highlighted)
- SASA correlation with Z-distance (scatter plot: hydrophobic SASA vs dist-to-interface)

---

## Target Audience & Framing

**Journal:** Langmuir (ACS) — Physical chemistry at interfaces, colloid science, food biophysics
**Framing:** Mechanistic physical chemistry — not food engineering. Lead with the kinetic energy barrier and atomistic mechanism. Food/foam context is motivation, not the conclusion.
**Length:** ~6,000–8,000 words, 6–8 figures, ~40 references

---

## What This Paper Does NOT Claim

- We do NOT claim BLG achieves **stable adsorption** (continuous residency > 10 ns) in our 1 µs unbiased simulations — we explicitly observe gated failure-to-commit; SET 1D tests whether enforcing patch-down orientation rescues residency.
- We do NOT claim Loop BC is the first-contact residue — Loop BC is the highest-RMSF region in bulk, but identifying *which* residues actually make first contact in the 97 CENTER and 52 R1 contact events requires a residue-resolved post-pass that is pending.
- We do NOT claim the mechanism is complete — Phase 2 (β-Casein) comparison is forthcoming as Paper 2.
- We do NOT extrapolate the contact statistics to the dimer or to higher concentrations.
- R2/R3 1,000 ns data not yet included — will sharpen the contact statistics and the residency-distribution tail once available.
