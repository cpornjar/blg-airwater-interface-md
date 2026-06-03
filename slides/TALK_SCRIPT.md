# Talk Script — Contact without Commitment
## COMFHA Lab Group Seminar · May 2026 · 15 slides · 20 min + Q&A
## Paper: 10/10 READY (Round 12, Gemini 2.5 Flash) · github.com/cpornjar/blg-airwater-interface-md

> **How to use this:** Read each slide section aloud during practice. Time yourself per slide.
> Transitions (→) are your cue to advance. Q&A answers at the end — read them aloud too.
> Note: slides use ASCII (us = µs, beta- = β, nm2 = nm²) — speak the real words.

---

## Slide 1 — Title [0:00–0:30]

*[Wait at title slide while the room settles.]*

"Good [morning/afternoon] everyone. Today I'm going to take you through our first paper on beta-lactoglobulin at the air-water interface. The title is 'Contact without Commitment' — and by the end I hope that phrase will be obvious to you. I'll keep to about 20 minutes."

→ *advance*

---

## Slide 2 — Today's Story [0:30–1:00]

"Quick roadmap. Four acts: the problem — why this question has been open for decades. Our approach — what makes this simulation different. The findings — three main results. And what it all means for the field. The findings are the heart of this talk."

→ *advance: "Let me start with the problem."*

---

## Slide 3 — The Problem [1:00–3:00]

"Beta-lactoglobulin is the dominant protein in whey — about 3 grams per litre in bovine milk. It stabilises milk foam by adsorbing at the air-water interface and forming a viscoelastic film that resists bubble coalescence.

BLG adsorbs slowly — over seconds to minutes. There's a measured kinetic energy barrier. The classical explanation, going back to Graham and Phillips in 1979, is that surface tension at the interface drives global unfolding. But that picture has never been directly observed at atomic resolution.

Experiments give time-averaged surface properties — they don't resolve individual molecular events. Prior MD on BLG was all oil-water, protein pre-positioned, under 100 nanoseconds. And the standard centre-of-mass metric is blind: BLG is 4 nanometres wide, so the CoM stays 2–3 nm away even when atoms are touching.

No unbiased atomistic simulation of native BLG at the air-water interface existed before this work. This is the gap we fill."

→ *advance: "Here's what we built."*

---

## Slide 4 — Our Approach [3:00–4:45]

"Our system is a 12 by 12 by 35 nanometre slab — about 7 nanometres of TIP3P water in the middle, with vacuum on each side. Force field: CHARMM36m.

Four independent trajectories. CENTER starts BLG at the geometric centre of the water slab — the unbiased bulk-start scenario. Then R1, R2, R3 each start with BLG 2.18 nanometres below the upper interface. Total: 4.00 microseconds.

Key methodological innovation: nearest-atom distance instead of CoM. Contact is declared when any heavy atom comes within 0.3 nanometres of the Gibbs dividing surface. With CoM: essentially zero events detected. With nearest-atom: 613 contact events."

→ *advance: "So what do those 613 events look like?"*

---

## Slide 5 — Finding 1: Contact Is Frequent [4:45–6:00]

"Center makes 97 contact events — 12.5% of all frames spent in contact. R1 makes 215 events — 23.4% of frames. Single atoms penetrate up to 0.71 nanometres past the interface plane.

The protein is not sitting in bulk waiting to adsorb. It is constantly visiting the interface. Contact is rapid and frequent."

→ *advance: "But look at what happens after those contacts."*

---

## Slide 6 — Finding 2: Commitment Is Absent [6:00–7:45]

"Across all four trajectories: 613 contact events. But of those 613, only 6 sustain continuous contact above 10 nanoseconds. And none — not one — commits to stable adsorption. 607 events terminate within 10 nanoseconds and the protein retreats.

Let me show you the 6 long events explicitly. The longest — R1 — is 59 nanoseconds. That's not a fluctuation. 59 nanoseconds at the interface, and then the protein just leaves. SASA: 29.1 nm². Angle: 63 degrees. No activation. No commitment.

All 6 events: event-mean SASA between 28.5 and 30.5 nm². Zero frames in any of them satisfy the activation criterion.

This is the contact-commitment dichotomy. Touching the interface is easy. Staying is not."

→ *advance: "What's happening structurally during all this?"*

---

## Slide 7 — Finding 3: Compact Globally, Breathing Locally [7:45–9:45]

"Radius of gyration for R1 over 1000 nanoseconds: 1.496 plus or minus 0.009 nanometres — completely flat. Beta-barrel RMSD stays around 0.21 nanometres. Alpha-helix RMSD never exceeds 0.137 nanometres. Under 4 microseconds of unbiased dynamics, the protein never globally unfolds. The Graham and Phillips surface-denaturation picture does not describe what we observe.

But the calyx is not static. Hydrophobic SASA fluctuates between 24 and 37 square nanometres — period roughly 30 to 40 nanoseconds. And critically — this is not a one-shot pre-adsorption event. It doesn't ramp up as the protein approaches. It's a stationary stochastic process throughout the entire trajectory. The calyx has been opening and closing the whole time."

→ *advance: "And here's the structural reason why."*

---

## Slide 8 — Finding 4: Interface Shifts Which Loop Opens [9:45–11:00]

"Per-residue RMSF. Blue is CENTER — bulk. Red is R1 — near the interface.

In bulk: Loop BC, residues 30 to 35, is the most flexible region. RMSF maximum of 0.54 nanometres.

Near the air-water interface: Loop CD/EF, residues 57 to 60, rises to 0.39 nanometres and becomes the dominant flexible region. Loop BC falls to 0.25. The hierarchy inverts.

Loop CD/EF sits directly above the hydrophobic calyx. This is an interface-induced conformational preference. Proximity to the AWI selects calyx-opening loop motions. Activation is loop-mediated and calyx-localised — not global unfolding. And this identifies Loop CD/EF as the engineering target for rational mutant design."

→ *advance: "Does the calyx exposure couple to orientation?"*

---

## Slide 9 — Finding 5: SASA and Orientation Are Independent [11:00–13:15]

"Left panel — kernel density estimate of hydrophobic SASA across all four replicas. Consistent, confined to 24–37 nm². p95 sits at 32.1. No replica pushes into a clearly distinct activated regime.

Right panel — 2D joint distribution. Calyx angle to the interface on the x-axis, hydrophobic SASA on the y-axis. All replicas combined.

If SASA and orientation were coupled — a two-factor gate — you'd see density concentrated in one corner. High SASA, aligned orientation. Instead: completely uniform. All angles are equally represented at all SASA values.

Pearson r: plus 0.006. We tested every reasonable threshold from 27 to 33 nm² — Obs/Indep stays around 1.0 throughout. The two coordinates are statistically independent."

→ *advance: "But we needed to be careful about the statistics."*

---

## Slide 10 — The Statistics [13:15–14:15]

"SASA has an autocorrelation time of 232 nanoseconds. Effective N across 4 microseconds: about 17. Standard confidence intervals assuming frame independence would be completely wrong.

We used block bootstrap with 232 ns block length. 95% CI for r: minus 0.09 to plus 0.11. We can confidently rule out any linear coupling stronger than 0.11 in absolute value. The conclusion stands."

→ *advance: "Before implications — one thing I want to be transparent about."*

---

## Slide 11 — Scientific Integrity [14:15–15:00]

"Midway through the project, we found a PBC artefact in our original analysis. freeSASA without MDAnalysis unwrap split protein atoms across periodic boundaries and inflated SASA to 45–62 nm² — making it look like BLG was regularly activating.

After the fix: SASA 24–37 nm², zero gate-open events. We disclose this fully in the Methods. Everything I've shown you today is from the corrected analysis."

→ *advance: "So what does all of this add up to?"*

---

## Slide 12 — What This Work Establishes [15:00–16:30]

"Prior models said: contact leads to unfolding leads to adsorption. Or: brief contacts don't matter. Neither holds.

59 nanoseconds of sustained contact without commitment is a genuine kinetic bottleneck. r = +0.006 rules out simple two-factor coupling. Global fold is preserved throughout.

What we have is the first atomistic characterisation of the pre-commitment contact ensemble of native BLG at the air-water interface. That matters because you cannot design the correct enhanced-sampling calculation without knowing what the pre-commitment state looks like. Now we know. Three findings in one sentence: contact is frequent, commitment is absent, SASA and orientation are independent."

→ *advance*

---

## Slide 13 — Implications [16:30–17:30]

"Three concrete takeaways for the field.

First, Loop CD/EF is the engineering target. If you want a BLG mutant that adsorbs faster, increase flexibility of Loop CD/EF — not just bulk hydrophobicity. The interface selects calyx-opening motions.

Second, enhanced sampling now has a well-defined collective variable: the (SASA, θ) plane. Metadynamics or REST2 can now compute the free energy barrier for commitment with a physically motivated CV.

Third — conceptually — slow BLG adsorption is not a diffusion problem. Contact is frequent. The bottleneck is orientational and conformational coincidence. Prior kinetic models based on diffusion need revision."

→ *advance*

---

## Slide 14 — What Comes Next [17:30–18:00]

"Three tracks. Paper 1 — this work — is sitting at 10 out of 10 in auto-review. Waiting on Zenodo DOI and P.P. sign-off before JCIS.

The next simulation is enhanced sampling along (SASA, θ) — metadynamics to characterise the commitment mechanism and quantify the barrier.

And Paper 2 on beta-casein starts July 2026. AlphaFold2 structure is ready. Beta-casein is intrinsically disordered and adsorbs much faster than BLG. Why? That's the question."

→ *advance to summary*

---

## Slide 15 — Summary [18:00–19:00]

"Three things to take away.

One: contact without commitment. 613 contact events across 4 microseconds. Only 6 sustain 10 ns or more. None commits. Touching is easy; staying is not.

Two: compact globally, loop-mediated locally. Radius of gyration flat at 1.496 nanometres. Loop CD/EF becomes the dominant flexible region near the interface. No global unfolding.

Three: SASA and orientation are statistically independent on the microsecond timescale. r = +0.006, block bootstrap 95% CI [−0.09, +0.11].

Together these establish what 4 microseconds of unbiased MD can and cannot tell us about BLG adsorption. The commitment mechanism requires enhanced sampling. That is the clear next step.

Thank you — happy to take questions."

*[Smile. Wait. Don't fill the silence.]*

---

## Time Budget

| Slide | Topic | Target | Cumulative |
|:-----:|-------|:------:|:----------:|
| 1 | Title | 0:30 | 0:30 |
| 2 | Story | 0:30 | 1:00 |
| 3 | Problem | 2:00 | 3:00 |
| 4 | Approach | 1:45 | 4:45 |
| 5 | Finding 1 — Contact Frequent | 1:15 | 6:00 |
| 6 | Finding 2 — Commitment Absent | 1:45 | 7:45 |
| 7 | Finding 3 — Compact/Breathing | 2:00 | 9:45 |
| 8 | Finding 4 — Loop Shift | 1:15 | 11:00 |
| 9 | Finding 5 — SASA Independent | 2:15 | 13:15 |
| 10 | Statistics | 1:00 | 14:15 |
| 11 | Scientific Integrity | 0:45 | 15:00 |
| 12 | What Establishes | 1:30 | 16:30 |
| 13 | Implications | 1:00 | 17:30 |
| 14 | What's Next | 0:30 | 18:00 |
| 15 | Summary | 1:00 | 19:00 |
| — | Buffer | 1:00 | 20:00 |

---

## Q&A Answers (read these aloud before the talk)

**Q: Why not use enhanced sampling from the start?**
"Unbiased MD first was the right call. Without it, we wouldn't know what the pre-commitment state looks like, and we'd have no basis for choosing the right collective coordinate. Now we have both: the contact ensemble is characterised, and the (SASA, θ) plane is the obvious reaction coordinate."

**Q: Is TIP3P appropriate for the air-water interface?**
"TIP3P underestimates surface tension by roughly half of experiment — about 36 versus 72 millinewtons per metre. We expect this shifts quantitative statistics — contact frequency, event durations — rather than qualitatively changing the contact-commitment picture. A TIP4P/2005 cross-check is in the pipeline."

**Q: What about the dimer? BLG is mainly dimeric at physiological concentrations.**
"The monomer is the right starting point for resolving the single-molecule mechanism. The dimer adds steric, kinetic, and orientational complexity that we'll address in dedicated dimer simulations. The monomer contact ensemble is the baseline."

**Q: The event count — 215 for R1 — but the figure seems to show fewer bands?**
"The 215 count comes from full 0.1 nanosecond resolution analysis. The figure uses 0.5 nanosecond stride for visual clarity, which merges some brief events. Both numbers are correct for their resolution. We explain this in Methods."

**Q: Why JCIS and not a higher-impact journal?**
"Scope fit. We characterise the pre-commitment ensemble and define where unbiased MD ends. JCIS is the right venue for mechanistic colloid-protein interface work — impact factor around 9, strong readership."

**Q: Is r = +0.006 meaningful with N~17?**
"The effective N of 17 is why we used block bootstrap. The 95% CI of [−0.09, +0.11] accounts for that small N. We can rule out the strong coupling that a two-factor gate would require."

**Q: What's the most surprising finding?**
"59 nanoseconds of contact without commitment. Not noise. A real kinetic bottleneck."

**Q: Loop CD/EF shift — is it caused by the interface?**
"Yes — interface-induced conformational preference. Proximity selects calyx-opening motions. Eberini et al. also showed Glu89 protonation triggers Loop CD/EF reorganisation in bulk — intrinsically primed."
