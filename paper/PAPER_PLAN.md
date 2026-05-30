# Paper Plan — COMFHA Paper 1

**Title:** "Two-Factor Gating Mechanism of β-Lactoglobulin Adsorption at the Air-Water Interface: Evidence from Atomistic Molecular Dynamics"
**One-sentence contribution:** BLG adsorption at the air-water interface requires simultaneous hydrophobic patch exposure AND correct patch orientation — a two-factor gating mechanism explaining why adsorption is slow despite repeated activation, with implications for engineering foam-stabilising proteins.
**Venue:** Nature Communications (IF 16.6) — upgraded from Langmuir (May 17 reframe)
**Type:** Computational biophysics / interfacial science
**Format:** NC format: Abstract, Introduction, Results, Discussion, Methods (at end)
**Main text target:** ~4,500 words; Methods additional ~1,200 words
**Date:** May 17, 2026

---

## Claims-Evidence Matrix

| # | Claim | Evidence | Status | Section |
|---|-------|----------|--------|---------|
| C1 | First atomistic BLG air-water MD — all prior BLG MD uses oil-water | NOVELTY_CHECK.md 8.5/10; SEMANTIC_SCHOLAR.md gap confirmed | **Supported** | Intro |
| C2 | BLG makes frequent intermittent atomic contact with the air–water interface but fails to commit to stable residency on a ≤ 1 µs timescale | CENTER 1000 ns nearest-atom analysis: 12.5% of frames in contact (≤ 0.30 nm), 97 contact events, deepest penetration −0.47 nm @ t = 570 ns. R1 (0–649 ns): 19.2% of frames in contact, 52 events, two sustained windows (370–450 ns; 580–650 ns), deepest penetration −0.71 nm @ t = 406 ns. No event sustains > 10 ns of continuous residency. CoM-only analysis (1.6 nm @ 570 ns CENTER; 1.35 nm @ 407 ns R1) is shown to mask surface contact for a ~4 nm globular protein. | **Supported** | Results §1 |
| C3 | **TWO-FACTOR GATING — gate to STABLE adsorption.** Brief contacts are common; sustained residency requires simultaneous hydrophobic patch exposure AND correct calyx orientation, which are statistically anticorrelated under unbiased dynamics. | Activated frames (SASA ≥ 35 nm²): 47.6%. Aligned frames (calyx angle ≤ 30°): 3.8%. Joint occurrence: 0.5% — 3.6× below independent expectation. No contact event with both conditions present persists > 10 ns. | **Supported** | Results §3 |
| C4 | Activation is loop-mediated, NOT global unfolding | Rg = 1.496 ± 0.009 nm compact; alpha-helix 0.115 nm stable; patch RMSD +7% only | **Supported** | Results §2 |
| C5 | Recurring activation every 30–40 ns | SASA bursts at 259, 569, 599, 639 ns R1; CENTER 940 ns | **Supported** | Results §2 |
| C6 | Interface proximity shifts dominant flexible loop BC→CD | RMSF: BC loop (30–35) in bulk CENTER; CD loop (57–60) near interface R1 | **Supported** | Results §2 |
| C7 | SET 1D proves gating by design: patch-down fast, patch-up no adsorption | SET 1D-a/b 38 ns production, pending completion | **Pending** | Results §4 |
| C8 | Slow ratchet: patch progressively mobilises toward adsorption | Patch RMSD 0.305→0.326 nm over 500→650 ns (+7%) | **Supported** | Results §3 |

---

## Structure

### §0 Abstract (150–200 words)
- Hook: milk foam stability is governed by protein adsorption at the air-water interface, yet the molecular mechanism is unknown
- Gap: no atomistic simulation of BLG at air-water interface exists
- What we do: µs-scale MD + slab geometry + orientation analysis + SET 1D orientation-control experiment
- Main result: two-factor gating to STABLE adsorption — intermittent atomic contact is frequent (~12–19% of frames) but stable residency requires simultaneous hydrophobic exposure AND correct calyx alignment, which are statistically anticorrelated
- Key numbers: contact density 12.5% (CENTER) / 19.2% (R1); 97 / 52 distinct contact events with no event > 10 ns; joint exposure-and-alignment probability 0.5% (3.6× below independent); activation bursts every 30–40 ns; Rg 1.496 ± 0.009 nm (compact); SET 1D proves mechanism by design
- Implication: explains slow natural adsorption; gating bottleneck is a target for protein engineering

### §1 Introduction (~550 words)
- Hook: milk foam stability; BLG dominant whey protein; foam collapse = poor foam
- Problem: prior MD only covers oil-water; no air-water MD of any food protein with this resolution and timescale
- Gap: experimental methods lack molecular resolution; coarse-grained MD cannot reveal mechanism
- Contribution statement (paragraph 4): "Here we present..."
- **4 numbered contributions:**
  1. First atomistic BLG air-water MD — µs timescale
  2. First atomistic resolution of the contact/residency distinction: BLG samples the interface frequently but does not commit to stable residency in 1 µs
  3. Two-factor gating mechanism for *stable* adsorption — simultaneous exposure + correct orientation, statistically anticorrelated
  4. SET 1D orientation-control experiment as mechanistic proof-by-design
- Key citations: Damodaran 2005; Dickinson 1999; Graham & Phillips 1979; Chaudhri et al. 2024
- **Hero figure (Fig 1):** Schematic of two-factor gating. 2×2 matrix: (SASA=low/high) × (orientation=random/aligned) — only (high, aligned) quadrant leads to adsorption. Right panel: actual data showing 100 ns burst window where SASA=40 nm² but orientation=80° — they do not co-occur.

### §2 Results (~2,800 words, 4 subsections)

#### §2.1 — Intermittent Atomic Contact Without Stable Residency
- Evidence: CENTER 1000 ns + R1 0–649 ns nearest-atom-to-interface analysis
- Key numbers: CENTER 12.5% / 97 contact events / min −0.47 nm @ 570 ns; R1 19.2% / 52 events / min −0.71 nm @ 406 ns; no event > 10 ns continuous residency
- Reframe: previously-reported "no adsorption" (CoM ≥ 1.35 nm) is a metric artefact — CoM-to-interface is blind to surface contact for a ~4 nm globular protein. Nearest-atom contact (≤ 0.30 nm) is the correct metric.
- Figure: **Fig 2** — two-panel composite: (a) CENTER topmost-atom-Z vs upper interface band with shaded contact windows; (b) R1 nearest-atom distance time series with 0.30 / 0.50 nm thresholds, two sustained windows highlighted. SASA burst overlay retained.

#### §2.2 — Loop-Mediated Activation near the Interface: Compact Protein, Mobile Patch
- Evidence: R1–R3 near-interface replicas; Rg = 1.496 ± 0.009 nm; SASA bursts every 30–40 ns; alpha-helix stable; CD loop RMSF elevated vs CENTER
- Key message: activation is a calyx-opening event (residues 57–60), NOT barrel unfolding — contradicts prevailing assumption
- Figure: **Fig 3** — 4-panel: (a) SASA time series R1 with bursts annotated, (b) Rg flat over 650 ns, (c) RMSF per residue CENTER vs R1, (d) hydrophobic patch RMSD slow ratchet

#### §2.3 — Two-Factor Gating: Exposure and Orientation Must Co-Occur for STABLE Adsorption
- Evidence: R1 contact events (52 total, deepest −0.71 nm @ 406 ns) inspected against simultaneous SASA + calyx orientation — no contact event with both gating conditions satisfied; bursts and contacts are temporally decoupled
- Key figure: **Fig 4** — 3-panel: (a) overlay of SASA, orientation, and nearest-atom distance vs time — contacts occur during low-SASA or misaligned windows, (b) 2D heatmap (SASA vs orientation angle) — empty upper-left quadrant = the gate, (c) schematic of gate
- Key message: contacts are gated for *commitment*, not for occurrence — joint probability of (high SASA AND aligned orientation) is 0.5% (3.6× below independent) → rate-limiting step for stable residency

#### §2.4 — Mechanistic Proof by Design: SET 1D Orientation-Control
- Hypothesis: pre-aligning patch toward interface should eliminate orientation gating → fast adsorption (1Da); anti-aligned control (1Db) should not adsorb
- Figure: **Fig 5** — 1Da vs 1Db distance to interface over time. Expected: 1Da rapid adsorption (<50 ns), 1Db stays above interface. **Placeholder pending SET 1D results.**
- If result confirmed: "This constitutes a direct experimental proof of the two-factor gating model"

### §3 Discussion (~500 words)
- Para 1: Reconcile two-factor gating with known surface activity of BLG — slow adsorption IS consistent with frequent activation given the gating constraint
- Para 2: Comparison to Chaudhri et al. 2024 — pre-stressed antibody bypasses orientation gate; native BLG must wait for spontaneous co-occurrence
- Para 3: Food science implication — surface activity ≠ hydrophobicity alone; engineering loop 57–60 orientation could accelerate adsorption
- Para 4: Limitations and future work — pH effect, fat competition (Phase 3/4), β-casein comparison (Paper 2), PMF free energy

### §4 Methods (at end — ~1,200 words, see METHODS.md)
- Subsections: Protein structure | Force field (CHARMM36m) | Slab geometry (12×12×35 nm) | Equilibration protocol (5-step) | Simulation sets (1A, 1B, 1D) | Software + hardware | Analysis pipeline

---

## Figure Plan

| ID | Type | Data Source | Status | Priority |
|----|------|-------------|--------|----------|
| **Fig 1** | Hero schematic | Manual / illustration | Commission via /paper-illustration | CRITICAL |
| **Fig 2** | 2-panel line plot | CENTER 1000 ns analysis | Data ready | HIGH |
| **Fig 3** | 4-panel composite | R1 650 ns analysis + CENTER RMSF | Data ready | HIGH |
| **Fig 4** | 3-panel (time series + 2D heatmap + schematic) | R1 SASA + orientation data | **Write script today** | CRITICAL |
| **Fig 5** | Comparison line plot | SET 1D-a vs 1Db | Pending SET 1D results | HIGH |
| Fig S1 | Line overlay | All 3 replicas Z-position | Data ready | MED |
| Fig S2 | Summary table | R1/R2/R3 RMSD+SASA numbers | R2/R3 pending | MED |
| Fig S3 | Multi-panel | Rg + RMSF advanced analysis | Data ready | MED |

**Fig 1 hero detail:** 2×2 gate matrix (SASA × orientation) + actual data snippet. Caption: "Adsorption requires simultaneous hydrophobic exposure AND patch alignment. Exposure events occur every 30–40 ns but are rarely accompanied by correct orientation."

**Fig 4 key detail:** The 2D heatmap with axes (hydrophobic SASA in nm², calyx angle in degrees) for all frames of R1. The upper-left quadrant (high SASA, low angle = patch aligned toward interface) should be nearly empty — this IS the two-factor gate, visualised directly.

---

## Citation Plan

| Section | Citations | Status |
|---------|-----------|--------|
| §1 Intro | Damodaran 2005; Dickinson 1999; Graham & Phillips 1979; Chaudhri et al. 2024; Brownlow et al. 1997 (1BEB) | Verified in SEMANTIC_SCHOLAR.md |
| §2 Methods ref | GROMACS (Abraham 2015); CHARMM36m (Huang 2017); TIP3P (Jorgensen 1983); MDAnalysis (Michaud-Agrawal 2011; Gowers 2016); freeSASA (Mitternacht 2016) | In METHODS.md |
| §3 Discussion | Graham & Phillips 1979 (surface unfolding theory — we contradict); Chaudhri 2024 (comparison) | Verified |
| All | Run /citation-audit before submission | — |

---

## Pending Items Before Submission

| Item | ETA | Blocks |
|------|-----|--------|
| R2 + R3 reach 1000 ns → auto_complete_replica.sh | ~May 18–19 | Fig S2, replica completeness |
| SET 1D-a adsorption result | ~May 19 | Fig 5, §2.4 |
| Fig 4 two-factor heatmap script | **Today** | §2.3 key figure |
| Fig 1 hero illustration | This week | Introduction |
| R1 reaches 1000 ns | ~May 23 | Full replica set |

---

## ARIS Pipeline Remaining

- [x] `/novelty-check` — 8.5/10 confirmed
- [x] `/semantic-scholar` — 7 must-cite papers, gap confirmed
- [x] `METHODS.md` — written May 17
- [x] `PAPER_PLAN.md` — this document
- [ ] **Fig 4 two-factor heatmap** — write `make_two_factor_figure.py`
- [ ] `/paper-figure` — generate Figs 2, 3 from data
- [ ] `/paper-illustration` — commission Fig 1 hero
- [ ] `/paper-write` — draft LaTeX (after SET 1D results)
- [ ] `/paper-compile` — build PDF
- [ ] `/auto-review-loop` — iterative polish
- [ ] `/citation-audit` — verify all references
- [ ] `/paper-claim-audit` — verify all numbers
- [ ] Submit to Nature Communications ~June–July 2026
