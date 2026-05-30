# Presenter Cheat Sheet — Contact without Commitment
## COMFHA Lab Group · May 2026 · Print and keep on podium

---

## The One-Sentence Story
> BLG visits the air-water interface constantly but never commits. Calyx SASA and orientation are independent on the us timescale. Commitment requires enhanced sampling to characterise.

---

## Key Numbers — Never Get These Wrong

| What | Value |
|------|-------|
| Total MD time | **4.00 us** (4 x 1000 ns) |
| Contact events | **613** total (97 CENTER + 215 R1 + 156 R2 + 145 R3) |
| Contact fraction | **7.1–23.4%** of frames per trajectory |
| Max penetration | **0.71 nm** past interface |
| Long events (>= 10 ns) | **6** — none commits |
| Longest event | **59 ns** (R1) |
| SASA range | **24–37 nm2** (PBC-corrected) |
| SASA mean | **28.95 nm2** |
| p95 threshold | **32.1 nm2** |
| Pearson r | **+0.006** |
| Block bootstrap CI | **[-0.09, +0.11]** |
| Effective N | **~17** (autocorrelation 232 ns) |
| Rg (R1) | **1.496 +/- 0.009 nm** (flat) |
| Patch RMSD | **~0.24 nm** (flat, no trend) |
| Loop BC RMSF (bulk) | **0.54 nm** (residues 30–35) |
| Loop CD/EF RMSF (AWI) | **0.39 nm** (residues 57–60) — dominant |
| PBC artefact SASA | **45–62 nm2** (before fix) |
| Gate-open frames | **0** (after PBC fix) |

---

## Slide Timing — Quick Reference

```
S1  Title           0:30    S11  Calyx breathes  9:45
S2  Outline         1:00    S12  Loop shift      11:00
S3  Foam            2:00    S13  SASA distrib.   12:00
S4  Gap             3:00    S14  Orientation     13:15
S5  System          4:00    S15  Bootstrap       14:15
S6  Metric          4:45    S16  PBC lesson      15:00
S7  Frequent        6:00    S17  Meaning         16:30
S8  Rare            7:00    S18  Implications    17:30
S9  Table           7:45    S19  Next steps      18:00
S10 Compact         8:45    S20  Summary         19:00
```

---

## Three Takeaways (say exactly these)

1. **Contact frequent, commitment absent** — 613 events, only 6 >= 10 ns, none commits
2. **Compact globally, loop-mediated locally** — Rg flat; Loop CD/EF dominates near AWI
3. **SASA independent of orientation** — r = +0.006, CI [-0.09, +0.11], rules out |r| > 0.11

---

## Quick Q&A Answers

| Question | Core answer |
|----------|-------------|
| Why not enhanced sampling first? | Need the pre-commitment baseline first; now we have it |
| TIP3P appropriate? | Surface tension ~50 vs 72 mN/m; quantitative shift, not qualitative; TIP4P/2005 planned |
| What about the dimer? | Monomer = single-molecule mechanism baseline; dimer adds steric/kinetic/orientational complexity |
| Event count vs figure bands? | 613 from full 0.1 ns resolution; figure uses 0.5 ns stride — both correct |
| Why JCIS not Nature? | Scope claim = honest scope; JCIS IF ~9 is right venue for this community |
| r = +0.006 with N~17? | Block bootstrap accounts for small N; CI [-0.09, +0.11] rules out strong coupling |
| Most surprising? | 59 ns contact without commitment — real kinetic bottleneck, not noise |
| Loop CD/EF shift — caused by interface? | Yes — interface-induced conformational preference; proximity selects calyx-opening motions |

---

## Paper Status (May 30, 2026)
- Auto-review Round 12: **10/10 READY** (Gemini 2.5 Flash — first READY verdict)
- GitHub: **github.com/cpornjar/blg-airwater-interface-md**
- Pending before JCIS submission: Zenodo DOI + P.P. sign-off
- Paper 2 (beta-Casein): AlphaFold2 structure ready
