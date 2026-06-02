# Citation Audit Report

**Date**: 2026-06-02  
**Bib file**: paper/latex/references.bib  
**Paper**: "Contact without Commitment: Atomistic Characterisation of β-Lactoglobulin Adsorption Dynamics at the Air–Water Interface"  
**Reviewer model**: gemini-2.5-flash (Gemini API, 5 parallel batches, fresh threads)  
**Total cited entries audited**: 42  
**Overall verdict**: **FAIL** — 2 wrong-context citations require replacement before submission

---

## Summary Table

| Verdict | Count | Keys |
|---------|-------|------|
| **REPLACE** | 2 | Gochev2019JPCB, Foam4_2020 |
| **FIX** | 5 | Ulaganathan2017b, Vega2007, Rabe2011, Ulaganathan2017a, Gowers2016 |
| KEEP | 35 | (all others — see clean list below) |

---

## Priority Fixes (Must Apply Before Submission)

---

### REPLACE: `Gochev2019JPCB` — wrong-context citation

**Files**: main.tex lines ~132, ~280, ~612  
**Issue**: Gochev2019JPCB is **Part 3** of the BLG adsorption layers series, which presents a neutron reflectometry study of adsorption layer *structure* at different pH values. It is **not** a kinetics paper and does not present data on adsorption kinetics or kinetic energy barriers. All three citation contexts load it for kinetics claims:

- Line ~132: "BLG adsorbs over seconds to minutes, exhibits a kinetic energy barrier" — **WRONG**: kinetics paper is Part 1 (Ulaganathan2017a)
- Line ~280: "kinetic energy barrier inferred from experimental adsorption kinetics" — **WRONG**: same reason
- Line ~612: "No contact grows into irreversibly adsorbed monolayer on seconds-to-minutes timescale" — **WRONG**: structural paper, not about adsorption timescales

**Action**: For kinetics claims (lines ~132, ~280), cite `Ulaganathan2017a` (Part 1 — kinetics and surface pressure isotherm) instead. For line ~612 (experimental timescale support), keep `Cornec1999` and `Ulaganathan2017a`; remove `Gochev2019JPCB`. If the intent is to cite the *series* generally for BLG adsorption at AWI, consider keeping this key only in a context that specifically references layer structure or pH effects.

---

### REPLACE: `Foam4_2020` — wrong-context citation for use 2

**Files**: main.tex lines ~132, ~612  
**Issue**: Foam4_2020 is **Part 4** of the series — "Impact on the Stability of Foam Films and Foams." It is about downstream foam stability after adsorption, not about adsorption kinetics or the timescale of initial monolayer formation from bulk.

- Line ~132: "partially unfolds in the adsorbed state" — **WEAK**: paper mentions unfolding in introduction as known background, but is not the primary source for this claim
- Line ~612: "No contact grows into irreversibly adsorbed monolayer on the experimentally relevant seconds-to-minutes timescale" — **WRONG**: foam stability paper, not about adsorption kinetics or timescales

**Action**: For line ~612, remove `Foam4_2020` from the timescale citation group; the timescale claim is already supported by `Cornec1999` and `Ulaganathan2017a`. For line ~132, if the intent is to support partial unfolding, `Perriman2007` (X-ray/neutron reflectometry showing AWI destabilises BLG) is a better choice; `Foam4_2020` may still be cited elsewhere if the paper discusses foam stability.

---

### FIX: `Vega2007` — quantitative inaccuracy in citing sentence

**File**: main.tex line ~647  
**Issue**: The paper text states "the TIP3P water model underestimates the air–water surface tension by **roughly one-third** relative to TIP4P/2005 and to experiment." Vega & de Miguel (2007) report TIP3P surface tension at 298 K as **~35.8 mN/m** vs experimental **~72 mN/m** — TIP3P is roughly **half** the experimental value, not one-third. The same discrepancy holds relative to TIP4P/2005 (~62.5 mN/m).

**Action**: Change "roughly one-third" → "roughly half" in the Discussion section. This is a factual error in the manuscript text, not in the bib entry itself.

```diff
- the TIP3P water model underestimates the air--water surface tension by roughly one-third relative to TIP4P/2005 and to experiment\citep{Vega2007}
+ the TIP3P water model underestimates the air--water surface tension by roughly half relative to TIP4P/2005 and to experiment\citep{Vega2007}
```

---

### FIX: `Ulaganathan2017b` — wrong-context citation

**File**: main.tex line ~132  
**Issue**: Part 2 of the BLG adsorption layers series covers **dilational rheology** — it does not present new adsorption kinetics data or kinetic energy barrier analysis. Citing it alongside the kinetics claim "BLG adsorbs over seconds to minutes, exhibits a kinetic energy barrier" is contextually wrong. Part 2 references Part 1 for kinetics.

**Action**: Remove `Ulaganathan2017b` from the kinetics citation at line ~132, or replace with a comment on rheology if the intent was to also cite surface rheology of the adsorbed layer. Also verify author list against Colloids Surf. A 521 (2017) 167–176.

---

### FIX: `Rabe2011` — solid-surfaces paper cited for AWI timescales

**File**: main.tex line ~618  
**Issue**: Rabe et al. (2011) is explicitly a review of protein adsorption at **solid surfaces**, not at fluid (air-water or oil-water) interfaces. The paper cites it for "protein adsorption from bulk to an irreversibly adsorbed monolayer encompasses structural rearrangements and cooperative processes that unfold on timescales from seconds to hours." While the timescale claim is broadly valid for protein adsorption, using a solid-surfaces-specific reference to support an air-water interface claim is indirect.

**Action**: Add a qualifying phrase ("as reviewed for solid surfaces by Rabe et al.") or supplement with a fluid-interface-specific review (e.g., `Dickinson1999`, `Narsimhan2018`) that covers similar timescale discussion.

---

### FIX: `Ulaganathan2017a` — author list needs verification

**File**: references.bib  
**Issue**: Reviewer flagged the 8-author list against a shorter version. The current bib entry lists 8 authors (Ulaganathan, Retzlaff, Won, Gochev, Gehin-Delval, Leser, Noskov, Miller). Needs confirmation against Colloids Surf. A 519 (2017) 153–160 to ensure completeness and order are correct.

**Action**: Manually verify against publisher record at doi:10.1016/j.colsurfa.2016.03.008.

---

### FIX: `Gowers2016` — author list may be incomplete

**File**: references.bib  
**Issue**: Reviewer reported the actual SciPy 2016 proceedings paper may have more authors than the 11 listed in the bib entry. The commonly cited version has 11 authors; the reviewer suggested 17. Needs verification.

**Action**: Verify at https://conference.scipy.org/proceedings/scipy2016/pdfs/richard_gowers.pdf. If additional authors are listed, update the bib entry.

---

## Lower Priority Notes (WEAK context — acceptable but suboptimal)

- **Cornec1999 uses (1) and (5)**: Cornec1999 primarily reports adsorption kinetics (k1, k2 rate measurements for α-La and BLG), not BLG's general role as "dominant stabiliser" or irreversibility of monolayer formation. WEAK for those uses but acceptable in a multi-citation group.
- **Mackie1999**: WEAK for explicit "kinetic energy barrier" language (discusses variants A/B kinetics but doesn't use barrier terminology explicitly).
- **Perriman2007**: WEAK for kinetic energy barrier context (paper demonstrates thermal destabilisation, not a kinetics measurement).
- **BertonCarabin2018**: Emulsion-focused review but principles apply broadly to fluid interfaces; acceptable.

---

## All-Clean Entries (KEEP — no action needed)

Zare2015, Zare2016, Saurabh2024, Magarkar2014, Euston2010, Cieplak2014, Alamdari2020, Beierlein2015, Dickinson1999, BertonCarabin2018, Damodaran2005, Narsimhan2018, Huppertz2010, Graham1979, Brownlow1997, Kontopidis2004, Eberini2004, Loch2013, Mercadante2012, Flower1996, Papiz1986, Barbiroli2022, Cornec1999, Mackie1999, Perriman2007, Huang2017, Jorgensen1983, Essmann1995, Abraham2015, MichaudAgrawal2011, Mitternacht2016, Bussi2007, Berendsen1984, Hess1997, Laio2002

---

## Verification Notes from Prior Bib Comments

The following bib notes were confirmed resolved by this audit:

| Note | Status |
|------|--------|
| Cornec1999 `[VERIFY DOI]` | Reviewer confirmed DOI resolves |
| Zare2016 `[VERIFY pages]` | Pages 1572–1581 confirmed correct |
| Barbiroli2022 (prior wrong authors Bolisetty & Mezzenga) | Barbiroli/Iametti/Bonomi confirmed correct |
| Saurabh2024 (prior wrong first author Chaudhri) | Saurabh confirmed correct (PubMed 38194618) |
| Brownlow1997 PDB 1BEB at 1.8 Å | Confirmed by reviewer |
| Eberini2004 Glu89 triggers Loop CD/EF | Confirmed explicitly by reviewer |
| Mercadante2012 ~50 μM dimer threshold | Confirmed by reviewer |

---

*Traces: `.aris/traces/citation-audit/2026-06-02_run01/`*  
*Machine-readable ledger: `CITATION_AUDIT.json`*
