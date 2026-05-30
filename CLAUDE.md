# CLAUDE.md — COMFHA MILK_FROTHING Project

> Read this file at the start of every session. It is the authoritative project briefing.
> For detailed cheat-sheet with key numbers, read `brief_me.md`.

---

## Project Identity

**Lab:** COMFHA — Computational Modelling in Food, Health, and Agriculture  
**Institution:** Kasetsart University, Bangkok, Thailand  
**Team:** Chalakon Pornjariyawatch (PhD student) + Prapasiri Pongprayoon (supervisor, P.P.)  
**Goal:** Molecular mechanism of BLG adsorption at the air-water interface → explain milk foam stability

---

## Current Status (May 30, 2026)

**Paper 1 is READY for submission to JCIS.**
- Auto-review Round 12: Gemini 2.5 Flash scored **10/10, READY** ✓ (first READY verdict)
- All LaTeX edits complete. All figures publication-quality (fonts, layout, float placement fixed May 30).
- Pending: P.P. co-author review + Zenodo DOI (hard blocker) + JCIS portal.

---

## Critical Science Facts — Memorise These

### What happened to the two-factor gate?
**It was disproven by a PBC artifact.** freeSASA without MDAnalysis `unwrap` split protein atoms across periodic boundaries, inflating SASA to 45–62 nm². Real values: **24–37 nm²**. After fix: **0 gate-open events** across 8006 frames. The paper is now reframed as a scope claim.

### Current framing: Scope Claim
> "We characterise the pre-commitment contact ensemble of native BLG at the air-water interface and define precisely where unbiased µs MD stops."

### Key numbers (all PBC-corrected, verified)
| Quantity | Value |
|----------|-------|
| Total MD time | **4.00 µs** (4 × 1000 ns) |
| Contact events | **613** (97 CENTER + 516 near-interface) |
| Long events ≥ 10 ns | **6** — all non-activated contact |
| SASA range | **24–37 nm²** (mean 28.95 nm²) |
| Pearson r (SASA vs θ) | **+0.006**, block bootstrap 95% CI **[−0.09, +0.11]** |
| Effective N for r | **≈17** (SASA autocorrelation ~232 ns) |
| Rules out | |r| > 0.11 |
| Rg | **1.496 ± 0.009 nm** (globally compact, stable) |
| Patch RMSD | **~0.24 nm** flat — no progressive opening |

### SET 1D status
**Removed from paper.** Data kept at `outputs_BLG/SET1D/corrected/`. Will serve as baseline for future enhanced-sampling paper.

---

## Paper

- **File:** `paper/latex/main.tex` (813 lines)
- **Title:** "Contact without Commitment: Atomistic Characterisation of β-Lactoglobulin Adsorption Dynamics at the Air–Water Interface"
- **Target:** Journal of Colloid and Interface Science (JCIS, IF ~9)
- **PDF:** `paper/latex/main.pdf` (18 pages, compiled May 28)

### Figures
| Fig | File | Status |
|-----|------|--------|
| Fig 2 AB | `results/figures/PAPER_FIG2_CONTACT_AB.png` | ✓ May 30 — TITLE_CROP=0; legends below axes |
| Fig 2 CD | `results/figures/PAPER_FIG2_CONTACT_CD.png` | ✓ May 30 — same fixes |
| Fig 3 | `results/figures/PAPER_FIG3_ACTIVATION.pdf` | ✓ May 30 — figsize (6.85,4.6); 7.6pt fonts; [htbp] |
| Fig 4 | `results/figures/Fig4_optionA.pdf` | ✓ May 30 — legend outside; stats in caption; [htbp] |

---

## Environment & Tools

```bash
# Python environment
source ~/research-env/bin/activate
# MDAnalysis 2.10.0, freeSASA, matplotlib, numpy, notebooklm-py 0.5.0

# Gemini CLI (reviewer)
export PATH="$HOME/.npm-global/bin:$PATH"
export GEMINI_API_KEY=...   # in ~/.bashrc
export GEMINI_CLI_TRUST_WORKSPACE=true
# Usage: gemini -m gemini-2.5-flash -p "prompt"
# Note: gemini-2.5-pro has 0 free-tier quota; use flash

# NotebookLM
# Auth: ~/.notebooklm/profiles/default/storage_state.json (from MacBook login)
# Notebook ID: see notebooklm/ directory or run list script
# Script: python3 notebooklm/upload_to_notebooklm.py

# LaTeX
pdflatex paper/latex/main.tex   # installed, works
```

---

## Key Scripts

| Script | Purpose |
|--------|---------|
| `scripts/gate_analysis_all_replicas.py` | PBC-corrected SASA + orientation (uses `mda_unwrap`) |
| `scripts/make_fig3_activation.py` | Fig 3 — RMSF cache-aware, p95=32.1 nm² threshold |
| `scripts/precompute_rmsf.py` | Standalone RMSF (one universe at a time — OOM safe) |
| `scripts/detect_adsorption_contact.py` | Canonical nearest-atom contact analysis |
| `scripts/verify_long_events.py` | Per-event SASA/angle from PBC-corrected data |
| `scripts/block_bootstrap_r.py` | Block bootstrap for Pearson r CI |
| `notebooklm/upload_to_notebooklm.py` | Upload docs + generate audio/video in NotebookLM |

---

## Data Paths

```
outputs_BLG/CENTER/MD1000/md_1000ns.tpr        # CENTER topology
outputs_BLG/CENTER/MD1000/traj_comp.xtc        # CENTER trajectory (1000 ns)
outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc       # R1 trajectory (0–500 ns)
outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part00*.xtc  # R1 AMD extension parts
outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc + md_replica2_ext.part0002.xtc  # R2 1000 ns
outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc + md_replica3_ext.part0002.xtc  # R3 1000 ns
results/gate_analysis/{CENTER,R1,R2,R3}_gate.npz   # PBC-corrected gate data
results/gate_analysis/rmsf_{center,r1}.{resids,rmsf}.npy  # RMSF cache
```

---

## Review History

| Round | Reviewer | Score | Verdict |
|-------|----------|-------|---------|
| 1–4 | Opus 4.7 (internal) | 5.5→7/10 | not ready → almost |
| 5 | Opus 4.7 | data-integrity hold | PBC fix triggered |
| 6–7 | Opus 4.7 | n/a | option choice + LaTeX revision |
| 8 | Opus 4.7 (advisor) | 4/10 NatComm | not ready — critical fixes applied |
| 9 | Gemini 2.5 Flash | 7/10 JCIS | ALMOST READY |
| 10 | Gemini 2.5 Flash | 8/10 JCIS | ALMOST READY |
| 11 | Gemini 2.5 Flash | 9/10 JCIS | ALMOST READY |
| **12** | **Gemini 2.5 Flash** | **10/10 JCIS** | **READY ✓** |

Full log: `review-stage/AUTO_REVIEW.md`  
State: `review-stage/REVIEW_STATE.json`

---

## Technical Gotchas — Never Forget

1. **AlignTraj `step`**: goes in `.run(step=stride)`, NOT the constructor — constructor causes `OSError: XTC write error = compression`
2. **OOM**: Never load CENTER + R1 simultaneously — 11 GB machine. Use `precompute_rmsf.py` one universe at a time.
3. **Python buffering**: Use `python3 -u` when piping to tee — avoids silent block-buffered output
4. **AMD time**: cumulative, does NOT reset on job restart — add to prior time
5. **NPT skip**: slab MD with protein in vacuum MUST skip NPT — semi-isotropic barostat crushes box
6. **SASA without unwrap**: produces PBC artifact (SASA up to 70 nm²) — always use `mda_unwrap` first
7. **Gemini 2.5 Pro**: 0 free-tier quota — use `gemini-2.5-flash` instead
8. **NotebookLM API**: v0.5.0 uses `task_id` (not `id`), `generate_audio` returns `GenerationStatus`

---

## Submission Checklist (JCIS)

- [ ] P.P. review: title + SET 1D removal + scope claim
- [ ] Zenodo upload → DOI → update `main.tex` Data Availability
- [ ] JCIS highlights (5 bullets, ≤85 chars) — Claude can write
- [ ] Graphical abstract — use Fig 4 KDE panel
- [ ] Cover letter — Claude can draft
- [ ] Final `pdflatex` compile + check PDF
- [ ] Submit at editorialmanager.com/jcis

---

## NotebookLM Notebook

**Notebook:** "COMFHA Paper 1 — BLG Adsorption at Air-Water Interface"  
**Sources:** main.pdf, narrative_summary.md, brief_me.md, AUTO_REVIEW.md  
**Local outputs:** `notebooklm/study_guide.md`, `notebooklm/overview_podcast.mp3` (when downloaded)  
**Recreate:** `python3 notebooklm/upload_to_notebooklm.py` (after deleting old notebook)

---

## What Comes After Paper 1

| Paper | Topic | Status |
|-------|-------|--------|
| Paper 1 | BLG contact ensemble at AWI | **Submitting to JCIS** |
| Paper 2 | β-Casein at AWI | AlphaFold2 structure ready (`inputs_CAS/`) |
| Paper 3 | BLG + β-Casein + Ca²⁺ bridge | Planned |
| Paper 4 | Fat interaction (triglycerides) | Planned |
| Enhanced sampling | Metadynamics along (SASA, θ) | SET 1D data = baseline |
