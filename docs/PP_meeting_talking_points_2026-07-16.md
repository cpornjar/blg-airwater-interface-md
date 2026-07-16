# P.P. Meeting — Talking Points (IFSC2026 poster)

Working prep doc. Not a report. Keep open during the conversation.

## 1. 60-second opening

"BLG is done and clean. Four microseconds of unbiased MD, fully PBC-corrected. We
hypothesised a two-factor adsorption gate — and disproved it: after catching a PBC/SASA
artifact, the real signal is zero gate-open events and r = +0.006 between exposure and
orientation. The value isn't 'nothing happened' — it's that we can state precisely **where
unbiased microsecond MD stops**, with a tight bound (rules out |r| > 0.11). That bound is the
result, and it's what motivates the CAS comparison and future enhanced sampling. CAS is
mid-prep — EM and NVT_bulk done on the corrected phosphoserine topology, production not yet."

Lead with method rigor (bug caught), not with the negative.

## 2. Likely tough questions

- **"Mechanism disproven — what's the contribution?"** The *bound* is the contribution: 4 µs
  rules out |r| > 0.11; folded BLG does not begin to commit at this timescale. Honest scope
  claim, not a failed experiment.
- **"Is a null enough to publish?"** Split it: **for a poster, yes** — standard and honest.
  **For JCIS, no on its own** — which is exactly why we expanded to the BLG+CAS comparison.
- **"Why did CAS take so long / real ETA?"** Restart was a caught bug (below), not drift. NPT
  not yet submitted, cluster not confirmed. Honest ETA: production may yield little or **nothing
  by Nov 12** on a ~199k-atom system. Abstract needs no CAS data; poster must stand without it.
- **"2 replicas enough for an IDP?"** Be honest — it's thin, especially from a single
  low-confidence AlphaFold conformation. Note *you* chose 2 (CAS is ~2× BLG atoms). Frame CAS as
  **preview, not conclusion**.
- **"Phosphoserine bug — wasted compute?"** Yes, some — but **equilibration-scale, caught before
  production** (the expensive part). SEP q=−1 → SP2 q=−2, correct for milk pH ~6.7. Catching it
  pre-production is the discipline a reviewer wants.
- **"BLG-only or BLG+CAS on the poster?"** BLG-only body, CAS as explicit in-progress preview.

## 3. Weakest points in the report (own these before P.P. does)

- **Surface tension "51.9 ± 38.5 mN/m matches literature almost exactly."** Sharpest poke.
  ±38.5 is the SD of the *instantaneous* tension (huge by nature), **not** the uncertainty on the
  mean. Say: "I should report block-averaged SEM — single digits — then 51.9 sits cleanly on
  TIP3P." Presentational fix, not a data problem.
- **Null framed as "positive statement / decoupled."** Overreach. A skeptic reads it as "the
  protein never engaged, so of course nothing co-varies." Soften to "no coupling detected within
  these limits." Keep the defensible bound, drop the anthropomorphising.
- **Comparative title already "locked" with only half the data.** "An Accessible Calyx and an Open
  Chain" promises two proteins; CAS has zero production data. Don't headline it yet.
- **R2 still open** (P.P. flagged in June): trends opposite to R1/R3, and all headline numbers
  include it. Come with a position — Option C (keep all 3, call R2 a non-committing pathway) is
  most honest.
- Latent (paper-level, not poster blocker): BLG and CAS use different box sizes — a confound for a
  strict comparative claim.

## 4. Recommendation

**Lead BLG-only as the complete story; present CAS as an explicit "in progress" preview. Submit
the abstract. Do not headline the comparative title until CAS production data exists.** The poster
degrades gracefully — BLG stands alone today; any CAS data by November is a bonus.
