"""
cas_dssp.py
===========
Per-residue secondary structure over time for β-casein.
Mirrors blg_dssp.py exactly.

β-casein is an IDP — expect high coil fraction (~70-80%) throughout.
High coil% is expected, not novel; primary use is as a sanity check
and for Fig 4 comparison table (BLG helix/sheet/coil vs CAS).

Usage:
    python -u scripts/analysis/cas_dssp.py [--label CENTER]

Output: results/analysis/cas_dssp_{label}.npz
  keys: time_ns, residue_ids, dssp_codes (n_frames × n_residues),
        frac_helix, frac_sheet, frac_coil (per frame),
        mean_helix, mean_sheet, mean_coil (scalars)
"""

import argparse
import gc
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis.dssp import DSSP

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

STRIDE = 10   # every 10 frames (~10 ns) — same as blg_dssp.py

HELIX_CODES = {'H', 'G', 'I'}
SHEET_CODES = {'E', 'B'}
COIL_CODES  = {'T', 'S', 'C', '-'}

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

    out_npz = OUT / f"cas_dssp_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    u = (mda.Universe(str(tpr), str(xtc_list[0]))
         if len(xtc_list) == 1
         else mda.Universe(str(tpr), *[str(p) for p in xtc_list]))

    protein = u.select_atoms("protein")
    n_res = protein.n_residues
    print(f"  Frames: {u.trajectory.n_frames}  Residues: {n_res}  Stride: {STRIDE}")

    ds = DSSP(protein)
    ds.run(step=STRIDE, verbose=True)

    codes = ds.results.dssp
    n_sampled = codes.shape[0]
    frac_helix = np.zeros(n_sampled)
    frac_sheet = np.zeros(n_sampled)
    frac_coil  = np.zeros(n_sampled)

    for i, row in enumerate(codes):
        frac_helix[i] = sum(c in HELIX_CODES for c in row) / n_res
        frac_sheet[i] = sum(c in SHEET_CODES for c in row) / n_res
        frac_coil[i]  = sum(c in COIL_CODES  for c in row) / n_res

    times = np.array([
        u.trajectory[i * STRIDE].time for i in range(n_sampled)
    ]) / 1000.0

    resids = protein.residues.resids
    codes_str = np.array([[''.join(c) for c in row] for row in codes])

    print(f"  Mean secondary structure (β-casein, IDP expected):")
    print(f"    Helix: {frac_helix.mean()*100:.1f}%")
    print(f"    Sheet: {frac_sheet.mean()*100:.1f}%")
    print(f"    Coil:  {frac_coil.mean()*100:.1f}%")

    np.savez(
        out_npz,
        time_ns=times,
        residue_ids=resids,
        dssp_codes=codes_str,
        frac_helix=frac_helix,
        frac_sheet=frac_sheet,
        frac_coil=frac_coil,
        mean_helix=frac_helix.mean(),
        mean_sheet=frac_sheet.mean(),
        mean_coil=frac_coil.mean(),
    )
    print(f"  Saved: {out_npz.name}")

    del u, ds, codes, codes_str
    gc.collect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="CENTER", choices=list(TRAJS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
