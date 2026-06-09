"""
blg_density.py
==============
Mass density profile along Z for protein and water, all BLG replicas.
Uses gmx density (GROMACS) for each replica, then saves averaged profiles.

This is the raw data source for Fig 3 (density × PCA panel) and a key
observable for the BLG vs CAS comparison.

Usage:
    python -u scripts/analysis/blg_density.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_density_{label}.npz
  keys: z_nm, protein_density, water_density (all in kg/m³)
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

GMX    = str(Path.home() / "opt/gromacs-2020.4/bin/gmx")
OUT    = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc",
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_ext.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
    },
    "R2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
    },
    "R3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
    },
}

# Molecule group numbers from gmx density selection (CHARMM36m slab system)
# 0 = System, 1 = Protein, 4 = SOL (water oxygens)
# Verify with: echo "q" | gmx make_ndx -f <tpr>
PROTEIN_GROUP = "Protein"
WATER_GROUP   = "SOL"


def parse_xvg(path):
    """Read a 2-column xvg file, return (x, y) arrays."""
    xs, ys = [], []
    with open(path) as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.split()
            if len(parts) >= 2:
                xs.append(float(parts[0]))
                ys.append(float(parts[1]))
    return np.array(xs), np.array(ys)


def run_density(label, tpr, xtc, group_name, out_xvg, tmpdir, stride=10):
    """Call gmx density for one group."""
    cmd = [
        GMX, "density",
        "-f", str(xtc),
        "-s", str(tpr),
        "-o", str(out_xvg),
        "-d", "Z",
        "-dens", "mass",
        "-b", "0",
        "-sl", "200",          # 200 slabs along Z
        "-dt", str(stride),    # stride in ps (stride=10 → every 10 ps = 0.01 ns)
        "-nobackup",
    ]
    result = subprocess.run(
        cmd,
        input=f"{group_name}\n",
        capture_output=True,
        text=True,
        cwd=tmpdir,
    )
    if result.returncode != 0:
        print(f"  [ERROR] gmx density failed for {label} {group_name}")
        print(result.stderr[-2000:])
        return None
    return parse_xvg(out_xvg)


def analyse_label(label):
    cfg = TRAJS[label]
    tpr, xtc = cfg["tpr"], cfg["xtc"]

    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found at {tpr}")
        return
    if not xtc.exists():
        print(f"[SKIP] {label}: xtc not found at {xtc}")
        return

    out_npz = OUT / f"blg_density_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} already exists — skipping")
        return

    print(f"\n=== {label} ===")
    with tempfile.TemporaryDirectory(dir="/var/folders") as tmpdir:
        prot_xvg  = Path(tmpdir) / f"{label}_prot_density.xvg"
        water_xvg = Path(tmpdir) / f"{label}_water_density.xvg"

        print(f"  Computing protein density ...")
        prot = run_density(label, tpr, xtc, PROTEIN_GROUP, prot_xvg, tmpdir)
        if prot is None:
            return

        print(f"  Computing water density ...")
        water = run_density(label, tpr, xtc, WATER_GROUP, water_xvg, tmpdir)
        if water is None:
            return

    z_prot,  d_prot  = prot
    z_water, d_water = water

    # Interpolate to common Z grid if lengths differ
    if len(z_prot) != len(z_water):
        z_common   = np.linspace(z_prot.min(), z_prot.max(), 200)
        d_prot_i   = np.interp(z_common, z_prot, d_prot)
        d_water_i  = np.interp(z_common, z_water, d_water)
        z_nm = z_common / 10.0  # Å → nm
        d_prot, d_water = d_prot_i, d_water_i
    else:
        z_nm = z_prot / 10.0

    np.savez(
        out_npz,
        z_nm=z_nm,
        protein_density=d_prot,
        water_density=d_water,
    )
    print(f"  Saved: {out_npz.name}")
    print(f"  Protein peak: {d_prot.max():.1f} kg/m³ at z={z_nm[np.argmax(d_prot)]:.2f} nm")
    print(f"  Water bulk:   {d_water.max():.1f} kg/m³")


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
