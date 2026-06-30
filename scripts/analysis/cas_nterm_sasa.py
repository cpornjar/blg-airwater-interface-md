"""
cas_nterm_sasa.py
=================
Per-frame SASA of the β-casein N-terminal amphipathic region (residues 1-25).
This is the HEADLINE "open chain" metric for Paper 1, paralleling BLG's
calyx SASA (blg_calyx_sasa.py / 3.81±0.46 nm²).

Target question: does the N-terminal 1-25 region maintain high solvent
exposure throughout the trajectory (consistent with "open chain" character)?
Compare mean ± std against BLG calyx SASA in Fig 4 table.

Same PBC-correction discipline as BLG: mda_unwrap before freeSASA.
SASA computed for whole protein per frame (burial by rest of chain is
physically correct), then summed over N-terminal atom indices only.

Usage:
    python -u scripts/analysis/cas_nterm_sasa.py [--label CENTER]

Output: results/analysis/cas_nterm_sasa_{label}.npz
  keys: time_ns, nterm_sasa_nm2
        mean_nm2, std_nm2 (scalars)
"""

import argparse
import gc
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.transformations import unwrap as mda_unwrap
import freesasa

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

# Residues 1-25: N-terminal amphipathic region of mature β-casein
# (AlphaFold numbering, 1-indexed, matches pdb2gmx residue IDs)
NTERM_RESIDS = list(range(1, 26))

RADIUS_MAP = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "H": 1.20, "P": 1.80}
STRIDE = 5   # 0.5 ns per frame, same as blg_calyx_sasa.py

# Add R1 here once outputs_CAS/R1/MD1000/ is set up
TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_CAS/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_CAS/CENTER/MD1000/traj_comp.xtc"],
    },
}


def analyse_label(label):
    cfg = TRAJS[label]
    tpr = cfg["tpr"]
    xtc_list = [p for p in cfg["xtc"] if p.exists()]

    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found at {tpr}")
        return
    if not xtc_list:
        print(f"[SKIP] {label}: no xtc files found")
        return

    out_npz = OUT / f"cas_nterm_sasa_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===", flush=True)
    u = (mda.Universe(str(tpr), str(xtc_list[0]))
         if len(xtc_list) == 1
         else mda.Universe(str(tpr), *[str(p) for p in xtc_list]))

    protein = u.select_atoms("protein")
    u.trajectory.add_transformations(mda_unwrap(protein))

    nterm_mask = np.array([a.resid in NTERM_RESIDS for a in protein.atoms])
    print(f"  Frames: {u.trajectory.n_frames} | stride={STRIDE} "
          f"| total = {u.trajectory.totaltime/1000:.1f} ns", flush=True)
    print(f"  N-term atoms (res 1-25): {nterm_mask.sum()} / {len(protein.atoms)}",
          flush=True)

    radii = [RADIUS_MAP.get(a.name[0].upper(), 1.70) for a in protein.atoms]

    times, nterm_sasa = [], []
    n_done = 0
    for ts in u.trajectory[::STRIDE]:
        coords = protein.positions
        result = freesasa.calcCoord(coords.flatten().tolist(), radii)
        sasa_atoms = np.array([result.atomArea(i) for i in range(len(protein.atoms))])
        # Å² → nm²
        nterm_sasa.append(float(sasa_atoms[nterm_mask].sum()) / 100.0)
        times.append(ts.time / 1000.0)
        n_done += 1
        if n_done % 100 == 0:
            print(f"    frame {n_done} | t={times[-1]:.0f} ns | "
                  f"N-term SASA={nterm_sasa[-1]:.2f} nm²", flush=True)

    t = np.array(times)
    s = np.array(nterm_sasa)
    print(f"\n  N-term (1-25) SASA: {s.mean():.2f} ± {s.std():.2f} nm²  "
          f"(n={len(s)}, range {s.min():.2f}–{s.max():.2f} nm²)", flush=True)
    print(f"  BLG calyx SASA reference: 3.81 ± 0.46 nm² (CENTER)", flush=True)

    np.savez(
        out_npz,
        time_ns=t,
        nterm_sasa_nm2=s,
        mean_nm2=s.mean(),
        std_nm2=s.std(),
    )
    print(f"  Saved: {out_npz.name}", flush=True)

    del u
    gc.collect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="CENTER", choices=list(TRAJS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
