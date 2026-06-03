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

## Claude Operating Rules

> These rules apply every session. They exist to keep this workspace clean and prevent the chaos that accumulated on the Linux machine.

### File Placement — enforce strictly, no exceptions
| Type | Where it goes |
|------|--------------|
| Analysis scripts | `scripts/` |
| Output figures | `results/figures/` |
| Cached analysis data (.npz, .npy) | `results/gate_analysis/` |
| Paper files | `paper/latex/` |
| Science notes, literature | `docs/` |
| Presentation files | `slides/` |
| New simulation directories | `outputs_BLG/<NAME>/` or `outputs_CAS/<NAME>/` |
| Progress reports (PDF/PPTX) | `progress-reports/` |

**Never create files in the repo root.** Only these are allowed there: `CLAUDE.md`, `brief_me.md`, `CITATION_AUDIT.md`, `CITATION_AUDIT.json`, `ABOUT_ME.md`.

### Git Discipline
- Always run `git status` before any `git add`
- Stage specific files by name — never `git add .` or `git add -A`
- These extensions are permanently forbidden from commits: `.xtc .trr .tpr .gro .edr .cpt`
- Commit message format: `type: short description` where type is `fix` / `feat` / `chore` / `docs` / `analysis` / `paper`
- Always `git push origin main` after committing — Mac Mini is the single source of truth

### Cluster Discipline
- Before `sbatch`: always show the full script for review, wait for explicit "yes"
- Before any `rsync` to cluster: dry-run first (`-n` flag), show what will transfer
- **Never run `scancel`** — not even your own jobs without checking if they're still needed
- Your directories only: `/comfha/users/guest/PAO/` (ku-cluster) and `~/PAO/` (ku-ai)
- Never touch: `TK/`, `dodo/`, `Ben/`, `Prin/`, `S_coco/`, `paii/`, `Nan/`, `NAN/`, `nil/`

### Analysis Discipline
- Always activate: `conda activate research-env` (Python 3.12, MDAnalysis 2.10.0)
- Always use `python -u` when piping stdout to tee (prevents silent buffering)
- Always call `mda_unwrap` before freeSASA (PBC artifact prevention — the inflated 45–62 nm² bug)
- Never load CENTER + R1 universe simultaneously — 8 GB RAM, guaranteed OOM
- Key verified numbers — never change without rerunning analysis: 613 contacts, 6 long events, SASA 24–37 nm², Pearson r +0.006

### Slash Commands (7 custom — `~/.claude/commands/`)
| Command | What it does |
|---------|-------------|
| `/start-research` | Full session init: health check + cluster status + recommendation |
| `/check-cluster` | Live squeue from both clusters |
| `/sync-results <run>` | Dry-run then sync cluster → Mac Mini |
| `/submit-job <args>` | Generate + review + submit SLURM job |
| `/analyze <type>` | Run analysis script for gate/rmsd/rmsf/sasa/fig2/fig3/fig4 |
| `/paper-review <focus>` | Structured review against JCIS checklist |
| `/new-sim <args>` | Scaffold new simulation on local + cluster |

### ARIS Skills (27 — paper/research, from `~/aris_repo`)
| Skill | Use |
|-------|-----|
| `/auto-review-loop-llm` | Autonomous review loop → Gemini 2.5 Flash (external reviewer) |
| `/auto-paper-improvement-loop` | Full paper improvement cycle |
| `/citation-audit` | Audit all bib entries for wrong-context citations |
| `/paper-write` `/paper-compile` `/paper-figure` | Paper writing/compiling/figure work |
| `/novelty-check` `/kill-argument` `/rebuttal` | Competitive analysis and defence |
| `/research-review` `/research-refine` | Research quality improvement |
| `/semantic-scholar` `/arxiv` `/research-lit` | Literature search |
| `/analyze-results` `/result-to-claim` `/figure-spec` | Analysis → paper claims |
| `/idea-creator` `/idea-discovery` | Next paper ideation |
| `/gemini-search` | Gemini-powered web search |

### 9ARM Skills (4 — engineering discipline, from `~/9arm_repo`)
| Skill | Use |
|-------|-----|
| `/debug-mantra` | 4-step discipline before any bug fix: reproduce → trace → falsify → breadcrumb |
| `/scrutinize` | Cold outsider review of any script, plan, or change before running |
| `/post-mortem` | Document a fixed bug: root cause, mechanism, fix, how it slipped through |
| `/management-talk` | Rewrite technical content for P.P. / committee / non-engineering audience |

### ECC Cherry-picks (3 — from `~/ecc_repo`)
| Skill | Use |
|-------|-----|
| `/mle-workflow` | ML/scientific engineering workflow discipline |
| `/verification-loop` | Iterative result verification |
| `/eval-harness` | Structured evaluation framework |

### AI Review Backend
- Reviewer: **Gemini 2.5 Flash** (external, cross-model — preserves independence)
- MCP: `gemini-review` server + `llm-chat` server wired to Gemini OpenAI endpoint
- Advisor model: **Opus 4.8** (set in `~/.claude/settings.json`)
- For paper review: always use Gemini as external reviewer, not Claude self-review

---

## Current Status (June 2, 2026)

**Paper 1 is READY for submission to JCIS. Citation audit complete. LaTeX installed.**
- Auto-review Round 12: Gemini 2.5 Flash scored **10/10, READY** ✓
- Round 13 (June 2): dead GitHub URL fixed; bib comment updated
- **Citation audit (June 2):** 42 entries audited — 2 wrong-context citations fixed, 1 factual error in text fixed:
  - `Gochev2019JPCB` (neutron reflectometry, not kinetics) removed from kinetics claims; swapped for `Ulaganathan2017a`
  - `Foam4_2020` (foam stability) removed from adsorption-timescale claim
  - `Ulaganathan2017b` (rheology) removed from kinetics group
  - TIP3P surface tension: "one-third" → **"half"** (35.8 vs 72 mN/m)
- **Final compile (June 2):** MacTeX installed; `pdflatex` clean — **19 pages, zero warnings**
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

# ARIS Gemini reviewer (MCP bridge — replaces Gemini CLI)
# API key in ~/.gemini/.env (auto-loaded by server.py)
# MCP registered as: claude mcp add gemini-review -s user
# Default model: gemini-2.5-flash (Pro has 0 free-tier quota on this key)
# Invoke via ARIS skills with: — reviewer: agy

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
**Notebook ID:** `b0f185af-ca0d-4415-b74b-16c6392bbbff`  
**URL:** https://notebooklm.google.com (find by title or ID above)  
**Sources (12):** main.pdf, brief_me.md, narrative_summary.md, TALK_SCRIPT.md, speaker_notes.md, PRESENTATION_CHEATSHEET.md, SLIDE_OUTLINE.md, LITERATURE_REVIEW.md, COMFHA_Science_Notes.md, METHODS.md, AUTO_REVIEW.md, CITATION_AUDIT.md  
**Local symlinks:** all sources linked under `notebooklm/` — edit originals, they auto-reflect  
**Audio/Study Guide:** generate from web UI (click Generate in notebook)  
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
<!-- ARIS:BEGIN -->
## ARIS Skill Scope
ARIS skills installed in this project: 79 entries.
Manifest: `.aris/installed-skills.txt` (lists every skill ARIS installed and its upstream target).
For ARIS workflows, prefer the project-local skills under `.claude/skills/` over global skills.
Do not modify or delete files inside any skill that is a symlink (symlinks point into `/Users/cp/aris_repo`).
Update with: `bash /Users/cp/aris_repo/tools/install_aris.sh`  (re-runnable; reconciles new/removed skills).
<!-- ARIS:END -->