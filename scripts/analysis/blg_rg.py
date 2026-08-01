"""
blg_rg.py
=========
Radius of gyration (Rg) over time for BLG, all replicas, via gmx gyrate.

Validation target for CENTER: Rg = 1.496 +/- 0.009 nm (locked value, CLAUDE.md)

Usage:
    python -u scripts/analysis/blg_rg.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_rg_{label}.npz
  keys: time_ns, rg_nm, rg_mean, rg_std
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

TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc",
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
    },
    "R2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
    },
    "R3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
    },
}


def parse_xvg(path):
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


def run_gyrate(tpr, xtc, out_xvg, tmpdir):
    cmd = [GMX, "gyrate", "-f", str(xtc), "-s", str(tpr),
           "-o", str(out_xvg), "-nobackup"]
    result = subprocess.run(
        cmd,
        input="Protein\n",
        capture_output=True,
        text=True,
        cwd=tmpdir,
    )
    if result.returncode != 0:
        print(f"  [ERROR] gmx gyrate failed")
        print(result.stderr[-2000:])
        return None
    return parse_xvg(out_xvg)


def analyse_label(label):
    cfg = TRAJS[label]
    tpr, xtc = cfg["tpr"], cfg["xtc"]

    if not tpr.exists() or not xtc.exists():
        print(f"[SKIP] {label}: trajectory files not found")
        return

    out_npz = OUT / f"blg_rg_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    with tempfile.TemporaryDirectory() as tmpdir:
        xvg_path = Path(tmpdir) / f"{label}_gyrate.xvg"
        result = run_gyrate(tpr, xtc, xvg_path, tmpdir)
        if result is None:
            return
        time_ps, vals = result

    # vals columns: Rg, Rg_x, Rg_y, Rg_z (nm)
    rg_nm = vals[:, 0]
    time_ns = time_ps / 1000.0

    rg_mean = float(np.mean(rg_nm))
    rg_std = float(np.std(rg_nm))

    print(f"  Rg = {rg_mean} +/- {rg_std} nm  (expected: 1.496 +/- 0.009)")
    print(f"  Time range: {time_ns[0]:.1f}-{time_ns[-1]:.1f} ns ({len(time_ns)} frames)")

    np.savez(
        out_npz,
        time_ns=time_ns,
        rg_nm=rg_nm,
        rg_mean=rg_mean,
        rg_std=rg_std,
    )
    print(f"  Saved: {out_npz.name}")


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
