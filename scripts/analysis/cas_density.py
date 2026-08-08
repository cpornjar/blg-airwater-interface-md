"""
cas_density.py
==============
Mass density profile along Z for β-casein and water.
Mirrors blg_density.py exactly. Used for Fig 3 (density panel).

β-casein is an IDP — expect a broader, lower-peak protein density
compared to globular BLG. That difference is itself a result.

Usage:
    python -u scripts/analysis/cas_density.py [--label CENTER]

Output: results/analysis/cas_density_{label}.npz
  keys: z_nm, protein_density, water_density (kg/m³)
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

GMX = str(Path.home() / "opt/gromacs-2020.4/bin/gmx")
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

PROTEIN_GROUP = "Protein"
WATER_GROUP   = "SOL"

# NOTE 2026-08-08: tpr filename fixed from md_1000ns.tpr (stale pre-Aug-4
# SEP-charge topology, quarantined as .tpr.bak on 2026-08-04) to the
# correct md_1000ns_v2.tpr (SP2, q=-2). R1 added — xtc path is where
# production job 6416 will write once it runs (mirrors CENTER's default
# mdrun output naming, no -deffnm in the sbatch script).
TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_CAS/CENTER/MD1000/md_1000ns_v2.tpr",
        "xtc": ROOT / "outputs_CAS/CENTER/MD1000/traj_comp.xtc",
    },
    "R1": {
        "tpr": ROOT / "outputs_CAS/R1/MD1000/md_1000ns_r1_v2.tpr",
        "xtc": ROOT / "outputs_CAS/R1/MD1000/traj_comp.xtc",
    },
}


def parse_xvg(path):
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
    cmd = [
        GMX, "density",
        "-f", str(xtc),
        "-s", str(tpr),
        "-o", str(out_xvg),
        "-d", "Z",
        "-dens", "mass",
        "-b", "0",
        "-sl", "200",
        "-dt", str(stride),
        "-nobackup",
    ]
    result = subprocess.run(
        cmd, input=f"{group_name}\n",
        capture_output=True, text=True, cwd=tmpdir,
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

    out_npz = OUT / f"cas_density_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        prot_xvg  = Path(tmpdir) / f"{label}_prot_density.xvg"
        water_xvg = Path(tmpdir) / f"{label}_water_density.xvg"

        print("  Computing protein density ...")
        prot = run_density(label, tpr, xtc, PROTEIN_GROUP, prot_xvg, tmpdir)
        if prot is None:
            return

        print("  Computing water density ...")
        water = run_density(label, tpr, xtc, WATER_GROUP, water_xvg, tmpdir)
        if water is None:
            return

    z_prot, d_prot = prot
    z_water, d_water = water

    if len(z_prot) != len(z_water):
        z_common  = np.linspace(z_prot.min(), z_prot.max(), 200)
        d_prot    = np.interp(z_common, z_prot, d_prot)
        d_water   = np.interp(z_common, z_water, d_water)
        z_nm      = z_common / 10.0
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
    ap.add_argument("--label", default="CENTER", choices=list(TRAJS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
