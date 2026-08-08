"""
cas_surface_tension.py
======================
Surface tension for β-casein slab MD from pressure tensor.
Mirrors blg_surface_tension.py exactly — same formula, same units.

    γ = (Lz / 2) × [Pzz − (Pxx + Pyy) / 2]    (bar·nm → mN/m via ×0.1)

Key comparative question: does β-casein reduce surface tension more than
BLG? BLG CENTER gives 51.9 ± 38.5 mN/m. CAS result goes in Fig 4 table.

Usage:
    python -u scripts/analysis/cas_surface_tension.py [--label CENTER]

Output: results/analysis/cas_surface_tension_{label}.npz
  keys: time_ns, gamma_mNm, gamma_mean, gamma_std
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

# NOTE 2026-08-08: TPRS filename fixed from md_1000ns.tpr (stale pre-Aug-4
# SEP-charge topology, quarantined as .tpr.bak on 2026-08-04) to the
# correct md_1000ns_v2.tpr (SP2, q=-2). EDR filenames were unaffected by
# that bug (ener.edr isn't versioned). R1 added — paths are where
# production job 6416 will write once it runs (mirrors CENTER's default
# mdrun output naming, no -deffnm in the sbatch script).
EDRS = {
    "CENTER": ROOT / "outputs_CAS/CENTER/MD1000/ener.edr",
    "R1": ROOT / "outputs_CAS/R1/MD1000/ener.edr",
}
TPRS = {
    "CENTER": ROOT / "outputs_CAS/CENTER/MD1000/md_1000ns_v2.tpr",
    "R1": ROOT / "outputs_CAS/R1/MD1000/md_1000ns_r1_v2.tpr",
}

QUANTITIES = ["Pres-XX", "Pres-YY", "Pres-ZZ"]


def parse_xvg_multi(path):
    times, rows = [], []
    with open(path) as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.split()
            if len(parts) >= 2:
                times.append(float(parts[0]))
                rows.append([float(v) for v in parts[1:]])
    return np.array(times), np.array(rows)


def get_box_z(tpr_path):
    result = subprocess.run(
        [GMX, "dump", "-s", str(tpr_path)],
        capture_output=True, text=True,
    )
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("box[    2]"):
            values = line.split("{")[1].rstrip("}").split(",")
            return float(values[2])
    raise ValueError(f"Could not find box[2] in gmx dump of {tpr_path}")


def extract_pressure(edr_path, out_xvg, tmpdir):
    selection = "\n".join(QUANTITIES) + "\n0\n"
    cmd = [GMX, "energy", "-f", str(edr_path), "-o", str(out_xvg), "-nobackup"]
    result = subprocess.run(
        cmd, input=selection, capture_output=True, text=True, cwd=tmpdir,
    )
    if result.returncode != 0:
        print("  [ERROR] gmx energy failed")
        print(result.stderr[-2000:])
        return None
    return parse_xvg_multi(out_xvg)


def analyse_label(label):
    edr = EDRS[label]
    tpr = TPRS[label]

    if not edr.exists():
        print(f"[SKIP] {label}: edr not found at {edr}")
        return
    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found at {tpr}")
        return

    out_npz = OUT / f"cas_surface_tension_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    lz_nm = get_box_z(tpr)
    print(f"  Box Lz = {lz_nm:.3f} nm (constant, NVT)")

    with tempfile.TemporaryDirectory() as tmpdir:
        xvg_path = Path(tmpdir) / f"{label}_pressure.xvg"
        result = extract_pressure(edr, xvg_path, tmpdir)
        if result is None:
            return
        time_ps, vals = result

    if vals.shape[1] < 3:
        print(f"  [ERROR] Expected 3 columns, got {vals.shape[1]}")
        return

    pxx, pyy, pzz = vals[:, 0], vals[:, 1], vals[:, 2]
    gamma_bar_nm = (lz_nm / 2.0) * (pzz - (pxx + pyy) / 2.0)
    gamma_mNm    = gamma_bar_nm * 0.1
    time_ns      = time_ps / 1000.0

    print(f"  γ = {gamma_mNm.mean():.1f} ± {gamma_mNm.std():.1f} mN/m")
    print(f"  BLG CENTER reference: 51.9 ± 38.5 mN/m")
    print(f"  TIP3P reference: ~50-52 mN/m (Vega & de Miguel 2007)")

    np.savez(
        out_npz,
        time_ns=time_ns,
        gamma_mNm=gamma_mNm,
        gamma_mean=gamma_mNm.mean(),
        gamma_std=gamma_mNm.std(),
    )
    print(f"  Saved: {out_npz.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="CENTER", choices=list(EDRS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
