# Speaker Notes — Contact without Commitment
## COMFHA Lab Group · May 2026 · 20 min

---

## Slide 1 — Title [0:00–0:30]
*Wait for introduction, then:*
"Thank you. Today I'll take you through our first paper — 4 microseconds of watching BLG at the air-water interface. I'll keep it to 20 minutes."
→ *Advance*

---

## Slide 2 — Today's Story [0:30–1:00]
"Quick roadmap. Four acts — problem, approach, findings, what it means. The findings are the heart of the talk so I'll spend most time there."
→ *Advance: "Let me start with why this matters."*

---

## Slide 3 — Why Milk Foam? [1:00–2:00]
"BLG is the dominant stabiliser in milk. It adsorbs over seconds to minutes — that's already unusual. There's a measured kinetic barrier. The classical picture from Graham and Phillips says surface tension induces global unfolding. But nobody has watched this at atomic resolution. That's the gap we fill."
→ *Advance: "What has MD told us so far?"*

---

## Slide 4 — The Atomistic Gap [2:00–3:00]
"Experiments give time-averaged ensemble properties — tensiometry, ellipsometry. They don't see individual molecular events. Prior MD: all oil-water, protein pre-positioned, under 100 ns. So we know almost nothing about what actually happens when BLG approaches the air-water interface from bulk."
→ *Advance: "Here's what we built."*

---

## Slide 5 — System [3:00–4:00]
"12 by 12 by 35 nm slab. 7 nm of water with vacuum on each side creating two interfaces. CHARMM36m force field, TIP3P water. Four independent trajectories — one starting from bulk center, three starting 2 nm below the interface. Total: 4 microseconds."
*Point to Z-position panels:* "The blue trace is Z-position. You can see the protein touching the interface repeatedly."
→ *Advance: "But here's the key methodological point."*

---

## Slide 6 — Contact Metric [4:00–4:45]
"This is important. BLG is 4 nm wide. Even when an atom is touching the interface, the centre of mass stays 2-3 nm away. If you use a CoM cutoff — which is the standard approach — you see almost nothing. Switch to nearest-atom distance and you find 613 contact events. That's the difference."
→ *Advance: "So what does 4 microseconds actually look like?"*

---

## Slide 7 — Contact Frequent (AB) [4:45–6:00]
*Figure: Fig 2 AB — CENTER + R1*
"Here's CENTER and R1. The bottom panel shows contact events — every time the nearest atom crosses 0.3 nm. CENTER makes 97 events — 12.5% of frames. R1 makes 215 — 23% of frames. Single atoms penetrate up to 0.71 nm past the interface. The protein visits the interface *constantly*."
→ *Advance: "But look what happens to those events."*

---

## Slide 8 — Commitment Rare (CD) [6:00–7:00]
*Figure: Fig 2 CD — R2 + R3*
"R2 and R3 — same story. 613 total events across the whole dataset. But 607 of them terminate within 10 nanoseconds. That's the contact-commitment dichotomy. The protein touches and retreats. And the 6 that do stay longer — I'll show you those now."
→ *Advance*

---

## Slide 9 — Long-Event Table [7:00–7:45]
"These are the six long events. The one I want you to notice is R1, row 2 — 59 nanoseconds. That's not noise. But look at the SASA: 29.1 nm². Look at the angle: 63°. No activation. No commitment. 59 nanoseconds of sustained contact without adsorption. That's the kinetic bottleneck in action."
→ *Advance: "So what's happening structurally?"*

---

## Slide 10 — Global Compactness [7:45–8:45]
*Figure: Fig 3 panel (b) Rg*
"Panel b shows radius of gyration for R1. 1.496 nm, completely flat for 1000 ns. The beta-barrel RMSD stays around 0.21 nm. The alpha-helix is intact. Under 4 microseconds of unbiased dynamics, the protein never globally unfolds. The Graham and Phillips picture does not hold."
→ *Advance: "But the calyx is not static."*

---

## Slide 11 — Calyx Breathes [8:45–9:45]
*Figure: Fig 3 panel (a) SASA*
"Panel a is SASA over time in R1. It fluctuates between 24 and 37 nm² with a period of roughly 30-40 ns. This is not a one-shot opening before adsorption — it's a stationary stochastic process. The calyx is mobile throughout."
→ *Advance: "And here's something interesting about which loops drive that mobility."*

---

## Slide 12 — RMSF Loop Shift [9:45–11:00]
*Figure: Fig 3 panel (c) RMSF*
"Panel c is per-residue RMSF — blue is CENTER bulk, red is R1 near interface. In bulk, Loop BC at residues 30-35 is the dominant peak — 0.54 nm. Near the interface, something shifts. Loop CD/EF at residues 57-60 rises to 0.39 nm and becomes the dominant flexible region. Loop CD/EF sits directly above the calyx. This is an interface-induced conformational preference — activation is loop-mediated, not global."
→ *Advance: "Now let me show you the full SASA and orientation picture."*

---

## Slide 13 — SASA Distribution [11:00–12:00]
*Figure: Fig 4 panel (a) KDE*
"This is the SASA distribution for all four replicas overlaid. They're remarkably consistent — all confined to 24-37 nm². We define p95 at 32.1 nm² as a distribution-based threshold. No replica pushes into a clearly activated regime."
→ *Advance: "And the orientation?"*

---

## Slide 14 — Orientation Independent [12:00–13:15]
*Figure: Fig 4 panel (b) 2D heatmap*
"This is the 2D joint distribution — calyx angle versus SASA, all replicas combined. If SASA and orientation were coupled — if there were a two-factor gate — you'd see density concentrated in one corner. Instead it's uniform. Pearson r is plus 0.006. We swept across every reasonable threshold from 27 to 33 nm² and the result held. The two coordinates are independent."
→ *Advance: "But r=0.006 needs proper statistics."*

---

## Slide 15 — Block Bootstrap [13:15–14:15]
"SASA has an autocorrelation of 232 nanoseconds. That means the effective number of independent observations across 4 µs is only about 17. Standard confidence intervals would be wrong. We used block bootstrap with a 232 ns block length. The 95% CI is minus 0.09 to plus 0.11. We can rule out any coupling stronger than 0.11."
→ *Advance: "One thing I want to be transparent about."*

---

## Slide 16 — PBC Lesson [14:15–15:00]
"Midway through the project we found a PBC artefact. freeSASA without unwrapping the trajectory was splitting atoms across periodic boundaries — inflating SASA to 45-62 nm². Our original analysis showed 21 gate-open events and what looked like a 3.3x suppression effect. After applying MDAnalysis unwrap: SASA 24-37 nm², zero gate-open events. We disclose this fully in Methods. Everything you've seen uses corrected data."
→ *Advance: "So what does all of this add up to?"*

---

## Slide 17 — What This Means [15:00–16:30]
"The prior picture — contact leads to global unfolding leads to adsorption — doesn't fit. We see 59 ns of contact with no unfolding and no commitment. r = +0.006 rules out simple two-factor coupling. What we have is the first characterisation of the pre-commitment state. And that matters because you cannot design the right enhanced sampling calculation without knowing what the pre-commitment ensemble looks like."
→ *Advance: "Two practical implications."*

---

## Slide 18 — Implications [16:30–17:30]
"Loop CD/EF is the engineering target. If you want to mutate BLG to adsorb faster, increasing calyx flexibility is likely more effective than just increasing hydrophobicity. The dimer is more complex — it adds steric, kinetic, and orientational constraints — and that's our next simulation project. And the SASA-orientation baseline we've established works as a reference for the whole lipocalin family."
→ *Advance: "What's the path forward?"*

---

## Slide 19 — What's Next [17:30–18:00]
"Paper 1 is sitting at 10/10 in the auto-review — we're waiting on Zenodo DOI and P.P. sign-off before JCIS submission. The clear scientific next step is enhanced sampling along the (SASA, θ) coordinate. Paper 2 on beta-casein is started — AlphaFold2 structure ready. And we have BLG dimer simulations planned."
→ *Advance to summary*

---

## Slide 20 — Summary + Q&A [18:00–19:00]
"Three takeaways. Contact frequent, commitment absent — 613 visits, none stays. Compact globally, loop-mediated locally — Loop CD/EF is what matters near the interface. SASA and orientation independent on the µs timescale. Together these define precisely what 4 µs of unbiased MD resolves, and where enhanced sampling picks up. Thank you."

*[Q&A — 5-10 min]*

---

## Anticipated Questions

**Q: Why not use enhanced sampling from the start?**
A: Unbiased MD first establishes what *actually* happens — contact is far more frequent than expected, and commitment is absent. Without this baseline, you wouldn't know which collective coordinate to bias. Now we do: (SASA, θ).

**Q: Is TIP3P appropriate for the AWI?**
A: TIP3P underestimates surface tension by ~1/3 vs. experiment. We expect this shifts quantitative contact statistics — not the qualitative contact/commitment dichotomy. A TIP4P/2005 cross-check is in the pipeline.

**Q: What about the dimer? BLG is mainly dimeric in solution.**
A: The monomer is the right starting point for resolving single-molecule mechanism. The dimer adds three layers of complexity: steric (Loop CD/EF occluded), kinetic (dissociation required), orientational (oblate shape). We plan dimer simulations as the next phase.

**Q: How confident are you in the 613 event count?**
A: Very. The PBC-corrected gate analysis at full 0.1 ns resolution gives 613. The figure panels use 0.5 ns stride and show slightly fewer merged bands — this is explained in Methods. The event count is from full-resolution analysis.

**Q: Why JCIS and not a higher-profile journal?**
A: Scope fit. We characterise the pre-commitment ensemble and state precisely where unbiased MD ends. JCIS (IF ~9) is the right home for this type of mechanistic colloid-protein interface paper.
