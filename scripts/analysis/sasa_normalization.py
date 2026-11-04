"""
sasa_normalization.py
=====================
Normalisation options for the headline "accessible feature" SASA comparison
(BLG calyx, 9 residues, vs CAS N-term 1-25, 25 residues). Raw sums are not
comparable across regions of different size. Two reference-free views are
computed here from the SAME frames, radii and freesasa settings as
blg_calyx_sasa.py / cas_nterm_sasa.py:

  ctx_nm2  region SASA inside the whole protein (burial by the rest of the
           chain included) -- identical definition to the existing headline.
  iso_res_nm2  sum over the region's residues of each residue's SASA ALONE
           (same frame conformation, all other atoms deleted). Same definition
           for scattered (calyx) and contiguous (N-term) regions, so
           ctx/iso_res = fraction of the residues' own surface left exposed.
  iso_seg_nm2  SASA of all region atoms together without the rest of the protein
           (kept for reference; NOT comparable across regions, because a
           contiguous segment self-buries while scattered residues do not).

Per-residue SASA = ctx_nm2 / n_residues (derived downstream).
No Gly-X-Gly / Tien max-ASA table is used: it is heavy-atom only and has no
SP2 entry, which would be inconsistent with this pipeline's H + custom radii.

Usage: python -u scripts/analysis/sasa_normalization.py [--only BLG|CAS]
Output: results/analysis/sasa_norm_{species}_{label}.npz
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.transformations import unwrap as mda_unwrap
import freesasa

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import blg_calyx_sasa as blg   # noqa: E402  (TRAJS, CALYX_RESIDS, RADIUS_MAP)
import cas_nterm_sasa as cas   # noqa: E402  (TRAJS, NTERM_RESIDS)

OUT = ROOT / "results" / "analysis"
STRIDE = 25   # 5 ns per frame -> ~401 frames per 1000 ns run


def run(species, label, cfg, resids, protein_sel, n_expected):
    out = OUT / f"sasa_norm_{species}_{label}.npz"
    if out.exists():
        print(f"[CACHED] {out.name}")
        return
    xtcs = [p for p in cfg["xtc"] if p.exists()]
    u = mda.Universe(str(cfg["tpr"]), *[str(p) for p in xtcs])
    prot = u.select_atoms(protein_sel)
    assert len(prot.atoms) == n_expected, (len(prot.atoms), n_expected)
    u.trajectory.add_transformations(mda_unwrap(prot))
    mask = np.array([a.resid in resids for a in prot.atoms])
    radii = np.array([blg.RADIUS_MAP.get(a.name[0].upper(), 1.70) for a in prot.atoms])
    print(f"=== {species} {label}: {mask.sum()} region atoms / {len(prot.atoms)}, "
          f"{len(resids)} residues, stride {STRIDE}", flush=True)
    res_masks = {rid: np.array([a.resid == rid for a in prot.atoms]) for rid in resids}
    t, ctx, iso, iso_res = [], [], [], []
    for ts in u.trajectory[::STRIDE]:
        xyz = prot.positions
        res = freesasa.calcCoord(xyz.flatten().tolist(), radii.tolist())
        a = np.array([res.atomArea(i) for i in range(len(prot.atoms))])
        ctx.append(a[mask].sum() / 100.0)
        r2 = freesasa.calcCoord(xyz[mask].flatten().tolist(), radii[mask].tolist())
        iso.append(r2.totalArea() / 100.0)
        s = 0.0
        for rid in resids:
            m = res_masks[rid]
            s += freesasa.calcCoord(xyz[m].flatten().tolist(), radii[m].tolist()).totalArea()
        iso_res.append(s / 100.0)
        t.append(ts.time / 1000.0)
    ctx, iso, iso_res = np.array(ctx), np.array(iso), np.array(iso_res)
    print(f"  ctx {ctx.mean():.2f}+-{ctx.std():.2f}  iso_res {iso_res.mean():.2f}  iso_seg {iso.mean():.2f} nm2  "
          f"ctx/iso_res {np.mean(ctx/iso_res):.3f}  n={len(ctx)}", flush=True)
    np.savez(out, time_ns=np.array(t), ctx_nm2=ctx, iso_seg_nm2=iso, iso_res_nm2=iso_res,
             n_res=len(resids), n_atoms=int(mask.sum()))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["BLG", "CAS"])
    a = ap.parse_args()
    if a.only in (None, "BLG"):
        for lab, cfg in blg.TRAJS.items():
            run("blg", lab, cfg, blg.CALYX_RESIDS, "protein", 2486)
    if a.only in (None, "CAS"):
        for lab, cfg in cas.TRAJS.items():
            run("cas", lab, cfg, cas.NTERM_RESIDS, "protein or resname SP2", 3363)
