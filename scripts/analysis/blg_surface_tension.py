"""
blg_surface_tension.py
======================
Compute instantaneous surface tension from the pressure tensor in the .edr file.

Formula (slab with two vacuum interfaces):
    γ = (Lz / 2) × [(Pxx + Pyy) / 2 − Pzz]

Units: Pxx/Pyy/Pzz in bar, Lz in nm → γ in bar·nm = 100 mN/m
Convert: 1 bar·nm = 100 mN/m = 0.1 N/m

TIP3P reference: ~35 mN/m (half of experimental 72 mN/m — expected systematic error).
Used in Fig 4 (quantitative comparison table, BLG vs CAS).

Usage:
    python -u scripts/analysis/blg_surface_tension.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_surface_tension_{label}.npz
  keys: time_ns, gamma_mNm (surface tension in mN/m), gamma_mean, gamma_std
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

# .edr files — one per replica (covers the full production run segment)
EDRS = {
    "CENTER": ROOT / "outputs_BLG/CENTER/MD1000/ener.edr",
    "R1":     ROOT / "outputs_BLG/REPLICA/MD/MD1/ener.edr",
    "R2":     ROOT / "outputs_BLG/REPLICA/MD/MD2/ener.edr",
    "R3":     ROOT / "outputs_BLG/REPLICA/MD/MD3/ener.edr",
}

# Quantity codes for gmx energy selection (exact names from GROMACS edr)
QUANTITIES = ["Pres-XX", "Pres-YY", "Pres-ZZ", "Box-Z"]


def parse_xvg_multi(path):
    """Read multi-column xvg (time + N values). Returns (time, values_array)."""
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


def extract_pressure(edr_path, out_xvg, tmpdir):
    """Run gmx energy to extract pressure tensor components and box Z."""
    # gmx energy takes selection via stdin (one per line, then 0 to finish)
    selection = "\n".join(QUANTITIES) + "\n0\n"
    cmd = [
        GMX, "energy",
        "-f", str(edr_path),
        "-o", str(out_xvg),
        "-nobackup",
    ]
    result = subprocess.run(
        cmd,
        input=selection,
        capture_output=True,
        text=True,
        cwd=tmpdir,
    )
    if result.returncode != 0:
        print(f"  [ERROR] gmx energy failed")
        print(result.stderr[-2000:])
        return None
    return parse_xvg_multi(out_xvg)


def analyse_label(label):
    edr = EDRS[label]
    if not edr.exists():
        print(f"[SKIP] {label}: edr not found at {edr}")
        return

    out_npz = OUT / f"blg_surface_tension_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    with tempfile.TemporaryDirectory(dir="/var/folders") as tmpdir:
        xvg_path = Path(tmpdir) / f"{label}_pressure.xvg"
        result = extract_pressure(edr, xvg_path, tmpdir)
        if result is None:
            return
        time_ps, vals = result

    # Columns: Pres-XX, Pres-YY, Pres-ZZ, Box-Z
    if vals.shape[1] < 4:
        print(f"  [ERROR] Expected 4 columns, got {vals.shape[1]}")
        return

    pxx   = vals[:, 0]   # bar
    pyy   = vals[:, 1]   # bar
    pzz   = vals[:, 2]   # bar
    lz_nm = vals[:, 3]   # nm

    # γ = (Lz/2) × [(Pxx + Pyy)/2 − Pzz]  in bar·nm
    # 1 bar·nm = 100 mN/m
    gamma_bar_nm = (lz_nm / 2.0) * ((pxx + pyy) / 2.0 - pzz)
    gamma_mNm    = gamma_bar_nm * 100.0

    time_ns = time_ps / 1000.0

    print(f"  γ = {gamma_mNm.mean():.1f} ± {gamma_mNm.std():.1f} mN/m")
    print(f"  TIP3P reference: ~35 mN/m (expected — half of experimental 72 mN/m)")
    print(f"  Time range: {time_ns[0]:.1f}–{time_ns[-1]:.1f} ns  ({len(time_ns)} frames)")

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
    ap.add_argument("--label", default="all",
                    choices=["CENTER", "R1", "R2", "R3", "all"])
    args = ap.parse_args()

    labels = list(EDRS) if args.label == "all" else [args.label]
    for lab in labels:
        analyse_label(lab)


if __name__ == "__main__":
    main()
