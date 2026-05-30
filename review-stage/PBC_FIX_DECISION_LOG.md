# PBC Fix Decision Log
**Session: May 27–28, 2026 | Author: Claude (Sonnet 4.6) | Scope: gate_analysis_all_replicas.py**

---

## The Problem

### Discovery chain

1. **Fig 3 regeneration completed** (tmux `fig3regen`, PID 5354). Patch RMSD confirmed
   flat: 0.241 nm at 500 ns, 0.226 nm at 650 ns. This correction is *valid*.

2. **Investigating SASA discrepancy**: `make_fig3_activation.py` (which uses
   `from MDAnalysis.transformations import unwrap`) reported a maximum SASA of
   32.39 nm² after the residue-list fix. The paper (Round 5 fixes) claimed
   62 nm² at t=259 ns, sourced from `R1_gate.npz`.

3. **Definitive proof of PBC splitting**: At t=259 ns in the R1 base trajectory,
   direct coordinate inspection showed x_span = 120.0 Å — exactly the box width.
   A protein with a ~4 nm diameter should span ≤ 40–45 Å. The protein was
   physically split across the x periodic boundary.

4. **Artifact chain**:
   - `freesasa.calcCoord` takes flat (x,y,z) coordinates and computes SASA in
     vacuum. It has no concept of periodic boundaries. When atoms from one half
     of the protein appear at x ≈ 0 Å and the other half at x ≈ 120 Å, the
     inter-atomic distances used for occlusion are vastly inflated.
   - Result: every buried hydrophobic atom appears fully exposed → SASA
     artificially elevated from ~28–30 nm² (real) to 37–70 nm² (artifact).
   - Angle formula uses `protein.center_of_mass()` and `calyx.center_of_mass()`.
     With split protein, the COM is the geometric average of atoms on both sides,
     producing a meaningless intermediate point. The resulting vector v is
     unrelated to the actual calyx direction.

5. **Confirmed match**: `sasa_without_unwrap` = 62.20 nm² matches `R1_gate.npz`
   exactly at t=259 ns. This proves the cached data was computed without unwrapping.

---

## Decision 1: Use `mda_unwrap`, not `NoJump` or `make_whole`

### Options considered

| Method | What it does | Why rejected/chosen |
|--------|-------------|---------------------|
| `MDAnalysis.transformations.unwrap` | Traverses bond graph, translates bonded fragments so no bond crosses PBC; applies per-frame | **CHOSEN** — proven correct in `make_fig3_activation.py`; guarantees molecule is whole |
| `MDAnalysis.transformations.NoJump` | Prevents large jumps between consecutive frames by adding box-length offsets | Doesn't fix single-frame splitting; frames at XTC file boundaries can still be split if the preceding frame is from a different file |
| `gmx trjconv -pbc mol` | GROMACS preprocessing: write new trajectory with whole molecules | Requires rewriting 7 XTC files × 4 replicas ≈ ~9 GB; not reversible; changes the source data; would need re-running the full pipeline |
| Manual min-image in calc_frame | Apply minimum-image convention to each atom relative to the protein COM | Circular: COM is wrong precisely because atoms are split; can't use COM as reference to fix the splitting |

### Validation evidence

- **t=259 ns** (worst artifact frame): SASA 62.20 → 30.31 nm², θ 84.4° → 31.7°,
  x_span 120.0 Å → 37.4 Å
- **t=510 ns** (first AMD-part0002 frame, XTC file boundary): SASA 29.88 nm²,
  x_span 39.8 Å — unwrap propagates correctly across XTC file boundaries
- **50-frame test** (t=0–24.5 ns): SASA mean 26.33 nm², max 28.62 nm²,
  0/50 frames ≥ 35 nm²

---

## Decision 2: Where to insert `add_transformations` in the code

### The function call

```python
protein = u.select_atoms("protein")
u.trajectory.add_transformations(mda_unwrap(protein))   # ← inserted here
calyx   = protein.select_atoms("(resid 39 or ...)")
water_o = u.select_atoms("resname SOL and (name OW OH2 O)")
```

### Why this position is correct

- `add_transformations` is registered once; it is applied lazily at each
  frame-access event (every `for ts in u.trajectory[::STRIDE]` iteration).
- It must be called **after** `protein = u.select_atoms("protein")` because
  `mda_unwrap(protein)` needs the protein AtomGroup to know which atoms are
  to be made whole.
- It must be called **before** the main loop, not inside it — registering a
  transformation inside the loop would not cause errors but is wasteful.
- Placing it **before** `calyx` and `water_o` selections is safe: AtomGroup
  selections are lazy references to the Universe's positions array. When
  `calyx.center_of_mass()` or `water_o.positions` are accessed inside
  `calc_frame()`, they read positions from the same Universe — which has
  already applied the transformation for the current frame.

---

## Decision 3: Do NOT change the SASA threshold simultaneously

### The threshold situation

The current `SASA_THR = 35.0 nm²` was calibrated against the artifact-inflated
values. With proper PBC treatment, the maximum SASA observed in R1 is
**32.39 nm²** (from `make_fig3_activation.py`). The 35 nm² threshold is never
reached.

### Why keep 35 nm² unchanged in this run

**Separation of concerns**: the PBC fix is a *correction* to a bug in the
measurement code. The threshold is a *scientific choice* about what constitutes
"calyx activated." If we change the threshold at the same time as fixing the bug:

1. We cannot attribute changes in the output statistics to either the fix or the
   recalibration.
2. We would be choosing the threshold based on the artifact data — the correct
   recalibration requires understanding the corrected SASA distribution first.
3. A reviewer examining the code history would see a simultaneous threshold change
   and a bug fix — this looks like outcome engineering.

**Correct procedure**: fix the bug → see what the new distribution looks like →
calibrate threshold → update paper.

### Expected consequence

With SASA_THR = 35 nm² and max real SASA ≈ 32 nm², the output will show:
- `activated_pct ≈ 0%` across all replicas
- `gate_open_pct ≈ 0%`
- `Obs/Indep` is undefined (0/0)

This is not a failure of the fix — it is the correct result, which now reveals
the scientific question: **what is the right threshold?** That requires
scientific judgment from the user and co-author (P.P.), not automated
recalibration.

---

## Decision 4: Do NOT fix the angle formula asymmetry in this pass

### The asymmetry

`angle = np.degrees(np.arccos(np.clip(-v[2], -1, 1)))`

This measures the angle between the calyx → protein COM vector and the **-z**
axis (downward, toward the lower air–water interface). When the calyx points
**upward** (+z), v[2] ≈ +1, so arccos(-1) ≈ 180° — correctly excluded by
ANGLE_THR = 30°. When the calyx points **downward** (-z), v[2] ≈ -1, so
arccos(+1) ≈ 0° — correctly included.

### With PBC artifact (old behavior)

The protein COM was in the middle of the box (average of split atoms). The calyx
COM was similarly wrong. The resulting angle was essentially random with respect
to physical orientation. The 84.4° at t=259 ns (artifact) was meaningless; the
real angle is 31.7° (calyx nearly pointing downward toward the interface).

### Why not fix now

1. The formula may be **intentional**: only the lower interface is relevant (the
   box setup puts the air–water interface at z_lo and z_up; if the protein is
   near the lower interface, the calyx should point toward -z; if near the upper
   interface, it should point toward +z). Whether arccos(-v[2]) is a bug or a
   feature depends on which interface the protein is near at each frame.

2. Fixing would require knowing: does the paper's gate model intend to detect
   proximity to **either** interface (then `min(arccos(v[2]), arccos(-v[2]))`)
   or **only one** interface (then the formula is fine)?

3. This is a scientific question the authors must decide. Conflating it with the
   PBC fix creates another compounded change that is hard to audit.

**Flag for user/co-author decision: should the angle formula be symmetric
(min over both interfaces)?**

---

## Decision 5: Rename .npz files to .prebpc, do not delete

### Rationale

The pre-fix cached files must be preserved because:
1. **Audit trail**: the exact numbers in the current paper version can be traced
   back to these files. If a reviewer asks "what exactly were the artifact
   values?" the answer is in `R1_gate.npz.prebpc`.
2. **Comparison**: to show P.P. the magnitude of the correction (e.g.,
   R1 activated: 48.2% → 0%), we need both old and new values.
3. **Attribution**: renaming (not deleting) makes the `if cached.exists()` check
   in `main()` fail, forcing full recomputation from raw XTC. If we kept the
   files, the script would silently load the corrupted cached values.

The `.prebpc` suffix (pre-PBC-correction) is self-documenting.

---

## Decision 6: Run all replicas sequentially in one tmux session

### Options

| Mode | Pros | Cons |
|------|------|------|
| Sequential in one tmux | Simple monitoring; one CPU fully utilized; low peak memory | Slower: ~80–90 min total |
| 4 parallel processes | ~4× faster | 4 simultaneous MDAnalysis Universes + freesasa ≈ 4 × 240 MB = ~1 GB RAM; at 11 GB total RAM with OS overhead, may OOM or thrash (prior feedback: MDAnalysis OOM with large trajectories) |

Sequential is the safe choice given the documented MDAnalysis OOM risk.

---

## What the Results Will Show

### Expected new gate statistics (preliminary)

Based on validation tests (t=259 ns real SASA = 30.31 nm², max from
`make_fig3_activation.py` = 32.39 nm²):

| Statistic | Old (artifact) | Expected new (real) |
|-----------|---------------|---------------------|
| SASA mean (R1) | 37.15 nm² | ~26–29 nm² |
| SASA max (R1) | 70.11 nm² | ~31–32 nm² |
| Activated (SASA ≥ 35 nm²) | 48.2% | ~0% |
| Gate-open | 0.35% | ~0% |
| Obs/Indep | 0.30 | undefined |
| Fold suppression | 3.3× | undefined |

### What changes

**Invalidated claims**:
- "48.2% of R1 frames showed calyx exposure" → 0%
- "3.3-fold suppression of gate opening" → no gate-open events, metric undefined
- "CI [0.11, 0.50]" → undefined
- "R3 long event: 88.4% SASA > 35 nm²" → expected ~0%
- "SASA bursts reaching 62 nm² at t=259 ns" → real value ~30 nm²

**Still valid**:
- min_dist contact events (z-only, unaffected by x-y PBC)
- All 613 contact event counts
- All 6 long-event classifications
- Rg = 1.496 ± 0.009 nm
- RMSF analysis
- Patch RMSD flat at 0.24 nm
- Loop CD/EF vs Loop BC dominance at interface

### Decision tree for user/co-author

```
A. Lower SASA threshold to ≤ 32 nm² (e.g., 30 nm²)
   → recalibrate from new distribution; see if suppression survives
   → Pro: preserves two-factor gate model structure
   → Con: threshold appears data-driven, not physically motivated

B. Replace SASA with another activation metric
   → e.g., calyx pocket volume, specific hydrogen bonds, hydrophobic contact count
   → Pro: physically motivated; independent of freesasa calibration
   → Con: requires new analysis scripts and computation

C. Reformulate the mechanism without a SASA gate
   → Keep min_dist contact events; characterize what happens during contact
   → Focus on orientation-only gate or other geometric criterion
   → Con: loses the "two-factor" narrative novelty

D. Add enhanced sampling (SET 1D) first, then revisit
   → Use the unbiased results as motivation only; add gate-open events
      from biased simulations
   → Already in progress but co-author decision pending
```

---

## Files Modified in This Session

| File | Change | Reason |
|------|--------|--------|
| `scripts/gate_analysis_all_replicas.py` | +1 import (`mda_unwrap`), +1 line (`add_transformations`) | PBC bug fix |
| `scripts/gate_analysis_all_replicas.py` | Added `flush=True` to 3 print statements | Future monitoring (does not affect current run) |
| `results/gate_analysis/CENTER_gate.npz` → `.prebpc` | Renamed | Preserve artifact-corrupted cache; force recompute |
| `results/gate_analysis/R1_gate.npz` → `.prebpc` | Renamed | Same |
| `results/gate_analysis/R2_gate.npz` → `.prebpc` | Renamed | Same |
| `results/gate_analysis/R3_gate.npz` → `.prebpc` | Renamed | Same |
| `review-stage/REVIEW_STATE.json` | Status → RECOMPUTING_WITH_PBC_FIX | Updated state |

---

*Written May 27–28, 2026. Full rerun in progress (tmux: gate_pbc, PID 8832).*
*Expected completion: ~01:30–02:00 local time.*
