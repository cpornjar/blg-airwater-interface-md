# P.P. Feedback Log — Canonical Record

> **This file is the single source of truth for supervisor (Prapasiri Pongprayoon, "P.P.")
> feedback, decisions, and open questions.** Before this file existed, the same information
> was scattered across `CLAUDE.md`'s "Open questions for P.P." line, `docs/paper1_expansion_plan.md`,
> and several `~/.claude/projects/.../memory/` entries — none of them kept in sync with each other.
> Read this file at the start of every session (`/start-research` prints the open-items summary
> automatically). Update it every time P.P. gives feedback, in a meeting, on LINE, or via email —
> log it here the same day, not just in memory.
>
> Format per entry: **Date** · **Context** (where it came from) · **What she said/decided**
> · **Status** (🔴 OPEN — needs an answer or action / 🟡 IN PROGRESS / 🟢 RESOLVED) ·
> **Source** (the doc/memory this was cross-checked against).

---

## 🔴 OPEN — needs action or a decision now

### 1. IFSC2026 abstract deadline — TIME-SENSITIVE, re-verify immediately
**Date raised:** 2026-07-15 (P.P. relayed via LINE) · **Status:** 🔴 OPEN, urgent
P.P. relayed that the faculty wants DPST students to present at **IFSC2026** (17th
International Fundamental Science Congress, Nov 12–13 2026, KU Faculty of Science) and
asked whether the work would be ready and "enough for a poster." Key dates verified
against https://www.sci.ku.ac.th/ifsc2026/#registration **on 2026-07-15** (now ~7 weeks
stale, **re-verify the page before relying on this date**):
- Abstract deadline: **Sept 25, 2026** — as of this log entry (Sept 4), **21 days away**
- Notification: Oct 9 · Early-bird registration: Oct 12 · Conference: Nov 12–13
- Poster size: 60cm(W) × 110cm(H) portrait

**Assessment given at the time:** BLG alone (4µs MD, disproven gate mechanism, backed by
the July 9 lit review) was poster-ready as of July. CAS was mid-pipeline. 4-month runway
gave real buffer even with CAS "in progress" on the poster.

**Concrete recommendation already drafted** (`docs/PP_meeting_talking_points_2026-07-16.md`,
Fable-reviewed prep notes for this exact meeting — found on a second, more thorough pass of
this backfill, missed the first time): **lead BLG-only as the complete story, present CAS
as an explicit "in progress" preview, submit the abstract, do NOT headline the comparative
title ("An Accessible Calyx and an Open Chain") until CAS production data exists.** The
poster degrades gracefully — BLG stands alone today, any CAS data by November is a bonus.
That doc also owns 3 self-flagged weak points worth re-reading before any P.P. conversation:
(1) surface tension "51.9 ± 38.5 mN/m matches literature" overstates precision — ±38.5 is
the *instantaneous* SD, not SEM on the mean; report block-averaged SEM instead. (2) the null
result was framed as "decoupled/positive," which a skeptic reads as overreach — soften to
"no coupling detected within these limits." (3) R2 replica question — already resolved
per R2 below, this doc just needed the position stated out loud in the room.

**`progress-reports/PP_status_report_IFSC2026_2026-07-16.pdf` (formal version of the same
July 16 report, checked during this backfill's third pass) closes with 5 explicit "Open
Questions for P.P.":** (1) poster framing — BLG-only vs. BLG+CAS-in-progress, **still open**,
(2) is "in progress" acceptable for CAS on a poster, **still open**, (3) R2 replica handling
— **resolved**, see R2 below, (4) applied-claim scope — same question as item 4 below,
**still open**, (5) which cluster for CAS production — **resolved 2026-09-04, see R7 below**
(ku-cluster primary, ku-ai backup with a verified GROMACS-version compatibility precondition).

**No record found anywhere (memory or docs) that P.P. actually answered questions 1/2/4
above, or that the July 16 meeting produced a decision.** That means the core poster-framing
question may still be genuinely unanswered from July straight through to today (Sept 4) —
this is a bigger risk than the date alone: with 21 days left, confirm with P.P. directly
whether IFSC2026 participation is happening at all before drafting anything, not just
re-verify the deadline date.

**Not yet done:** abstract draft, confirmation with P.P. that this is actually happening,
poster content plan. **This was never added to CLAUDE.md's Submission Checklist — that's
the gap this log exists to close.**

### 2. "Secondary SASA" — exact definition unconfirmed
**Date raised:** 2026-06-09 meeting · **Status:** 🔴 OPEN (raised again 2026-08-01, still open)
Her raw meeting note said "secondary dasa" as a separate line item from the DSSP table
row — meaning genuinely ambiguous. Candidate reading (Fable brief, 2026-08-04): SASA
computed *per secondary-structure element* (DSSP assigns the region, SASA partitions
across it) — absolute per-SSE SASA is computable now; ΔSASA-on-adsorption is NOT
computable (no completed adsorption event exists in either dataset to take a delta over).
**Action:** propose the absolute-per-SSE reading to her in one line, don't build it
speculatively first.

### 3. Which lab experiments to correlate against?
**Date raised:** 2026-06-09 meeting · **Status:** 🔴 OPEN
Direction note: "correlation with lab experiment expected" — unclear whether she means
COMFHA in-house wet-lab data or published experimental literature. Repo shows **zero
evidence of in-house tensiometry/Langmuir-trough capability** — strong signal this means
published literature (already surveyed in `paper/LITERATURE_REVIEW.md`: Cornec1999,
Ulaganathan2017a for BLG kinetics; Mackie1999 for CAS interfacial rheology; Atkinson1995
for CAS N-terminal neutron reflectivity). **Action:** confirm this reading with her
directly — repo silence isn't conclusive proof there's no in-house collaboration.

### 4. How prescriptive should the "modify to adsorb" applied claim be?
**Date raised:** 2026-06-09 meeting · **Status:** 🔴 OPEN
Her direction: paper should "suggest how to modify/improve milk protein adsorption."
Tension: BLG/CAS data show the **pre-commitment** ensemble only — no completed adsorption
event in either dataset, so a strong causal "mutate X → adsorbs faster" claim isn't
supported. Drafted candidate framing (soft, defensible): *"intrinsic disorder and
surface-exposed hydrophobic patches lower the kinetic barrier to adsorption"* — a design-
principle statement, not a prescription. A more concrete candidate exists
(`docs/COMFHA_Science_Notes.md`: CD/EF loop residues 57–60 as an engineering target) but
it descends from the now-disproven two-factor gate hypothesis — recommend keeping it OUT
of Paper 1 and reframing as a testable Paper 4 (enhanced sampling) hypothesis instead.
**Action:** confirm which level of prescription she actually wants — changes how much
needs writing.

### 5. Figure-plan sub-decisions (P.P.'s June 9 note, still unconfirmed)
**Date raised:** 2026-06-09 meeting · **Status:** 🔴 OPEN (low urgency — resolve before final figure build, not before analysis)
- Fig 1B (box schematic): both proteins in one box, or separate boxes?
- Fig 2 (RMSD/RMSF/Rg): BLG and CAS as separate subpanels, or overlaid?
- Fig 4 (DSSP): table or heatmap?
- Calyx clustering: exact residue definition for `--target calyx` in `blg_cluster.py`
  (script currently uses an approximate ~35–45, 55–65, 80–90 range — needs confirmation
  before that clustering mode is ever run for real).
- **Contact-frame clustering metric** (her raw note: "Cluster 100 frames → properties") —
  which metric to cluster the ~100 representative contact frames on: whole-protein RMSD, or
  calyx orientation specifically? `blg_cluster.py --target contact` currently defaults to
  GROMOS/RMSD (0.2 nm cutoff) — never explicitly confirmed against her intent. Distinct from
  the calyx-clustering *residue definition* question above — this is which *metric*, that
  one is which *residues*.

### 6. Co-author review of Paper 1 BLG-only draft — blocking submission
**Date raised:** ongoing since June · **Status:** 🔴 OPEN, hard blocker
Even for the paused BLG-only `main.tex` (10/10 Gemini review, June 2): P.P.'s review of
title + SET 1D removal + scope claim is still pending, and it's a listed hard blocker
alongside the Zenodo DOI in the Submission Checklist. Not urgent while the comparative
expansion is in progress, but don't forget it exists.

---

## 🟢 RESOLVED — decisions locked, kept for the trail

### R1. Report both BLG and CASEIN (not BLG-only)
**Date:** 2026-06-09 meeting · **Resolution:** Reporting only BLG is insufficient — both
are the main milk proteins. Drove the Paper 1 scope pivot from BLG-only to comparative.
**Applied:** all analysis scripts since have been prefixed `blg_`/`cas_`/`combined_`; never
revert to BLG-only framing.

### R2. R2 replica — keep or drop? (Open Decision 1 in `paper1_expansion_plan.md`)
**Date raised:** 2026-06-09 · **Resolved:** by 2026-08-08, doc text fixed 2026-08-23
**Option C — keep all 3 replicas.** R2 has 101 contact events, comparable to R3's 99 — not
an outlier. Headline numbers (613 contacts, SASA 24–37 nm², Pearson r +0.006) already
reflect CENTER+R1+R2+R3 as originally computed; no recompute needed.

### R3. Characterisation, not mechanism
**Date:** 2026-06-12 · **Resolved:** confirmed the two-factor gate mechanism is disproven
(r = +0.006); the paper is framed as characterisation of the pre-commitment contact
ensemble, not a discovered activation mechanism. P.P.'s "real-experiment ref for
application" need is met by refs already in the literature review — a framing task, not a
literature gap.

### R4. β-Casein simulated in same BLG environment, 2 replicas only
**Date:** 2026-06-09 meeting · **Resolved, applied.** Saves cluster time — CASEIN is the
larger system (~2× BLG's atom count). CENTER + R1 only, no R2/R3 for CAS.

### R5. Meeting cadence: Tuesday & Thursday progress updates
**Date:** 2026-08-01 · **Resolved, standing practice.** User named the actual recurring
failure mode: not lack of automation, lack of structure connecting day-to-day work to a
visible checkpoint (CASEIN sat idle 16 days once with no forcing function). Plan work in
Tue/Thu-sized chunks; if a session opens with no work since the last meeting, flag it
plainly.

### R7. Cluster allocation for CAS production: ku-cluster primary, ku-ai backup
**Date:** 2026-09-04 · **Resolved (user decision, not yet run through P.P. — flag if she
asks).** ku-cluster is primary (already what CAS production 6413/6416 ran on); ku-ai
approved as a fallback **with a compatibility precondition, verified same day**:
ku-cluster runs GROMACS **2020.4** (matches local Mac Mini exactly — no `.tpr` compatibility
issue, same as all current work). ku-ai only has **2022.6 / 2024.1** modules — a genuinely
different major version. Same failure mode already hit once in this project (replica
`_ext.tpr` files at tpx 138 unreadable by local tpx 119) would recur if ku-ai's `gmx grompp`
were ever used directly. **Rule going forward if ku-ai is actually invoked:** always
`grompp` locally (2020.4) and only run `mdrun` on ku-ai (forward-compatible); never `grompp`
on ku-ai itself. See [[feedback-mac-technical]] item 17 for the full verification.

### R6. SET 1D mention in the abstract — co-author decision (found in `review-stage/AUTO_REVIEW_R4_critique.md`)
**Date raised:** pre-August (NatComms review round R4) · **Resolved by 2026-06-12
onward:** the 3-way options at the time (keep in abstract / move to its own section only /
remove entirely) are all superseded — SET 1D was **removed from the paper entirely** per
CLAUDE.md's "SET 1D status" note (data kept at `outputs_BLG/SET1D/corrected/` as a baseline
for a future enhanced-sampling paper). Noted here only to close the loop on an old
"co-author decision required" flag found during this log's backfill — no action needed.

---

## 🟡 Flagged, not yet formally raised with P.P. (surface at next meeting)

- **Box geometry differs between BLG and CASEIN** (BLG 12×12×7nm bulk vs CAS 16×14×9nm) —
  a real physical constraint (CASEIN's AlphaFold extended conformation doesn't fit BLG's
  box), not a preference. Worth a one-line heads-up so it doesn't look like an
  inconsistency to a reviewer.
- **TIP3P surface tension framing bug in `main.tex`** (~line 144: claims "half of 72 =
  35.8 mN/m"; verified value is 51.9 mN/m, matching real TIP3P literature ~50–52 mN/m
  almost exactly) — needs a fix whenever `main.tex` work resumes, not P.P.'s decision to
  make, but she should know the number changed.
- **Surface tension precision overstatement** (separate from the bug above —
  `docs/PP_meeting_talking_points_2026-07-16.md`): "51.9 ± 38.5 mN/m matches literature
  almost exactly" quotes the *instantaneous* SD (huge by nature, not the uncertainty on the
  mean). Fix: report block-averaged SEM (single digits) instead — presentational, not a
  data problem, but a sharp point a reviewer will poke at first.
- **"Decoupled" framing of the null result reads as overreach** — same source. "No
  coupling detected within these limits" is the defensible version; the current framing in
  some drafts anthropomorphises a null result as a positive finding.
- **Gate-orientation angle formula symmetry — never formally decided**
  (`review-stage/PBC_FIX_DECISION_LOG.md` Decision 4, dated during the PBC-fix work): the
  angle formula (`arccos(-v[2])`) only measures orientation toward the *lower* interface;
  whether it should be symmetric (`min` over both interfaces) was explicitly flagged as a
  "user/co-author decision," never resolved. Low priority now that the two-factor gate
  model itself was abandoned in favor of the "characterisation, not mechanism" framing
  (see R3 below) — but technically still an open loose end in `blg_gate_analysis.py`'s
  methodology if anyone revisits the r=+0.006 result.

---

*Maintained by `/pp-feedback`. See also `docs/paper1_expansion_plan.md` (the original,
more detailed capture of the June 9 meeting) and `CLAUDE.md`'s "Last Session" section for
session-to-session handoff. This file is for supervisor feedback specifically — it does
not duplicate technical/analysis state, which lives in
`~/.claude/projects/-Users-mac2022-1/memory/project_paper1_expansion.md`.*
