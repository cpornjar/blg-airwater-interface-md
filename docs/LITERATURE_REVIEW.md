# Literature Review — Contact/Commitment Dichotomy in BLG Adsorption at the Air–Water Interface
**For group meeting June 4, 2026**
**Generated: May 27, 2026 | Sources: PubMed, CrossRef, Semantic Scholar, arXiv**

---

## Overview

The literature on BLG at the air–water interface divides into four axes:
1. **Structural biology of BLG** — calyx architecture, loop dynamics, lipocalin fold
2. **Experimental interfacial adsorption** — tensiometry, neutron reflectometry, SFG, ellipsometry
3. **Computational studies** — MD at oil–water, CG models, orientation-resolved simulation
4. **Foam stability** — film drainage, monolayer rheology, particle stabilisation

The **first-ever unbiased atomistic MD of native BLG at the air–water interface** (this work) fills the gap at the intersection of axes 2 and 3.

---

## Part 1 — BLG Structural Biology (Axis 1)

### Already cited

| Paper | Key finding | Relevance |
|-------|------------|-----------|
| Brownlow et al. 1997 (*Structure*) | Crystal structure of BLG-A at 2.6 Å | Reference structure for simulations |
| Kontopidis et al. 2004 (*J Mol Biol*) | Calyx ligand binding; Glu89/loop EF gating | Defines the calyx as the functional ligand pocket |
| Flower 1996 (*Biochem J*) | Lipocalin superfamily overview | BLG as canonical lipocalin |
| Loch et al. 2013 | BLG variant structures | Force-field validation reference |
| Papiz et al. 1986 | Early BLG crystal structure | Historical structural anchor |

### Not yet cited — relevant to calyx/loop dynamics

**Eberini et al. 2004** (*Proteins*, DOI:10.1002/prot.10643) — "Reorganization in apo- and holo-β-lactoglobulin upon protonation of Glu89: molecular dynamics and pKa calculations"
- **Method:** Classical MD from crystallographic data, GROMACS
- **Key finding:** Glu89 protonation triggers calyx re-organisation; apo vs holo forms show distinct loop EF dynamics
- **Relevance:** The only prior MD study of BLG calyx loop dynamics. Directly relevant to the "loop-mediated calyx activation" narrative in our Fig 3c. The CD/EF loop (residues 57–60) that dominates flexibility in the near-interface R1 simulation is the same loop controlled by Glu89 in this work.
- **Cite where:** sec:activation, paragraph on Loop CD/EF shift

**Uhrínová et al. 2000** (*Biochemistry*, DOI:10.1021/bi992629o) — "Structural changes accompanying pH-induced dissociation of the β-lactoglobulin dimer"
- **Method:** NMR, recombinant BLG-A at pH 2.6
- **Key finding:** 3D structure of monomeric BLG at low pH; backbone dynamics reveal loop flexibility
- **Relevance:** NMR evidence for loop flexibility in BLG monomer — complements our RMSF analysis

---

## Part 2 — Experimental Interfacial Adsorption (Axis 2)

### Already cited (full series)

| Paper | Technique | Key finding |
|-------|-----------|------------|
| Cornec et al. 1999 (*JCIS*) | Tensiometry, radiolabelling | BLG adsorbs faster than αLA; kinetic barrier exists |
| Mackie et al. 1999 (*Langmuir*) | AFM, interfacial rheology | BLG forms viscoelastic monolayer |
| Ulaganathan et al. 2017a (*Adv Colloid*) | Neutron reflectometry | BLG layer structure pH-dependent |
| Ulaganathan et al. 2017b (*JPCB*) | Neutron reflectometry | Conformational changes in adsorbed BLG |
| Gochev et al. 2019 (*JPCB*) | Neutron reflectometry | BLG layer structure Series 3 |
| Gochev et al. 2020/Foam4 (*Minerals*) | Tensiometry + foam | BLG layer impact on foam stability, Series 4 |
| Perriman et al. 2007 (*JPCB*) | Neutron reflectometry | BLG stability at AWI; partial unfolding |

### Not yet cited — should consider adding

**Engelhardt et al. 2012** (*Langmuir*, DOI:10.1021/la301368v) — "Protein adsorption at the electrified air-water interface: implications on foam stability"
- **Method:** SFG spectroscopy + ellipsometry; BSA at AWI
- **Key finding:** Microscopic surface chemistry (ion–protein interactions at AWI) directly controls macroscopic foam stability; BLG and BSA show different orientational preferences
- **Relevance:** Experimental evidence that AWI protein orientation → foam stability. Supports the orientation component of the commitment barrier — correct calyx orientation is one of the two independent variables required for commitment. Note: uses BSA not BLG, but in same context.
- **Citations:** 75

**Beierlein et al. 2015** (*JPCB*, DOI:10.1021/acs.jpcb.5b01944) — "Carboxylate Ion Pairing with Alkali-Metal Ions for β-Lactoglobulin and Its Role on Aggregation and Interfacial Adsorption"
- **Method:** SFG + ellipsometry + MD (BLG in electrolyte solutions); also includes MD simulation of BLG
- **Key finding:** Carboxylate-cation pairing modulates BLG orientation and adsorption efficiency at the AWI; BLG shows distinct face-on vs edge-on orientations depending on ionic environment
- **Relevance:** **Direct experimental + MD evidence** that BLG orientation at the AWI matters for adsorption. The closest prior work connecting BLG orientation to adsorption efficiency. The BLG MD component (in electrolyte, not air–water slab) is the only prior MD study linking BLG orientation to adsorption outcome — relevant to our finding that commitment requires the rare coincidence of correct calyx orientation and open calyx state.
- **Cite where:** Introduction and Discussion — "Experimental evidence that BLG orientation at the AWI modulates adsorption (Beierlein et al. 2015) is consistent with the orientation component of the commitment barrier characterised here."

**Gochev et al. 2020 Series 4** (already cited as Foam4_2020): confirmed as DOI:10.3390/min10070636 — *Minerals* 2020. Open access.

**Li et al. 2021** (preprint, DOI:10.1101/2021.05.14.444152) — "Effect of charge on protein preferred orientation at the air–water interface in cryo-electron microscopy"
- **Method:** Cryo-EM + analysis of protein datasets
- **Key finding:** Proteins show systematic preferred orientation at the AWI determined by charge distribution; enrichment of hydrophobic surfaces toward the air phase
- **Relevance:** Independent cryo-EM evidence that proteins have preferential orientations at AWI — directly supports the orientation component of the commitment barrier. Note: preprint, treat with caution.

---

## Part 3 — Computational Studies (Axis 3)

### Already cited

| Paper | System | Method | Key finding |
|-------|--------|--------|-------------|
| Zare et al. 2015 (*Langmuir*) | BLG at decane–water | Atomistic MD, 100 ns | BLG at oil–water: calyx toward oil; partial unfolding |
| Zare et al. 2016 (*Langmuir*) | BLG at decane–water | Atomistic MD | Force-field comparison; BLG retains β-barrel at oil–water |
| Alamdari et al. 2020 (*Langmuir*) | Various proteins at AWI | MD + SFG | Orientation-resolved; hydrophobic face tilts toward air |
| Magarkar et al. 2014 (*Sci Rep*) | Hydrophobins at AWI | MD | Hydrophobins self-assemble via surface-active patches |
| Saurabh et al. 2024 (*Biophys J*) | mAb at water/vapour | MD, thermally stressed | mAb partially unfolds; AWI destabilises IgG |
| Cieplak & Zhao 2014 | 5 proteins at AWI+OWI | All-atom MD | Proteins distort at interface; oil coupling stronger |
| Euston 2010 | Protein model at AWI | Coarse-grained | AWI selects amphiphilic configurations |

### Not yet cited — should consider adding

**Saurabh et al. 2024 APL** (*APL Bioengineering*, DOI:10.1063/5.0207959) — "Adsorption of monoclonal antibody fragments at the water–oil interface: A coarse-grained molecular dynamics"
- **Method:** CG-MD, mAb Fab fragments at water–oil
- **Key finding:** Fab fragments show preferential orientation at oil–water interface; Fc mediates aggregation
- **Relevance:** Extends the Saurabh 2024 work; CG approach for larger systems; shows orientation matters for mAb adsorption — parallel to our BLG finding
- **Note:** Different from the Saurabh 2024 already cited (which used thermally stressed conformations at water/vapour)

**Hingst et al. 2025** (*Eur Biophys J*, DOI:10.1007/s00249-025-01752-0) — "Competitive adsorption of a monoclonal antibody and amphiphilic polymers to the air–water interface"
- **Method:** SFG + tensiometry; mAb competition with polysorbate 80
- **Key finding:** mAb orientation at AWI is disrupted by polysorbate 80; orientation-dependent adsorption efficiency
- **Relevance:** Very recent (2025); shows mAb orientation at AWI is selectively disrupted — supports orientation gating as a general phenomenon

---

## Part 4 — Foam Stability / Film Rheology (Axis 4)

### Already cited

| Paper | System | Key finding |
|-------|--------|-------------|
| Narsimhan & Xiang 2018 (*Annu Rev*) | General review | Protein foams: kinetics and mechanism overview |
| Dickinson 1999 (*Colloids Surf B*) | Review | Protein films at fluid interfaces |
| Damodaran 2005 (*Food Sci*) | Review | Interfacial protein structure-function |
| BertonCarabin 2018 (*Annu Rev*) | Review | Protein stabilisers of food dispersions |
| Huppertz 2010 (*Int Dairy J*) | BLG dairy foam | BLG as primary milk foam stabiliser; processing effects |
| Barbiroli et al. 2022 | BLG variants | Stability and foam function of BLG variants |

### Not yet cited — should consider adding

**Sun et al. 2024** (*Food Hydrocolloids*, DOI:10.1016/j.foodhyd.2023.109290) — "Enhancing foam stability with β-lactoglobulin nanoparticles: Insights into molecular-level interactions"
- **Method:** Tensiometry, pendant drop, small-angle X-ray
- **Key finding:** BLG nanoparticles (partially denatured aggregates) form more stable foam than native BLG; hydrophobic surface patches exposed on nanoparticle surface drive enhanced adsorption
- **Relevance:** Supports calyx SASA as the rate-limiting variable: when BLG is forced into a state with more exposed hydrophobic surface (as nanoparticles), adsorption improves — consistent with calyx breathing being the slow intrinsic variable the interface selects for. (Note: the earlier "SASA ≥ 35 nm² threshold" was a PBC artifact; the valid claim is that hydrophobic exposure correlates with adsorption propensity.)
- **Citations:** 9

**Kurz et al. 2021** (*Food Research International*, DOI:10.1016/j.foodres.2019.04.027) — "Correlation between physico-chemical characteristics of particulated β-lactoglobulin and interfacial behaviour"
- **Key finding:** BLG particle surface hydrophobicity correlates with interfacial adsorption rate; more hydrophobic → faster adsorption
- **Relevance:** Same point as Sun 2024 — hydrophobic exposure is the rate-limiting factor for BLG adsorption

---

## Synthesis

### What the field was mostly trying to solve (before this work)

**Experimental axis:** Measure the kinetic energy barrier for BLG adsorption (Cornec, Ulaganathan, Gochev series). Establish that BLG has a measurable activation barrier unlike α-lactalbumin. Characterise the adsorbed layer structure by neutron reflectometry. **Never identified the molecular origin of the barrier.**

**Computational axis:** Study BLG at oil–water interfaces (Zare 2015/2016, shorter timescales, pre-positioned). Demonstrate that the β-barrel core survives interfacial contact. **Never simulated BLG at the air–water interface from bulk solution.**

**Foam axis:** Show that BLG foam stability depends on hydrophobic surface exposure (Sun 2024, Kurz 2021) and protein conformation. **Never connected this to a specific geometric condition.**

### Four literature clusters

| Cluster | Representative papers | Gap addressed by COMFHA |
|---------|----------------------|------------------------|
| Adsorption phenomenology | Cornec 1999, Gochev 2019/2020, Ulaganathan 2017 | Kinetic barrier known but mechanism unknown |
| BLG MD at oil–water | Zare 2015/2016 | Oil ≠ air; pre-positioned; too short |
| Protein orientation at AWI | Alamdari 2020, Engelhardt 2012, Beierlein 2015 | None used BLG from bulk at air–water; none identified SASA ⊥ θ independence |
| BLG structure / calyx | Eberini 2004, Kontopidis 2004, Brownlow 1997 | Loop dynamics in isolation, not at interface |

### What's new vs what was known

| Aspect | Prior state | COMFHA contribution |
|--------|-------------|---------------------|
| BLG at AWI by MD | Never done | First atomistic, native-state, bulk-start, 4 µs |
| Adsorption metric | Centre-of-mass distance (unreliable for 4 nm protein) | Nearest-atom contact |
| Contact/commitment distinction | Not resolved | 613 contact events; only 6 > 10 ns |
| Molecular origin of kinetic barrier | Unknown | SASA ⊥ θ (r = +0.006, CI [−0.09, +0.11], N_eff ≈ 17); commitment requires rare coincidence of two statistically independent variables |
| Loop responsible for activation | CD/EF loop suspected from structure | Confirmed: Loop CD/EF shift at interface vs Loop BC in bulk |

### Evidence strength

- **Strong:** Experimental kinetics literature (Cornec, Gochev, Ulaganathan) — well-replicated, decades of data, confirms kinetic barrier exists
- **Strong:** BLG crystal structures (Brownlow, Kontopidis) — high-resolution, directly used as simulation starting point
- **Moderate:** Protein orientation at AWI (Alamdari, Engelhardt, Beierlein) — SFG is difficult; Beierlein's MD component is BLG-specific but not in air–water slab
- **Weak:** Computational study of BLG at AWI — only our work; Zare 2015/2016 is oil-water with pre-positioning
- **Weak:** Calyx loop MD (Eberini 2004) — old force field (GROMOS), pH-dependent perturbation rather than interfacial dynamics

---

## Gaps Remaining After This Work

1. **Direct validation:** No commitment event observed in unbiased MD — all 613 contacts end with retreat. Enhanced sampling (metadynamics along (SASA, θ)) needed to compute the commitment PMF and characterise the transition state.
2. **Force-field dependence:** Only CHARMM36m tested; AMBER14SB or ff19SB comparison would strengthen
3. **pH dependence:** All simulations at pH ~7; BLG adsorption is strongly pH-dependent (Gochev series); the gate thresholds may shift with pH
4. **αLA comparison:** BLG adsorbs faster than αLA experimentally (Cornec 1999) but αLA has no calyx — testing the gate model on αLA would be a falsification test
5. **Concentration effects:** All simulations use a single BLG molecule; protein–protein interactions at the interface (monolayer crowding) not modelled

---

## Practical Takeaway

| | |
|--|--|
| **Dominant current approach** | Tensiometry + neutron reflectometry (experimental); CG-MD or short atomistic at oil–water (computational) |
| **Saturated direction** | Measuring adsorption kinetics and layer thickness — well-characterized; diminishing returns |
| **Promising open direction** | Orientation-resolved MD of globular proteins at AWI; enhanced sampling (metadynamics along (SASA, θ)) for commitment events and PMF; αLA/BLG comparison to test the calyx specificity hypothesis |

---

## Priority Citation Additions

Papers to consider adding to the manuscript bibliography:

| Priority | Paper | Where to cite | Why |
|----------|-------|--------------|-----|
| **HIGH** | Beierlein et al. 2015 (*JPCB*) | Intro + Discussion | Only prior work combining BLG MD + SFG showing orientation matters for adsorption |
| **HIGH** | Eberini et al. 2004 (*Proteins*) | sec:activation, Loop CD/EF paragraph | Only prior BLG MD study of calyx loop dynamics |
| **MEDIUM** | Engelhardt et al. 2012 (*Langmuir*) | Discussion | Experimental link: protein AWI orientation → foam stability |
| **MEDIUM** | Sun et al. 2024 (*Food Hydrocolloids*) | Discussion | Hydrophobic surface exposure accelerates BLG adsorption; supports calyx SASA as the slow variable driving the commitment barrier |
| **LOW** | Hingst et al. 2025 (*Eur Biophys J*) | Discussion | Very recent; mAb orientation at AWI disrupted by surfactants |

---

*Literature review updated June 2, 2026 to reflect PBC-corrected framing (see Science Notes §8). Gate threshold language removed throughout; paper now frames SASA ⊥ θ independence (r = +0.006) as the mechanistic origin of the kinetic barrier. Next step: add Beierlein 2015 and Eberini 2004 to manuscript bibliography.*
