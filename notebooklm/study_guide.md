# Study Guide — Contact without Commitment
## BLG Adsorption at the Air-Water Interface
*COMFHA Lab · Kasetsart University · Paper 1 → JCIS (IF ~9)*

---

## The One-Sentence Story

> BLG touches the air-water interface 613 times across 4 µs, but never commits. Calyx exposure (SASA) and orientation (θ) are statistically independent on the µs timescale. Commitment requires enhanced sampling to characterise.

---

## Part 1 — Background: Why This Problem Matters

### What is BLG and why does it foam?
β-Lactoglobulin (BLG) is the dominant whey protein in bovine milk (~3 g/L). It forms a viscoelastic film at the air-water interface (AWI) that stabilises milk foam bubbles. Adsorption is **slow** — seconds to minutes — with a measured kinetic barrier. This distinguishes BLG from flexible proteins like β-casein.

### What was the classical explanation?
Graham & Phillips (1979): surface tension at the AWI drives **global unfolding**, which anchors the protein. This was never directly observed at atomic resolution.

### What gap did this work fill?
- All prior BLG MD: oil-water only, pre-positioned, ≤100–200 ns
- Centre-of-mass (CoM) metric is blind for a 4 nm protein: CoM stays 2–3 nm from AWI even when atoms are touching
- **No unbiased atomistic simulation of native BLG at the AWI existed**

---

## Part 2 — The Five Findings

### Finding 1 — Contact Is Frequent
- **613 contact events** across 4 µs (nearest-atom ≤0.3 nm criterion)
- **7.1–23.4%** of frames per trajectory spent in contact
- Deepest penetration: **0.71 nm** past the Gibbs dividing surface
- Typical duration: < 1 ns (touch and retreat)
- *Why it matters:* CoM distance detected ~0 events; nearest-atom reveals the protein is constantly probing the interface

### Finding 2 — Commitment Is Absent
- Only **6 events ≥ 10 ns** out of 613
- Longest event: **59 ns** (R1) — still no commitment
- **0 stable adsorptions** in 4.00 µs
- Long-event SASA: 28.5–30.5 nm² (not activated); angles 44–75° (not aligned)
- *Why it matters:* The bottleneck is not contact — it is commitment

### Finding 3 — Compact Globally, Breathing Locally
- Rg = **1.496 ± 0.009 nm**, flat throughout 4 µs — no global unfolding
- β-barrel RMSD ~0.21 nm, α-helix RMSD ≤0.14 nm — secondary structure intact
- Calyx SASA fluctuates **24–37 nm²** in recurring ~30–40 ns bursts — stationary stochastic process
- *Why it matters:* Disproves the Graham & Phillips surface-denaturation model

### Finding 4 — Interface Shifts Which Loop Opens
- **Bulk (CENTER):** Loop BC (residues 30–35) dominates — RMSF peak **0.54 nm**
- **Near AWI (R1):** Loop CD/EF (residues 57–60) rises to **0.39 nm**; Loop BC falls to 0.25 nm
- Loop CD/EF sits directly above the hydrophobic calyx → interface-induced conformational preference
- *Why it matters:* Loop CD/EF is the **engineering target** for rational mutant design

### Finding 5 — SASA and Orientation Are Independent
- Pearson r = **+0.006** (SASA vs. θ across 8006 contact frames)
- Block bootstrap 95% CI: **[−0.09, +0.11]** — rules out |r| > 0.11
- SASA autocorrelation: **232 ns** → N_eff ≈ 17 (not 8006)
- 2D joint KDE: uniform — no quadrant clustering
- *Why it matters:* No two-factor gate exists on the µs timescale; commitment cannot be predicted by SASA or θ alone

---

## Part 3 — The PBC Correction (Scientific Integrity)

| | Before fix | After fix |
|---|---|---|
| SASA range | 45–62 nm² | **24–37 nm²** |
| Gate-open frames | 21 (0.27%) | **0** |
| Pearson r | −0.085 | **+0.006** |
| Original narrative | "Two-factor gate" | Scope claim |

**Root cause:** freeSASA is not PBC-aware. Without `mda_unwrap`, atoms split across periodic boundaries inflate SASA 2×. Fix: MDAnalysis `unwrap` transformation before every freeSASA call.

**Lesson:** Always verify coordinate integrity before surface calculations in periodic systems.

---

## Part 4 — Key Numbers (Memorise These)

| Quantity | Value |
|----------|-------|
| Total simulation time | **4.00 µs** (4 × 1000 ns) |
| Trajectories | **4**: CENTER (bulk-start) + R1, R2, R3 (near-AWI) |
| Contact events | **613** — 97 + 215 + 156 + 145 |
| Contact fraction | **7.1–23.4%** per trajectory |
| Max penetration | **0.71 nm** |
| Long events (≥10 ns) | **6** — none commits |
| Longest event | **59 ns** (R1) |
| SASA range (corrected) | **24–37 nm²** (mean 28.95) |
| p95 threshold | **32.1 nm²** |
| Pearson r | **+0.006** |
| Block bootstrap 95% CI | **[−0.09, +0.11]** |
| N_eff | **≈17** (from 4 µs / 2×232 ns) |
| SASA autocorrelation | **232 ns** |
| Rg (R1) | **1.496 ± 0.009 nm** |
| Loop BC RMSF (bulk) | **0.54 nm** (residues 30–35) |
| Loop CD/EF RMSF (AWI) | **0.39 nm** (residues 57–60) |
| TIP3P surface tension | **~36 mN/m** vs 72 mN/m experiment (≈ half) |

---

## Part 5 — Study Questions

### Conceptual Questions

**Q1: Why was the CoM distance metric inadequate for this study?**
BLG is ~4 nm in diameter. When any surface atom touches the AWI, the centre of mass is still ~2–3 nm away — well above any reasonable CoM threshold. The CoM metric recovers ~0 contact events; nearest-atom recovers 613.

**Q2: What is the contact/commitment dichotomy?**
Contact = nearest atom within 0.3 nm of the Gibbs surface. This is frequent (613 events, 7–23% of frames). Commitment = stable adsorption where the protein stays permanently. This is never observed in 4 µs. The bottleneck is not making contact — it is converting contact into stable residence.

**Q3: Why does r = +0.006 matter scientifically?**
A "two-factor gate" mechanism would require that commitment happens only when both SASA is high AND θ is favourable — implying strong SASA–θ correlation. r = +0.006 with CI [−0.09, +0.11] rules out |r| > 0.11 at 95% confidence. The two conditions never reliably coincide, explaining why commitment is not observed.

**Q4: Why was block bootstrap necessary instead of standard CI?**
SASA has a 232 ns autocorrelation time. Standard CIs assume independence between frames. With 8006 contact frames at 0.5 ns stride, naive N = 8006 is wildly inflated. Block bootstrap with 232 ns blocks gives N_eff ≈ 17 — the true number of independent observations in 4 µs.

**Q5: What does the Loop CD/EF shift tell us?**
In bulk, Loop BC (30–35) is the dominant flexible region. Near the AWI, Loop CD/EF (57–60) takes over. Since Loop CD/EF borders the calyx entrance, this interface-induced shift means proximity to the AWI preferentially activates calyx-opening motions. The interface does more than attract the protein — it changes its internal dynamics.

**Q6: Why can't this paper claim to explain the adsorption mechanism?**
The commitment step requires a free energy barrier crossing that is not sampled by 4 µs of unbiased MD. What this paper provides is the pre-commitment baseline: what the protein looks like just before committing. The mechanism of commitment itself requires enhanced sampling (metadynamics, REST2) along the (SASA, θ) coordinate.

**Q7: Does the paper disprove global unfolding?**
It shows global unfolding does NOT occur during the pre-commitment contact ensemble over 4 µs. Rg is flat at 1.496 nm, β-barrel intact. This contradicts Graham & Phillips (1979) as the dominant mechanism at the pre-commitment stage. Whether commitment itself eventually involves partial unfolding remains an open question for enhanced sampling to answer.

### Data Interpretation Questions

**Q8: R1 has 215 contact events but the figure shows fewer bands — why?**
Event count (215) comes from full 0.1 ns resolution analysis. Figures are plotted at 0.5 ns stride — brief events separated by gaps < 0.5 ns get merged into one band. Both numbers are correct for their resolution; the Methods explains this.

**Q9: Why are R1/R2/R3 called "near-AWI replicas" and CENTER "bulk-start"?**
CENTER starts BLG at the geometric centre of the water slab, ~9 nm from either interface. R1–R3 start BLG at 2.18 nm below the upper interface. This tests whether starting position affects the contact ensemble — it does not change the fundamental dichotomy, but replicas spend more time near the interface.

**Q10: SET 1D — what was it and why was it removed?**
SET 1D tested oriented starting positions (calyx-down and calyx-up). Both 1Da and 1Db submerged into water within 2 ns regardless of starting orientation (CoM drops from 23 → 19 nm; calyx angle drifts to ~100°). Removed from Paper 1 as it was preliminary and only 45 ns. Kept as baseline for future enhanced-sampling comparison.

---

## Part 6 — Anticipated Q&A (Reviewer/Audience)

| Question | Answer |
|----------|--------|
| Why not enhanced sampling first? | Need pre-commitment baseline first to define the right CV. Now we have it: (SASA, θ). |
| TIP3P appropriate? | Surface tension ~36 vs 72 mN/m — quantitative shift expected, not qualitative change. TIP4P/2005 cross-check planned. |
| What about the dimer? | Monomer = single-molecule mechanism baseline. Dimer adds steric (Loop CD/EF occluded), kinetic (must dissociate), orientational complexity. Next project. |
| Why JCIS not Nature/JACS? | Scope fit: characterising the pre-commitment ensemble + defining where unbiased MD stops. JCIS IF ~9 is the right community. |
| Is N_eff ≈ 17 enough? | Block bootstrap accounts for it. CI [−0.09, +0.11] rules out the coupling a two-factor gate needs. We are transparent about the limitation. |
| Most surprising finding? | 59 ns contact without commitment. Not noise — a real kinetic bottleneck. |

---

## Part 7 — The Research Arc

| Phase | What happened |
|-------|--------------|
| Initial analysis | Two-factor gate hypothesis — SASA and θ thresholds must coincide for adsorption |
| Round 5 review | Data integrity question raised — SASA values seemed too high |
| May 27 discovery | PBC artefact found: freeSASA without unwrap inflated SASA 2× (45–62 → 24–37 nm²) |
| Reframing | Gate-open events: 21 → 0. Paper reframed as "scope claim" — characterising the contact ensemble |
| May 30 | Figures rebuilt; auto-review Round 12 → 10/10 READY (Gemini 2.5 Flash, JCIS) |
| June 2 | Citation audit — 42 entries, 2 wrong-context fixes, TIP3P "one-third" → "half" |
| June 3 | Mac Mini set as primary workspace; slide docs fixed to match 15-slide deck |
| Pending | P.P. co-author review + Zenodo DOI → JCIS submission |

---

## Part 8 — Submission Checklist

- [ ] P.P. review — title, SET 1D removal, scope claim sign-off
- [ ] Zenodo upload → DOI → replace `10.5281/zenodo.XXXXXX` in `main.tex` (~line 828)
- [ ] JCIS highlights (5 bullets, ≤85 chars each)
- [ ] Graphical abstract — use Fig 4 KDE panel
- [ ] Cover letter
- [ ] Final `pdflatex` compile → zero warnings → 19 pages
- [ ] Submit at editorialmanager.com/jcis

---

## Part 9 — Glossary

| Term | Definition |
|------|-----------|
| BLG / β-Lactoglobulin | Dominant whey protein in bovine milk (~18 kDa); forms the calyx barrel structure |
| AWI | Air-water interface — the boundary between gas and liquid phases |
| Calyx | Hydrophobic barrel pocket of BLG; normally binds fatty acids; candidate for driving adsorption |
| SASA | Solvent Accessible Surface Area — how much protein surface is exposed to water |
| Nearest-atom metric | Contact declared when any heavy atom is within 0.3 nm of the Gibbs dividing surface |
| Gibbs dividing surface | Mathematical definition of the AWI plane; determined from water density profile |
| CoM distance | Centre-of-mass to interface distance — blind for BLG due to its 4 nm size |
| Contact event | Period where nearest-atom distance ≤0.3 nm (continuous) |
| Commitment | Stable, permanent adsorption — the protein stays at the AWI |
| Pearson r | Linear correlation coefficient — measures strength of linear relationship (−1 to +1) |
| Block bootstrap | Resampling method that preserves temporal autocorrelation; used to compute CIs for correlated time series |
| N_eff | Effective independent sample size = total time / (2 × autocorrelation time) |
| PBC | Periodic Boundary Condition — simulation box repeats; requires careful handling for surface calculations |
| mda_unwrap | MDAnalysis transformation that reassembles molecules split across PBC boundaries |
| RMSF | Root Mean Square Fluctuation — time-averaged flexibility of each residue |
| Rg | Radius of gyration — overall compactness measure |
| CHARMM36m | Force field (interaction parameters) optimised for proteins in solution |
| TIP3P | 3-site water model; underestimates surface tension (~36 vs 72 mN/m) |
| Enhanced sampling | MD techniques (metadynamics, REST2) that bias simulation to cross free energy barriers |
| CV / collective variable | The coordinate along which to bias — here: (SASA, θ) |
| PMF | Potential of Mean Force — free energy profile along a reaction coordinate |
