"""
blg_surface_tension.py
======================
Compute instantaneous surface tension from the pressure tensor in the .edr file.

Formula (slab with two vacuum interfaces):
    γ = (Lz / 2) × [Pzz − (Pxx + Pyy) / 2]

Units: Pxx/Pyy/Pzz in bar, Lz in nm → γ in bar·nm
Convert: 1 bar·nm = 1e-4 N/m = 0.1 mN/m

TIP3P reference: ~50-52 mN/m (Vega & de Miguel, J. Chem. Phys. 2007, 126, 154707),
vs ~72 mN/m experimental — known TIP3P underestimate, NOT a factor of 2.
Cross-checked against GROMACS's own #Surf*SurfTen (.edr term 36): for CENTER,
<#Surf*SurfTen> = 1035.76 bar*nm = exactly 2x gamma_bar_nm (517.88 bar*nm),
confirming the Lz/2 per-interface factor and sign convention.
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

# .edr files per replica — R1/R2/R3 concatenate the base segment with the
# AMD-hardware/extension continuation parts (same gap blg_rg.py had; those
# .xtc extensions were already being read, but the matching .edr extensions
# were never synced locally until now).
EDRS = {
    "CENTER": [ROOT / "outputs_BLG/CENTER/MD1000/ener.edr"],
    "R1":     [ROOT / "outputs_BLG/REPLICA/MD/MD1/ener.edr"] +
              sorted((ROOT / "outputs_BLG/REPLICA/MD/MD1").glob("md_replica1_amd.part00*.edr")),
    "R2":     [ROOT / "outputs_BLG/REPLICA/MD/MD2/ener.edr",
               ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.part0002.edr"],
    "R3":     [ROOT / "outputs_BLG/REPLICA/MD/MD3/ener.edr",
               ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.part0002.edr"],
}

# .tpr files — used to read the (constant) box Z dimension.
# NVT slab MD: box never fluctuates, so GROMACS does not write Box-X/Y/Z
# energy terms to the .edr — Lz must come from the .tpr instead.
TPRS = {
    "CENTER": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
    "R1":     ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
    "R2":     ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2.tpr",
    "R3":     ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3.tpr",
}

# Quantity codes for gmx energy selection (exact names from GROMACS edr)
QUANTITIES = ["Pres-XX", "Pres-YY", "Pres-ZZ"]


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


def get_box_z(tpr_path):
    """Read the (constant) box Z dimension in nm from a .tpr via gmx dump."""
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


def concat_edr(edr_list, tmpdir):
    """gmx energy's -f only accepts one file, same restriction gmx gyrate has
    for .xtc (see blg_rg.py). Use gmx eneconv first to merge continuation
    segments into one .edr; eneconv sorts by timestamp and drops the
    duplicate checkpoint-restart frame by default — tested directly: R2's
    two segments concatenate to 10001 frames reaching 1000 ns, no duplicate
    at the 500 ns boundary."""
    if len(edr_list) == 1:
        return edr_list[0]
    out_edr = Path(tmpdir) / "concat.edr"
    cmd = [GMX, "eneconv", "-f", *[str(e) for e in edr_list], "-o", str(out_edr), "-nobackup"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=tmpdir)
    if result.returncode != 0:
        print(f"  [ERROR] gmx eneconv failed")
        print(result.stderr[-2000:])
        return None
    return out_edr


def extract_pressure(edr_list, out_xvg, tmpdir):
    """Run gmx energy to extract pressure tensor components and box Z."""
    edr_path = concat_edr(edr_list, tmpdir)
    if edr_path is None:
        return None
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
    edr_list = [p for p in EDRS[label] if p.exists()]
    tpr = TPRS[label]
    if not edr_list:
        print(f"[SKIP] {label}: no edr files found")
        return
    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found at {tpr}")
        return

    out_npz = OUT / f"blg_surface_tension_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} === ({len(edr_list)} edr segment(s): {[p.name for p in edr_list]})")
    lz_nm = get_box_z(tpr)
    print(f"  Box Lz = {lz_nm:.3f} nm (constant, NVT)")

    with tempfile.TemporaryDirectory() as tmpdir:
        xvg_path = Path(tmpdir) / f"{label}_pressure.xvg"
        result = extract_pressure(edr_list, xvg_path, tmpdir)
        if result is None:
            return
        time_ps, vals = result

    # Columns: Pres-XX, Pres-YY, Pres-ZZ
    if vals.shape[1] < 3:
        print(f"  [ERROR] Expected 3 columns, got {vals.shape[1]}")
        return

    pxx = vals[:, 0]   # bar
    pyy = vals[:, 1]   # bar
    pzz = vals[:, 2]   # bar

    # γ = (Lz/2) × [Pzz − (Pxx + Pyy)/2]  in bar·nm
    # 1 bar·nm = 1e5 Pa * 1e-9 m = 1e-4 N/m = 0.1 mN/m
    gamma_bar_nm = (lz_nm / 2.0) * (pzz - (pxx + pyy) / 2.0)
    gamma_mNm    = gamma_bar_nm * 0.1

    time_ns = time_ps / 1000.0

    print(f"  γ = {gamma_mNm.mean():.1f} ± {gamma_mNm.std():.1f} mN/m")
    print(f"  TIP3P reference: ~50-52 mN/m (Vega & de Miguel 2007); experimental ~72 mN/m")
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
