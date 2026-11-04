"""
cas_rmsd.py
===========
Calpha RMSD and per-residue RMSF for beta-casein (CENTER, R1), one pass per
trajectory. Mirrors blg_rmsd.py / precompute_rmsf.py conventions so the CAS
panels of Fig 2 are comparable with the BLG ones:

  * self-referenced to frame 0 of each run, single global Calpha fit
  * regions reported from that SAME fit (no per-region re-fit):
      backbone = all 209 Calpha, nterm = Calpha of residues 1-25
  * RMSF = per-residue Calpha RMSF about the mean position of the fitted
    trajectory (same global fit)
  * STRIDE 10 (1 ns), as blg_rmsd.py / precompute_rmsf.py

CAUTION: beta-casein is intrinsically disordered. RMSD from frame 0 and RMSF
after a global fit are dominated by chain motion, not "stability"; read them as
chain mobility. SP2 (phosphoserine) residues are included explicitly -- the
MDAnalysis "protein" keyword omits them (see project memory, 2026-11-04).

Usage: python -u scripts/analysis/cas_rmsd.py [--label CENTER|R1]
Output: results/analysis/cas_rmsd_{label}.npz
  keys: time_ns, rmsd_backbone, rmsd_nterm (nm); resids, rmsf (nm)
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis.align import rotation_matrix
from MDAnalysis.transformations import unwrap as mda_unwrap

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import cas_nterm_sasa as cas   # noqa: E402  (TRAJS)

OUT = ROOT / "results" / "analysis"
STRIDE = 10


def run(label):
    out = OUT / f"cas_rmsd_{label}.npz"
    if out.exists():
        print(f"[CACHED] {out.name}")
        return
    cfg = cas.TRAJS[label]
    u = mda.Universe(str(cfg["tpr"]), *[str(p) for p in cfg["xtc"] if p.exists()])
    prot = u.select_atoms("protein or resname SP2")
    assert len(prot.atoms) == 3363, len(prot.atoms)
    u.trajectory.add_transformations(mda_unwrap(prot))
    ca = prot.select_atoms("name CA")
    assert len(ca) == 209, len(ca)
    nt = np.array([r in range(1, 26) for r in ca.resids])
    print(f"=== {label}: {len(ca)} Calpha, {nt.sum()} in 1-25, stride {STRIDE}", flush=True)

    u.trajectory[0]
    ref = ca.positions - ca.center_of_mass()
    t, rb, rn, coords = [], [], [], []
    for ts in u.trajectory[::STRIDE]:
        x = ca.positions - ca.center_of_mass()
        R, _ = rotation_matrix(x, ref)
        xf = x @ R.T
        d = np.sqrt(((xf - ref) ** 2).sum(axis=1))
        rb.append(np.sqrt((d ** 2).mean()) / 10.0)
        rn.append(np.sqrt((d[nt] ** 2).mean()) / 10.0)
        t.append(ts.time / 1000.0)
        coords.append(xf)
    X = np.array(coords)                       # frames x 209 x 3 (Angstrom)
    rmsf = np.sqrt(((X - X.mean(axis=0)) ** 2).sum(axis=2).mean(axis=0)) / 10.0
    print(f"  RMSD backbone {np.mean(rb):.2f} nm, N-term {np.mean(rn):.2f} nm; "
          f"RMSF range {rmsf.min():.2f}-{rmsf.max():.2f} nm; n={len(t)}", flush=True)
    np.savez(out, time_ns=np.array(t), rmsd_backbone=np.array(rb),
             rmsd_nterm=np.array(rn), resids=ca.resids, rmsf=rmsf)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="all")
    a = ap.parse_args()
    for lab in (cas.TRAJS if a.label == "all" else [a.label]):
        run(lab)
