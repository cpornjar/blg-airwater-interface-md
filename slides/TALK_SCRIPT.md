# Talk Script — Contact without Commitment
## COMFHA Lab Group Seminar · May 2026 · 20 slides · 20 min + Q&A
## Paper: 10/10 READY (Round 12, Gemini 2.5 Flash) · github.com/cpornjar/blg-airwater-interface-md

> **How to use this:** Read each slide section aloud during practice. Time yourself per slide. The transitions (→) are your cue to advance the slide. Q&A answers at the end — read them out loud too so the words feel natural.
>
> **Note on slide text:** Slides use ASCII approximations (us = µs, beta- = β, -> = →, nm2 = nm²). Speak the real words — microseconds, beta-lactoglobulin, etc.

---

## Slide 1 — Title [0:00–0:30]

*[Wait at title slide while the room settles. Don't rush.]*

"Good [morning/afternoon] everyone. Today I'm going to take you through our first paper on beta-lactoglobulin at the air-water interface. The title is 'Contact without Commitment' — and by the end I hope that phrase will be obvious to you. I'll keep to about 20 minutes."

→ *advance*

---

## Slide 2 — Today's Story [0:30–1:00]

"Quick roadmap before we start. Four acts. The problem — why this question has been open for decades. Our approach — what makes this simulation different from prior work. The findings — and there are three main results. And what it all means for where the field goes next. The findings are the heart of this talk so I'll spend most time there."

→ *advance: "Let me start with the problem."*

---

## Slide 3 — Why Milk Foam? [1:00–2:00]

"Beta-lactoglobulin is the dominant protein in whey — about 3 grams per litre in bovine milk. It's responsible for stabilising milk foam, and it does this by adsorbing at the air-water interface and forming a viscoelastic film that resists bubble coalescence.

Now, the interesting thing is that BLG adsorbs *slowly* — over seconds to minutes from bulk solution. That's unusual. There's a measured kinetic energy barrier that distinguishes BLG from more flexible proteins like beta-casein. The classical explanation, going back to Graham and Phillips in 1979, is that surface tension at the interface drives the protein to globally unfold, and that unfolding is what allows it to anchor.

But here's the thing — that picture has never been directly observed at atomic resolution. We don't actually know what the protein is doing at the interface on the way to adsorption."

→ *advance: "And that's where the MD field comes in — or rather, where it has been missing."*

---

## Slide 4 — The Atomistic Gap [2:00–3:00]

"Experimental methods — tensiometry, ellipsometry, neutron reflectometry — give us time-averaged surface properties. They tell us that BLG adsorbs and that the surface tension drops over seconds. But they don't resolve what individual protein molecules are doing during that process.

Prior MD studies of BLG at fluid interfaces have only looked at oil-water systems. And in those, the protein was pre-positioned near the interface and simulated for tens to hundreds of nanoseconds — nowhere near the timescale of real adsorption.

And crucially — *no atomistic simulation has been reported for BLG at the air-water interface.* The air-water surface tension is about 72 millinewtons per metre, versus roughly 20 for decane-water. Qualitatively different physics. This is the gap we fill."

→ *advance: "So what did we build?"*

---

## Slide 5 — System [3:00–4:00]

"Our system is a 12 by 12 by 35 nanometre slab. About 7 nanometres of TIP3P water in the middle, with vacuum on each side creating two independent air-water interfaces. Force field is CHARMM36m.

We ran four independent trajectories. SET 1A — which we call CENTER — starts with BLG at the geometric centre of the water slab. That's the unbiased bulk-start scenario. Then SET 1B — three replicas, R1, R2, R3 — each starts with the protein placed 2.18 nanometres below the upper interface.

Total cumulative simulation time: 4.00 microseconds. That's four times 1000 nanoseconds.

The figure shows the Z-position and contact events over time for CENTER and R1. But I'll come back to reading those in a moment."

→ *advance: "Before the results, one methodological point that turns out to matter a lot."*

---

## Slide 6 — Contact Metric [4:00–4:45]

"BLG is a roughly spherical protein, about 4 nanometres in diameter. If you use the centre-of-mass distance from the interface as your contact criterion — which is the standard approach in the literature — you get a number that stays around 2 to 3 nanometres even when the protein is physically touching the interface. The CoM just can't get close enough while the protein is still folded.

So we switched to nearest-atom distance. Contact is declared when any heavy atom comes within 0.3 nanometres of the Gibbs dividing surface. That resolves actual surface touch.

The difference is dramatic: with CoM distance, you detect essentially nothing. With nearest-atom at 0.3 nanometres, you find 613 contact events."

→ *advance: "So let me show you what those look like."*

---

## Slide 7 — Contact is Frequent (AB) [4:45–6:00]

"This is CENTER and R1. The blue trace at the top of each panel is the Z-position of the protein centre of mass. The orange/red bars at the bottom are the contact events — every time the nearest atom comes within 0.3 nanometres of the interface.

CENTER makes 97 contact events — that's 12.5% of all frames spent in contact. R1 makes 215 events — 23.4% of frames. Single atoms penetrate up to 0.71 nanometres past the interface plane.

The protein is not sitting in bulk waiting to adsorb. It is *constantly* visiting the interface. Contact is rapid and frequent."

→ *advance: "But look at what happens after those contacts."*

---

## Slide 8 — Commitment is Rare (CD) [6:00–7:00]

"R2 and R3 — 156 and 145 events respectively. Across all four trajectories, 613 contact events total.

But of those 613, only 6 sustain continuous contact above 10 nanoseconds. And none — not one — commits to stable adsorption. 607 events terminate within 10 nanoseconds and the protein retreats back into bulk.

This is what we call the contact-commitment dichotomy. Touching the interface is easy and frequent. Staying there is not."

→ *advance*

---

## Slide 9 — Long-Event Table [7:00–7:45]

"Let me show you the 6 long events explicitly, because they're important. The longest one — R1, second row — is 59 nanoseconds. That's not a brief fluctuation. It's 59 nanoseconds of the protein staying at the interface. And yet — look at the SASA column: 29.1 square nanometres. Look at the angle: 63 degrees. No activation. No commitment. The protein just... eventually leaves.

All 6 events have event-mean SASA between 28.5 and 30.5 square nanometres. Zero frames in any of them satisfy the activation criterion of SASA above 32.1. The contact-commitment dichotomy holds even at 59 nanoseconds."

→ *advance: "So what's happening structurally during all this?"*

---

## Slide 10 — Global Compactness [7:45–8:45]

"Panel b of Figure 3 — radius of gyration for R1 over 1000 nanoseconds. 1.496 plus or minus 0.009 nanometres — and completely flat. No trend toward expansion.

The beta-barrel backbone RMSD stays around 0.21 nanometres. The alpha-helix RMSD never exceeds 0.137 nanometres. The beta-barrel stays assembled. The helix stays intact.

Under 4 microseconds of unbiased dynamics, the protein never globally unfolds. The Graham and Phillips surface-denaturation picture — that interfacial adsorption requires global unfolding — does not describe what we observe. Whatever is happening at the interface, it isn't global structural collapse."

→ *advance: "But the calyx is not static."*

---

## Slide 11 — Calyx Breathes [8:45–9:45]

"Panel a of Figure 3 — hydrophobic SASA over time for R1. It fluctuates between 24 and 37 square nanometres. The dashed line is p95, the 95th percentile at 32.1 square nanometres.

The fluctuations happen on a timescale of roughly 30 to 40 nanoseconds. And critically — this is not a one-shot pre-adsorption event. It doesn't ramp up as the protein approaches the interface. It's a stationary stochastic process. The calyx has been opening and closing throughout the entire trajectory."

→ *advance: "And here's the structural reason why."*

---

## Slide 12 — Interface Shifts Loop [9:45–11:00]

"Panel c of Figure 3 — per-residue C-alpha RMSF. Blue is CENTER, the bulk simulation. Red is R1, near the interface.

In bulk — and this is the blue curve — Loop BC, residues 30 to 35, is the most flexible region. RMSF maximum of 0.54 nanometres.

Near the air-water interface, that hierarchy inverts. Loop CD/EF, residues 57 to 60, rises to 0.39 nanometres and becomes the dominant flexible region. Loop BC falls to 0.25 nanometres.

Loop CD/EF sits directly above the hydrophobic calyx. This inversion is an interface-induced conformational preference. The proximity to the air-water interface selects calyx-opening loop motions over the bulk-default Loop BC mobility.

Activation is loop-mediated and calyx-localised. Not global unfolding."

→ *advance: "Now the final piece of the puzzle — does the calyx exposure couple to orientation?"*

---

## Slide 13 — SASA Distribution [11:00–12:00]

"The left panel of Figure 4 is the KDE — kernel density estimate — of hydrophobic SASA for all four replicas. The distributions are remarkably consistent across replicas. All confined to 24–37 square nanometres. p95 sits at 32.1.

No replica pushes into a clearly distinct activated regime. The SASA distribution is continuous, not bimodal."

→ *advance: "And the orientation?"*

---

## Slide 14 — Orientation Independent [12:00–13:15]

"The right panel is the 2D joint distribution — calyx angle to the interface on the x-axis, hydrophobic SASA on the y-axis. All replicas combined. Each pixel's colour represents how many frames fell there on a log scale.

If SASA and orientation were coupled — if there were a two-factor gate where both had to be in the right regime simultaneously — you'd see the density concentrated in one corner. The top-left quadrant: high SASA, aligned orientation.

Instead it's completely uniform. All angles are equally represented at all SASA values.

Pearson r: plus 0.006. We tested this across every reasonable threshold — from 27 to 33 square nanometres — and Obs/Indep stays around 1.0 throughout. The two coordinates are independent."

→ *advance: "But we needed to be careful about the statistics here."*

---

## Slide 15 — Block Bootstrap [13:15–14:15]

"SASA has an autocorrelation time of 232 nanoseconds — that's the time over which successive values are no longer independent. If you apply standard confidence intervals, you're assuming independence between all 8006 frames. That assumption is wildly wrong.

We used block bootstrap with a block length of 232 nanoseconds. This gives an effective N of approximately 17 independent observations across the full 4 microseconds. The 95% confidence interval for r is minus 0.09 to plus 0.11.

We can confidently rule out any linear coupling stronger than 0.11 in absolute value. The conclusion stands: SASA and orientation are statistically independent on the microsecond timescale."

→ *advance: "Before I go to the implications — one thing I need to be transparent about."*

---

## Slide 16 — PBC Lesson [14:15–15:00]

"Midway through the project, we found a periodic-boundary-condition artefact in our original analysis. The freeSASA program, without applying MDAnalysis's unwrap transformation first, was computing SASA on protein coordinates that had been split across periodic boundaries. This inflated our SASA values to 45–62 square nanometres — and made it look like BLG was regularly activating.

After applying the fix — mda_unwrap on all 8006 gate-analysis frames — SASA dropped to 24–37 square nanometres and the gate-open event count went from 21 to zero.

We disclose this fully in the Methods section of the paper. Every number I've shown you today is from the corrected analysis."

→ *advance: "So — what does all of this add up to?"*

---

## Slide 17 — What This Means [15:00–16:30]

"The prior models said: contact leads to global unfolding leads to adsorption. Or: brief contacts don't matter. Neither holds.

59 nanoseconds of sustained contact without commitment is not sampling noise. It's a genuine kinetic bottleneck. The protein can stay at the interface for an extended time and still not commit.

r equals plus 0.006 rules out simple two-factor coupling — there's no pair of SASA and orientation thresholds that predicts commitment. Global fold is preserved — whatever triggers commitment is not the gross structural rearrangement that the classical picture invoked.

What we have is the first characterisation of the pre-commitment contact ensemble. And that matters because you cannot design the correct enhanced-sampling calculation — the one that will actually find the commitment mechanism — without knowing what the pre-commitment state looks like. Now we know."

→ *advance*

---

## Slide 18 — Implications [16:30–17:30]

"Two practical takeaways.

First, Loop CD/EF is the engineering target. If you want to make a BLG mutant that adsorbs faster — for better foam stability in a food product — the rational design strategy is to increase the flexibility of Loop CD/EF, not just to increase overall surface hydrophobicity. The interface selects calyx-opening motions. Enhance those.

Second, we simulated the monomer. BLG is predominantly dimeric above about 50 micromolar — which covers essentially all food-relevant concentrations. The dimer adds three layers of complexity: steric, because the dimer interface occludes Loop CD/EF; kinetic, because the dimer must dissociate before the calyx can present unobstructed; and orientational, because the oblate shape alters rotational diffusion. That's our next simulation project."

→ *advance*

---

## Slide 19 — What's Next [17:30–18:00]

"Three parallel tracks going forward.

Paper 1 — this work — is sitting at 10 out of 10 in our automated review. We're waiting on Zenodo DOI and P.P.'s sign-off before submitting to JCIS.

The scientific next step is enhanced sampling along the SASA-theta coordinate — metadynamics or umbrella sampling to characterise the commitment mechanism. We have SET 1D data as baseline starting conformations.

And Paper 2 on beta-casein is started. AlphaFold2 structure is ready. It will be an interesting comparison — beta-casein is intrinsically disordered and adsorbs much faster. Why? That's the question."

→ *advance to summary*

---

## Slide 20 — Summary [18:00–19:00]

"Three things to take away.

One: contact without commitment. BLG contacts the air-water interface in 7 to 23 percent of frames across all four trajectories. Only 6 events sustain 10 nanoseconds or more. None commits. Touching the interface is easy; staying there is not.

Two: compact globally, loop-mediated locally. The radius of gyration is flat throughout. The beta-barrel stays assembled. Loop CD/EF becomes the dominant flexible region near the interface — calyx mobility is driven by this loop, not by global unfolding.

Three: SASA and orientation are statistically independent on the microsecond timescale. r equals plus 0.006, block bootstrap 95% CI minus 0.09 to plus 0.11. No two-factor gate.

Together these establish what 4 microseconds of unbiased MD can and cannot tell us about BLG adsorption. Characterising the commitment mechanism requires enhanced sampling. That's the clear next step.

Thank you — I'm happy to take questions."

*[Smile. Wait. Don't fill the silence.]*

---

## Time Budget

| Slide | Topic | Target | Cumulative |
|:-----:|-------|:------:|:----------:|
| 1 | Title | 0:30 | 0:30 |
| 2 | Outline | 0:30 | 1:00 |
| 3 | Why foam | 1:00 | 2:00 |
| 4 | Atomistic gap | 1:00 | 3:00 |
| 5 | System | 1:00 | 4:00 |
| 6 | Contact metric | 0:45 | 4:45 |
| 7 | Contact frequent | 1:15 | 6:00 |
| 8 | Commitment rare | 1:00 | 7:00 |
| 9 | Long events table | 0:45 | 7:45 |
| 10 | Compact globally | 1:00 | 8:45 |
| 11 | Calyx breathes | 1:00 | 9:45 |
| 12 | Loop shift | 1:15 | 11:00 |
| 13 | SASA distribution | 1:00 | 12:00 |
| 14 | Orientation independent | 1:15 | 13:15 |
| 15 | Block bootstrap | 1:00 | 14:15 |
| 16 | PBC lesson | 0:45 | 15:00 |
| 17 | What it means | 1:30 | 16:30 |
| 18 | Implications | 1:00 | 17:30 |
| 19 | What's next | 0:30 | 18:00 |
| 20 | Summary | 1:00 | 19:00 |
| — | Buffer | 1:00 | 20:00 |

---

## Q&A Answers (read these out loud before the talk)

**Q: Why not use enhanced sampling from the start?**
"Unbiased MD first was the right call. Without it, we wouldn't know what the pre-commitment state looks like, and we'd have no basis for choosing the right collective coordinate to bias. Now we have both: the contact ensemble is characterised, and the SASA-theta plane is the obvious reaction coordinate space."

**Q: Is TIP3P appropriate for the air-water interface?**
"TIP3P underestimates surface tension by roughly half of experiment — about 36 versus 72 millinewtons per metre. We expect this shifts the quantitative statistics — contact frequency, event durations — rather than qualitatively changing the contact-commitment picture. A TIP4P/2005 cross-check is in the pipeline."

**Q: What about the dimer? BLG is mainly dimeric at physiological concentrations.**
"Completely valid point. The monomer is the right starting point for resolving the single-molecule mechanism. The dimer adds steric, kinetic, and orientational complexity that we'll address in dedicated dimer simulations. The monomer contact ensemble we've characterised is the baseline."

**Q: The event count — 215 for R1 — but the figure seems to show fewer bands?**
"Good catch. The 215 count comes from full 0.1 nanosecond resolution analysis. The figure panels use 0.5 nanosecond stride for visual clarity, which merges some brief events that are separated by gaps shorter than 0.5 nanoseconds. Both numbers are correct for their respective resolutions. We explain this in the Methods section."

**Q: Why JCIS and not a higher-impact journal?**
"Scope fit. We characterise the pre-commitment ensemble and define precisely where unbiased MD ends. That's a clean, honest result. JCIS is the right home for this type of mechanistic colloid-protein interface work — impact factor around 9, strong readership for exactly this community."

**Q: Is Pearson r = +0.006 meaningful, or is your effective N too small?**
"The effective N of 17 is low, yes. That's exactly why we used block bootstrap rather than assuming independence. The 95% CI of minus 0.09 to plus 0.11 accounts for that small N. We can't rule out very weak correlations below 0.11 — but we can rule out the kind of strong coupling that a two-factor gate model would require."

**Q: What's the most surprising finding?**
"For me, the 59-nanosecond event. The protein spends 59 nanoseconds at the interface and then just leaves. Nothing in the classical picture prepares you for that. It tells you that the commitment barrier is a genuine molecular event — not just timescale."

**Q: Could the interface itself be causing the Loop CD/EF shift?**
"Yes — that's exactly the interpretation. It's an interface-induced conformational preference. The air-water interface selects calyx-opening loop motions. It doesn't require contact — the proximity of the interface is enough to shift which loop dominates the dynamics. Eberini et al. showed that Glu89 protonation also triggers Loop CD/EF reorganisation in bulk, which suggests this loop is intrinsically primed for these dynamic responses."
