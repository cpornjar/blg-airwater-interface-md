# Speaker Notes — Contact without Commitment
## COMFHA Lab Group · May 2026 · 15 slides · ~20 min

> Slide numbers match presentation_final.pptx / .key (15-slide deck).
> ASCII on slides: us = µs, beta- = β, nm2 = nm², perp = independent

---

## S1 — Title [0:00–0:30]
*Wait for room to settle.*
"Good morning everyone. Today I'll take you through our first paper — Contact without Commitment. I'll keep to about 20 minutes."
→ *advance*

---

## S2 — Today's Story [0:30–1:00]
"Quick roadmap. Four acts: the problem, our approach, the findings, and what it means. The findings are the heart of it so I'll spend most time there."
→ *advance: "Let me start with the problem."*

---

## S3 — The Problem [1:00–3:00]
"BLG is the dominant protein in whey — about 3 g/L in bovine milk. It stabilises milk foam by forming a viscoelastic film at the air-water interface. Adsorption is slow — seconds to minutes — and there's a measured kinetic barrier. The classical explanation from Graham and Phillips is global unfolding driven by surface tension. But that has never been directly observed at atomic resolution.

Experiments give time-averaged surface properties — they don't resolve individual molecular events. Prior MD on BLG was all oil-water, protein pre-positioned, under 100 ns. And no atomistic simulation of BLG at the air-water interface had been reported. The CoM distance metric is also blind: BLG is 4 nm wide, so CoM stays 2–3 nm away even when atoms are touching. We fill all three gaps."
→ *advance: "Here's what we built."*

---

## S4 — Our Approach [3:00–4:45]
"12 by 12 by 35 nm slab. CHARMM36m force field, TIP3P water. Four trajectories: CENTER from bulk, R1 R2 R3 from 2.18 nm below the interface. Total: 4 microseconds.

Key innovation: nearest-atom metric at 0.3 nm. With CoM distance you detect essentially nothing. With nearest-atom you find 613 contact events."
→ *advance: "So what does 4 microseconds look like?"*

---

## S5 — Finding 1: Contact Is Frequent [4:45–6:00]
*[Point to figure]*
"CENTER makes 97 events — 12.5% of frames. R1 makes 215 — 23.4% of frames. Single atoms penetrate up to 0.71 nm past the interface. The protein visits the interface constantly."
→ *advance: "But look at what happens to those events."*

---

## S6 — Finding 2: Commitment Is Absent [6:00–7:45]
"613 total events across 4 trajectories. Only 6 sustain above 10 nanoseconds. And none — not one — commits to stable adsorption. 607 events terminate within 10 ns and the protein retreats.

The 6 long events explicitly: the longest — R1 — is 59 nanoseconds. SASA 29.1 nm². Angle 63°. No activation. No commitment. All 6 events: SASA 28.5–30.5 nm², zero activation-criterion frames.

This is the contact-commitment dichotomy. Touching is easy and frequent. Staying is not."
→ *advance: "What's happening structurally?"*

---

## S7 — Finding 3: Compact Globally, Breathing Locally [7:45–9:45]
*[Point to Rg panel]*
"Rg for R1: 1.496 nm, completely flat for 1000 ns. Beta-barrel RMSD 0.21 nm. Alpha-helix intact. The protein never globally unfolds. The Graham and Phillips surface-denaturation picture does not hold.

*[Point to SASA panel]*
But the calyx is not static. SASA fluctuates 24–37 nm², period roughly 30–40 ns. Not a one-shot pre-adsorption event — a stationary stochastic process throughout. The calyx has been opening and closing the entire time."
→ *advance: "And here's the structural reason."*

---

## S8 — Finding 4: Interface Shifts Which Loop Opens [9:45–11:00]
*[Point to RMSF panel]*
"In bulk: Loop BC, residues 30–35, is dominant — RMSF 0.54 nm.

Near the AWI: Loop CD/EF, residues 57–60, rises to 0.39 nm. Loop BC falls to 0.25. Loop CD/EF sits directly above the calyx. Interface-induced conformational preference. Activation is loop-mediated and calyx-localised — not global unfolding."
→ *advance: "Does calyx exposure couple to orientation?"*

---

## S9 — Finding 5: SASA and Orientation Are Independent [11:00–13:15]
*[Point to KDE panel]*
"All four replicas — consistent, confined to 24–37 nm². p95 at 32.1. No replica pushes into a distinct activated regime.

*[Point to 2D heatmap]*
2D joint distribution. If SASA and orientation were coupled — a two-factor gate — density would cluster in one corner. Instead it's completely uniform. Pearson r: plus 0.006. Threshold sweep from 27–33 nm² — Obs/Indep stays around 1.0 throughout. The two coordinates are independent."
→ *advance: "But we needed proper statistics."*

---

## S10 — The Statistics [13:15–14:15]
"SASA autocorrelation: 232 nanoseconds. Effective N: about 17 across 4 microseconds. Standard CIs assuming independent frames are wildly wrong.

Block bootstrap with 232 ns block length: 95% CI minus 0.09 to plus 0.11. Confidently rules out any coupling stronger than 0.11."
→ *advance: "One thing I need to be transparent about."*

---

## S11 — Scientific Integrity [14:15–15:00]
"Midway through the project we found a PBC artefact. freeSASA without unwrapping inflated SASA to 45–62 nm². After MDAnalysis unwrap: 24–37 nm², zero gate-open events. Full disclosure in Methods. Everything you've seen today is PBC-corrected."
→ *advance: "So what does all of this add up to?"*

---

## S12 — What This Work Establishes [15:00–16:30]
"Prior models: contact leads to unfolding leads to adsorption — or brief contacts don't matter. Neither holds.

59 ns contact without commitment is a genuine kinetic bottleneck. r = +0.006 rules out simple two-factor coupling. Global fold is preserved.

We have the first characterisation of the pre-commitment contact ensemble — the required foundation before enhanced sampling can be designed and interpreted."
→ *advance*

---

## S13 — Implications [16:30–17:30]
"Loop CD/EF is the engineering target. Mutations increasing calyx flexibility should accelerate adsorption.

Enhanced sampling now has a well-defined CV: (SASA, θ). Metadynamics or REST2 can compute the commitment barrier.

And conceptually: slow adsorption is not a diffusion problem — contact is frequent. The bottleneck is orientational and conformational coincidence."
→ *advance*

---

## S14 — What Comes Next [17:30–18:00]
"Paper 1 is at 10/10 — waiting on Zenodo DOI and P.P. sign-off before JCIS. Enhanced sampling along (SASA, θ) is the clear next step. Paper 2 on beta-casein starts July 2026."
→ *advance to summary*

---

## S15 — Summary [18:00–19:00]
"Three takeaways. Contact frequent, commitment absent — 613 visits, none stays. Compact globally, loop-mediated locally — Loop CD/EF drives calyx mobility near the AWI. SASA and orientation independent on the microsecond timescale.

Together these define what 4 microseconds of unbiased MD can and cannot tell us. Thank you."

*[Smile. Wait. Don't fill the silence.]*

---

## Q&A Prep

**Why not enhanced sampling first?**
Need this baseline to know the right reaction coordinate. Now we have both.

**TIP3P appropriate?**
Surface tension ~36 vs 72 mN/m; expect quantitative shift, not qualitative change. TIP4P/2005 cross-check planned.

**What about the dimer?**
Monomer = single-molecule mechanism baseline. Dimer adds steric (Loop CD/EF occluded), kinetic (dissociation required), orientational (oblate shape). Next phase.

**Event count vs figure bands?**
613 from full 0.1 ns resolution. Figures use 0.5 ns stride — fewer merged bands. Both correct; Methods explains this.

**Why JCIS not higher-impact?**
Scope fit. JCIS IF ~9 is right for mechanistic colloid-protein interface work.

**r = +0.006 with N~17?**
Block bootstrap accounts for small N. CI [−0.09, +0.11] rules out strong coupling.

**Most surprising?**
59 ns contact without commitment — real kinetic bottleneck, not noise.

**Loop CD/EF shift — interface-caused?**
Yes — interface-induced conformational preference. Proximity selects calyx-opening motions. Eberini et al. showed Glu89 protonation also triggers this loop in bulk — intrinsically primed.
