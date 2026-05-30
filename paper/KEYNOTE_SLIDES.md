# Keynote Slide Deck — Advisor Meeting
# Two-Factor Gating of BLG Adsorption at the Air-Water Interface
*Chalakon Pornjariyawatch | May 26, 2026*

> **Usage:** Each `---` block = one slide. Title in `##`, bullets are content, *italics* = speaker notes.

---

## Slide 1 — Title

**Two-Factor Gating Mechanism of β-Lactoglobulin Adsorption at the Air-Water Interface: Evidence from Atomistic Molecular Dynamics**

Chalakon Pornjariyawatch & Prapasiri Pongprayoon
Department of Chemistry, Kasetsart University
May 2026 | Target: Nature Communications

*[Visual: BLG crystal structure (1BEB) near a water surface. Clean, minimal.]*

---

## Slide 2 — Why Does This Matter?

- Good milk foam = high protein, low fat
- The protein film stabilising foam bubbles is anchored at the **air-water interface**
- β-Lactoglobulin (BLG) is the **dominant interfacial protein** in bovine milk (~3 g/L)
- Central question: **How does BLG get from bulk water to the interface?**

*[Visual: cartoon of foam bubbles with protein monolayer, then zoom to BLG approaching interface]*
*[Keep it brief — advisor knows the context. One slide maximum on motivation.]*

---

## Slide 3 — The Classical View vs. The Problem

**Classical view (Graham & Phillips, 1979):**
> Surface tension induces global protein unfolding → unfolded chain adsorbs

**The problem:**
- BLG adsorbs slowly (seconds-to-minutes) despite being surface-active
- BLG in the adsorbed state is only *partially* unfolded
- **No atomistic simulation of BLG at the air-water interface has ever been reported**
  - All prior MD: oil-water systems, pre-stressed conformations, or different proteins
  - CoM-distance metrics used → blind to surface contact for a 4 nm globular protein

**Our approach:** First unbiased atomistic MD of native-state BLG at the air-water interface

*[Visual: schematic showing CoM vs. nearest-atom metric — show why CoM misses contact]*

---

## Slide 4 — Simulation Setup

| Parameter | Value |
|-----------|-------|
| Protein | BLG (1BEB), native fold |
| Force field | CHARMM36m + TIP3P |
| Box geometry | 12 × 12 × 35 nm slab |
| Atoms | ~140,000 |
| Replicas | CENTER (1 µs, bulk start) + R1/R2/R3 (825–1000 ns, near-interface) |
| **Total trajectory** | **3.83 µs** |
| Adsorption metric | Nearest-atom contact ≤ 0.30 nm (not CoM distance) |

*[Visual: simulation box snapshot showing protein, water slab, vacuum region — side view]*
*[Emphasise the metric correction — this is the methodological contribution]*

---

## Slide 5 — Finding 1: Contact Is Frequent, Commitment Is Rare

**458 contact events across 3.83 µs:**
- CENTER: 97 events, 12.5% of frames
- R1–R3: 7.1–24.6% of frames per replica
- Atoms penetrate up to 0.71 nm past the interface plane

**But:**
- 451/458 events (98.5%) terminate within 10 ns
- Only **7 events sustain ≥ 10 ns continuous residency**
- **0 events show stable commitment to the interface**

> The protein arrives readily. The bottleneck is not contact — it is **commitment**.

*[Visual: PAPER_FIG2_CONTACT_AB.png — show Z-position + contact timeseries for CENTER and R1]*
*[Point to the rapid contact/retreat pattern — "touch and go"]*

---

## Slide 6 — Contact Timeseries: All Four Replicas

*[Visual: PAPER_FIG2_CONTACT_CD.png — R2 and R3 contact timeseries]*
*[Highlight R3's 21.8 ns event — longest in the dataset — and note: gate was CLOSED]*

- R2 (1000 ns): 156 events, deepest −0.502 nm, longest 6.0 ns
- R3 (1000 ns): 145 events, deepest −0.475 nm, **longest 21.8 ns**
- R3's 21.8 ns event: SASA above threshold 88% of the time — but **calyx angle never below 30°** (mean θ = 76°)
- The most extreme outlier in 3.83 µs proceeds *without gate opening*

---

## Slide 7 — Finding 2: The Two-Factor Gate

**Why does the protein retreat? Two conditions must coincide simultaneously:**

| Condition | Meaning | Frequency (R1) |
|-----------|---------|---------------|
| SASA ≥ 35 nm² | Hydrophobic calyx **exposed** | 46.6% |
| θ ≤ 30° | Calyx **oriented toward interface** | 3.0% |
| **Both (gate-open)** | **Commitment-competent** | **0.36%** |

**Independent expectation:** 46.6% × 3.0% = 1.40%
**Observed:** 0.36% → **3.9× BELOW independence**

> The two factors are geometrically anti-correlated: when the calyx opens, it tends to face away.

*[Visual: schematic of BLG with calyx shown — two panels: "exposed but misaligned" vs "aligned but not exposed"]*

---

## Slide 8 — Gate Is Robust Across All Four Replicas

*[Visual: PAPER_FIG3_GATE — scatter plot (SASA vs θ) + 2D heatmap showing empty upper-left quadrant]*

**Aggregate (3.83 µs, 7,655 frames):**

| Replica | Frames | Activated | Aligned | Obs/Indep |
|---------|--------|-----------|---------|-----------|
| CENTER | 2,001 | 24.3% | 1.6% | **0.16** |
| R1 | 1,653 | 46.6% | 3.0% | **0.26** |
| R2 | 2,000 | 36.0% | 3.5% | **0.38** |
| R3 | 2,001 | 38.6% | 2.7% | **0.58** |
| **Aggregate** | **7,655** | **32.9%** | **3.5%** | **0.32** |

- **Every replica: Obs/Indep < 1.0**
- Aggregate suppression: 3.1-fold
- Block-jackknife 95% CI: **[0.15, 0.48]** — entirely below unity

---

## Slide 9 — All 7 Long Events Are Gate-Absent

*[Visual: TWO_FACTOR_GATE_Fig4.png — upper panel showing the 7 events mapped]*

**Two gate-absent pathways:**

**Activated-but-misaligned (4 events):**
- R1: 57.5 ns, 34.5 ns, 12.5 ns | R3: 21.8 ns
- High SASA throughout — calyx exposed for *minutes equivalent*
- Calyx orientation persistently wrong (θ mean > 60°)
- Contact ends when SASA drops below 35 nm² within 5 ns → fully reversible

**Non-activated contact (3 events):**
- CENTER: 10.5 ns | R1: 19.0 ns + 31.5 ns
- Calyx buried (SASA < 35 nm²) — non-hydrophobic surface contact
- Gate concept doesn't apply

> Even 57.5 ns of surface contact without gate opening is insufficient for commitment.

---

## Slide 10 — Structural Analysis: Loop-Mediated Activation

*[Visual: PAPER_FIG3_ACTIVATION.png — panels a-d: SASA, Rg, RMSF, patch RMSD]*

**Global structure preserved throughout (3.83 µs):**
- Rg = 1.496 ± 0.009 nm — no monotonic expansion
- α-helix (130–142) RMSD ≤ 0.137 nm — intact
- β-barrel backbone RMSD 0.19–0.24 nm — assembled

**Activation is local, not global:**
- SASA bursts every 30–40 ns (stochastic process, not a one-shot event)
- RMSF: Loop BC (30–35) dominant in bulk → shifts to Loop CD/EF (57–60) near interface
- Loop CD/EF sits directly above the hydrophobic calyx
- Patch RMSD ratchets slowly upward (progressive calyx mobilisation)

> The classical "surface unfolding" narrative is inconsistent with our data.

---

## Slide 11 — Mechanistic Reframing

**Before (classical view):**
```
Diffusion → Surface tension → Global unfolding → Adsorption
```

**After (this work):**
```
Diffusion → Contact (frequent, reversible)
                    ↓
         Two-factor gate on commitment:
         SASA ≥ 35 nm²  AND  θ ≤ 30°  (simultaneous)
                    ↓
               Commitment → Stable residency
```

**Key implication for protein engineering:**
- The orientation gate is the bottleneck
- Pre-aligning the calyx toward the interface (SET 1D) should accelerate adsorption
- This is a **designable molecular target**

---

## Slide 12 — SET 1D: Testing the Gate (Design Experiment)

**Prediction:** If the gate controls commitment, then:
- Pre-aligning calyx toward interface (1Da, patch-down) → **faster commitment**
- Pre-aligning away (1Db, patch-up control) → **commitment suppressed**

**Status:**
- Both 1Da and 1Db placed in vacuum region, 2.06 nm above interface
- Preliminary 45 ns: protein reaches interface within 2 ns in both
- Unexpected: both variants submerge into water regardless of calyx orientation

**Two interpretations (decision needed):**
- A. Setup issue — protein too close to interface at t=0 after equilibration
- B. Real physics — gate operates asymmetrically (bulk-water → interface only); from vacuum side, hydrophilic exterior dominates

*[This result needs advisor input — do not present as settled]*

---

## Slide 13 — Paper Status

| Item | Status |
|------|--------|
| Main text | ✅ 20 pages, clean compile |
| Figures | ✅ All 4 figures generated |
| Bibliography | ✅ 40 entries, RIS exported |
| Auto-review (Opus 4.7) | ✅ **7/10, "almost ready"** |
| R1 trajectory (1000 ns) | ⏳ Job running, ETA **May 27** |
| Fig 2b + Fig 3 update | ⏳ After R1 done |
| SET 1D abstract decision | 🔴 **Co-author decision needed** |
| Acknowledgements | 🔴 Needed |
| Data availability | 🔴 Needed |

**Target journal:** Nature Communications (IF 16.6)
**Submission target:** Early June 2026

---

## Slide 14 — What the Advisor Needs to Decide Today

1. **SET 1D in abstract:** Currently promises "follow-up communication." Options:
   - (a) Keep as-is *(weakens abstract)*
   - **(b) Move SET 1D mention to §4 only — abstract stands on what was done** ← recommended
   - (c) Remove SET 1D entirely from abstract

2. **Acknowledgements:** Please draft — funding source (DPST scholarship? KU grant?), compute time (KU HPC COMFHA cluster)

3. **Data availability:** Will trajectories be deposited? (Zenodo, OSF?) MDAnalysis scripts on GitHub?

4. **Submission timeline:** Early June acceptable?

---

## Slide 15 — Summary

- **458 contact events in 3.83 µs** — BLG touches the interface frequently
- **451/458 events < 10 ns** — commitment is rare
- **Two-factor gate identified:** SASA ≥ 35 nm² AND θ ≤ 30° must coincide
- **3.1-fold joint occupancy suppression** (Obs/Indep = 0.32, CI [0.15, 0.48])
- **Gate robust across all 4 replicas** (Obs/Indep: 0.16–0.58, all < 1)
- **7 long events — all gate-absent** — even 57.5 ns contact without gate opening is insufficient
- **Global fold preserved** — activation is loop-mediated, not global unfolding

> BLG is coincidence-limited, not diffusion-limited.
> The gate is an orientation filter, not an energy barrier from unfolding.

**Next: R1 1000 ns (May 27) → submit June 2026**

---

## Appendix — Robustness Checks (if asked)

**Threshold robustness grid (3 × 5):**
- Obs/Indep < 1 for all SASA thresholds (30, 35, 40 nm²) at angle ≤ 45°
- Breaks down only at angle ≤ 90° (unconstrained) — as expected
- Confirms threshold choice is not load-bearing

**Statistical note on "anti-correlation":**
- Pearson r = −0.085, n_eff = 125 (autocorr-corrected), 95% CI [−0.26, +0.09] crosses zero
- Raw p = 6.9×10⁻¹⁴ is misleading (n = 7,655 >> n_eff)
- We do NOT claim statistical anti-correlation — we claim suppression below independence (confirmed by jackknife CI)
