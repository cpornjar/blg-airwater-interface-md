"""
blg_dssp.py
===========
Per-residue secondary structure over time for BLG, all replicas.
Uses MDAnalysis 2.10.0 built-in DSSP (STRIDE algorithm).

Outputs:
  - Time-resolved secondary structure codes per residue
  - Aggregate fractions (helix / sheet / coil) per frame
  - Mean secondary structure fraction over the trajectory

Key question for the paper: does BLG secondary structure change during
interface contact events? Compare contact frames vs bulk frames.

Usage:
    python -u scripts/analysis/blg_dssp.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_dssp_{label}.npz
  keys: time_ns, residue_ids, dssp_codes (n_frames × n_residues, str)
        frac_helix, frac_sheet, frac_coil (n_frames)
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

OUT    = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

STRIDE = 10  # every 10 frames (~10 ns at 1 ns/frame) — manageable for DSSP

TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"],
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_ext.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0002.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0003.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0004.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0005.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0006.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0007.xtc",
        ],
    },
    "R2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.part0002.xtc",
        ],
    },
    "R3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.part0002.xtc",
        ],
    },
}

# Secondary structure code mapping (DSSP single-letter codes)
HELIX_CODES = {'H', 'G', 'I'}   # α-helix, 3₁₀-helix, π-helix
SHEET_CODES = {'E', 'B'}         # β-strand, β-bridge
COIL_CODES  = {'T', 'S', 'C', '-'}  # turn, bend, coil, undefined


def analyse_label(label):
    cfg = TRAJS[label]
    tpr = cfg["tpr"]
    xtc_list = [p for p in cfg["xtc"] if p.exists()]

    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found")
        return
    if not xtc_list:
        print(f"[SKIP] {label}: no xtc files found")
        return

    out_npz = OUT / f"blg_dssp_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    u = mda.Universe(str(tpr), *[str(x) for x in xtc_list])
    protein = u.select_atoms("protein")
    n_res   = protein.n_residues
    print(f"  Frames: {u.trajectory.n_frames}  Residues: {n_res}  Stride: {STRIDE}")

    ds = DSSP(protein, verbose=True)
    ds.run(step=STRIDE)

    # ds.results.dssp_ndarray: (n_sampled_frames, n_residues) char array
    codes = ds.results.dssp_ndarray  # shape (n_frames, n_res)

    # Compute per-frame fractions
    n_sampled = codes.shape[0]
    frac_helix = np.zeros(n_sampled)
    frac_sheet = np.zeros(n_sampled)
    frac_coil  = np.zeros(n_sampled)

    for i, row in enumerate(codes):
        frac_helix[i] = sum(c in HELIX_CODES for c in row) / n_res
        frac_sheet[i] = sum(c in SHEET_CODES for c in row) / n_res
        frac_coil[i]  = sum(c in COIL_CODES  for c in row) / n_res

    # Time axis from sampled frames
    times = np.array([
        u.trajectory[i * STRIDE].time for i in range(n_sampled)
    ]) / 1000.0  # ps → ns

    # Residue IDs
    resids = protein.residues.resids

    print(f"  Mean secondary structure:")
    print(f"    Helix: {frac_helix.mean()*100:.1f}%")
    print(f"    Sheet: {frac_sheet.mean()*100:.1f}%")
    print(f"    Coil:  {frac_coil.mean()*100:.1f}%")

    # Store codes as object array (str per residue per frame)
    codes_str = np.array([[''.join(c) for c in row] for row in codes])

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
    ap.add_argument("--label", default="all",
                    choices=["CENTER", "R1", "R2", "R3", "all"])
    args = ap.parse_args()

    labels = list(TRAJS) if args.label == "all" else [args.label]
    for lab in labels:
        analyse_label(lab)


if __name__ == "__main__":
    main()
