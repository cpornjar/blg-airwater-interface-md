# Brief Me — COMFHA Research Summary
*Updated: May 30, 2026 — All figures publication-ready; fonts corrected; float placement fixed; /paper-figure audit complete*

---

## The One-Sentence Story

> **BLG touches the air-water interface frequently but almost never commits to stable residency.
> Calyx SASA (24–37 nm²) and orientation are independent of each other and of residency outcome
> on the microsecond timescale — the commitment step is not sampled by unbiased MD.**

---

## What the Data Actually Shows (post-PBC fix, May 27)

**PBC artifact was found and fixed.** `freesasa calcCoord` (not PBC-aware) split atoms across periodic boundaries, inflating SASA to 45–62 nm². Applied MDAnalysis `unwrap` transformation as fix.

| Claim | Old (artifact) | Corrected |
|-------|---------------|-----------|
| SASA max | 45–62 nm² | **24–37 nm²** |
| Gate-open frames | 0.27% (21 events) | **0 events** across 8006 frames |
| 3.3× suppression | Apparent | **Artifact — entirely gone** |
| Pearson r (SASA vs θ) | −0.085 | **+0.0057** (p=0.61; CI [−0.016, +0.028]) |
| R3 event 120–142 ns | "88.4% SASA>35" | **0% SASA>35** (real max 29.9 nm²) |

**The two-factor gate mechanism is not supported by corrected data.**

---

## Key Numbers (all verified, PBC-corrected)

| Quantity | Value | Status |
|----------|-------|--------|
| Total simulation time | **4.00 µs** (4 replicas × 1000 ns) | ✓ valid |
| Contact events | **613** (97 CENTER + 516 near-interface) | ✓ valid |
| Long events (≥ 10 ns) | **6** — all non-activated contact | ✓ verified |
| Per-event SASA | 28.5–30.5 nm² (event means) | ✓ verified |
| Per-event angle | 44–75° (well above 30° threshold) | ✓ verified |
| Rg (compact throughout) | **1.496 ± 0.009 nm** | ✓ valid |
| SASA (R1, pooled) | **29.08 ± 1.21 nm²; max 32.39 nm²** | ✓ PBC-corrected |
| Patch RMSD | 0.241 nm at 500 ns, 0.226 nm at 650 ns — **flat** | ✓ valid |
| Threshold (Fig 3) | **p95 = 32.10 nm²** (top 5% pooled distribution) | distribution-based |

---

## What Is Novel (unchanged from original framing)

- **First unbiased atomistic MD of native BLG at air-water interface** (all prior MD: oil-water, pre-stressed, or non-BLG)
- **Contact/commitment dichotomy:** prior CoM-distance studies missed 613 contact events
- **Precise boundary of unbiased MD:** SASA 24–37 nm², r = +0.006, p = 0.61 — calyx exposure and orientation are independent on µs timescale
- **Loop CD/EF shift at interface:** bulk → Loop BC (30–35); interface → Loop CD/EF (57–60)
- **All 6 long events non-activated:** commitment is not sampled even at 59 ns contact duration

---

## Paper Framing: Scope Claim (Option i)

Paper's positive contribution = characterising the pre-commitment contact ensemble and defining where unbiased MD stops.

**Framing sentence (Discussion opening):** The central finding is an atomistic characterisation of what the pre-commitment contact ensemble of native BLG at the air-water interface looks like, and a precise statement of where the boundary of unbiased µs MD lies.

---

## Literature Context

| Paper | What they found | How we differ |
|-------|----------------|---------------|
| **Beierlein et al. 2015** (*JPCB*) — SFG+MD | BLG orientation at AWI depends on ionic environment | They used bulk MD, not AWI slab; we characterise from first principles |
| **Eberini et al. 2004** (*Proteins*) | Glu89 protonation triggers Loop CD/EF reorganisation | Bulk MD, pH perturbation; same loop, different driver |
| **Zare et al. 2015/2016** (*Langmuir*) | BLG at decane-water: calyx toward oil; β-barrel survives | Oil≠air; 100 ns; pre-positioned |
| **Saurabh et al. 2024** (*Biophys J*) | mAb partially unfolds at water/vapour AWI | Pre-stressed conformations; not native fold |

---

## Figures (updated May 30 — /paper-figure audit complete; fonts corrected; float placement fixed)

| Figure | File | Format | DPI | Notes |
|--------|------|--------|-----|-------|
| Fig 2 AB | `PAPER_FIG2_CONTACT_AB.png` | PNG | 300 ✓ | `TITLE_CROP=0` (was 80 — was cutting into Z-position panel top); arrow annotations removed from inside panels; legend anchored below axes with reserved margin |
| Fig 2 CD | `PAPER_FIG2_CONTACT_CD.png` | PNG | 300 ✓ | Same fixes as AB |
| Fig 3 | `PAPER_FIG3_ACTIVATION.pdf` | **PDF** + PNG | 300 ✓ | figsize `(double_width, 4.6)` — renders 7.6pt in PDF (was 4pt at 13-inch figsize); panel (a) fill fixed to 22–37 nm² range; LaTeX `[t]→[htbp]` |
| Fig 4 | `Fig4_optionA.pdf` | **PDF** + PNG | 300 ✓ | KDE legend moved outside axes (bottom center); stats box removed (values in caption); LaTeX `[t]→[htbp]` |

Scripts: `detect_adsorption_contact.py` (all 4 panels regenerated), `make_fig2_ab_cd.py`, `make_fig3_activation.py`, `make_fig4_optionA.py`.

**May 30 figure fixes (this session):**
- Root cause of all previous overlap: elements were moved *within* axes rather than reserving margin space. Fix: gridspec `bottom=0.18+` and `bbox_to_anchor=(0.5, -0.22+)` for all legends.
- `TITLE_CROP=80` in PIL assembler was cutting top of Z-position panel (panels had no baked-in suptitle). Set to 0.
- Fig 3 figsize `double_width * 1.9 = 13 in` → LaTeX scaled to 0.5× → fonts at 4pt (unreadable). Fixed to `double_width = 6.85 in` → 0.95× → 7.6pt.
- `[t]` float placement with multiple backed-up floats deferred Fig 3+4 to end of paper. Fixed with `[htbp]`.
- Final PDF: **19 pages, 4.65 MB**. All figures appear near their `\ref{}` citations.

### ⚠ Known figure–text inconsistency (needs P.P. decision before submission)

The **event counts** in the figure label bars (97/215/156/145) come from `gate_analysis_all_replicas.py` (PBC-corrected, full 0.1 ns resolution) and match the paper text (613 total).

The **contact window shading** in the panels comes from `detect_adsorption_contact.py` at stride=5 (0.5 ns resolution), which gives 97/75/79/74 events — fewer because brief contacts separated by <0.5 ns gaps are merged.

A reader counting shaded bands in the figure will see fewer than the 215/156/145 stated in the caption. This is not wrong, but it needs a clarifying sentence in the Methods that event counts are from the full-resolution gate analysis, while figures show 0.5 ns resolution for clarity.

Also: R3 panel annotation shows "min −0.38 nm @ 123 ns" (detect, no PBC), but caption says "−0.48 nm @ 126 ns" (gate_analysis, PBC-corrected). Same event, different values — PBC correction shifts the minimum. Consider adding a note or using the gate_analysis value for the annotation.

---

## SET 1D — Retired from Paper, Kept as Database

**Decision (May 28):** SET 1D removed from paper (all mentions deleted from main.tex). Data kept for future comparison.

**What SET 1D found (preliminary, 45 ns):** Both 1Da (patch-down) and 1Db (patch-up) submerge into water within 2 ns regardless of calyx orientation. CoM 23→19 nm in 2 ns; calyx angle drifts to ~100° in both. Interpretation: protein exterior is hydrophilic — from the vacuum side, BLG always enters the water phase.

**Data location:** `outputs_BLG/SET1D/corrected/md_1Da.xtc` + `md_1Db.xtc`
**Use in future:** Baseline for enhanced-sampling comparison (metadynamics/REST2 follow-up paper).

---

## Questions a Reviewer May Ask

**Q: Why not observe actual adsorption?**
A: 4.00 µs unbiased MD resolves the contact ensemble. The commitment step requires enhanced sampling — that's exactly the scope claim we make.

**Q: Is Pearson r = +0.006 meaningful?**
A: No — that's the point. Bootstrap CI [−0.016, +0.028] rules out |r| > 0.03 at 95% confidence. SASA and orientation are independent on the µs timescale.

**Q: Is 6 long events enough?**
A: We don't make a mechanistic claim from the 6 events alone. We report SASA and angle distributions over 8006 contact frames. 6 events confirm the pattern, not the mechanism.

**Q: The old paper claimed 3.3× suppression — what happened?**
A: PBC artifact. freesasa without unwrap split atoms across boundaries. After fix: 0 gate-open events. We disclose this fully in Methods (PBC correction paragraph).

**Q: When can we submit?**
A: After co-author (P.P.) review of mechanism reframing and SET 1D removal. Target: **early June 2026**.

---

## Paper Status (May 30, 2026)

- **File:** `paper/latex/main.tex` (19 pages, 4.65 MB PDF)
- **Target venue:** Journal of Colloid and Interface Science (JCIS, IF ~9)
- **Auto-review:** Round 12 complete — Gemini 2.5 Flash: **10/10, READY** ✓ (best score; verdict upgraded from ALMOST to READY)
- **Round 12 trigger:** Figure quality improvements (May 30) — no remaining scientific weaknesses identified
- **Round 11 fixes (May 29):** Methods event-count resolution; Discussion pre-commitment framing; monomer/dimer limitation expanded
- **Score progression:** 5.5 → 6 → 6.5 → 7 → 7 → 7 → 7 → 4 (NatComm) → 7 → 8 → 9 → **10** (JCIS)
- **Remaining before submission:**
  - [ ] Co-author (P.P.) review — actual sign-off required
  - [ ] Zenodo upload → replace DOI placeholder in Data Availability (**hard blocker**)
  - [ ] Final compile + PDF check
  - [ ] JCIS submission portal

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/gate_analysis_all_replicas.py` | PBC-corrected SASA + orientation (with `mda_unwrap`) |
| `scripts/make_fig3_activation.py` | Fig 3 generator; RMSF cache-aware; p95=32.1 nm² |
| `scripts/precompute_rmsf.py` | Standalone RMSF precomputation (OOM-safe, one universe at a time) |
| `scripts/detect_adsorption_contact.py` | Canonical nearest-atom contact analysis |
| `scripts/verify_long_events.py` | Per-event SASA/angle verification (PBC-corrected) |

## Key Technical Gotchas

- **AlignTraj `step`**: goes in `.run(step=stride)`, NOT constructor — constructor causes OSError XTC write error
- **OOM**: Never load CENTER + R1 simultaneously; use `precompute_rmsf.py` one at a time
- **Python buffering**: Use `python3 -u` when piping to tee
- **AMD time**: cumulative, does NOT reset on restart (add to previous time)
- **NPT skip**: slab MD with protein in vacuum MUST skip NPT (semi-isotropic barostat crushes box)
