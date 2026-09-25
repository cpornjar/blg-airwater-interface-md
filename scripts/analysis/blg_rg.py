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
        "xtc": [ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"],
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
        "xtc": [ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc"] +
               sorted((ROOT / "outputs_BLG/REPLICA/MD/MD1").glob("md_replica1_amd.part00*.xtc")),
    },
    "R2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2.tpr",
        "xtc": [ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
                ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.part0002.xtc"],
    },
    "R3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3.tpr",
        "xtc": [ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
                ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.part0002.xtc"],
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


def concat_xtc(xtc_list, tmpdir):
    """gmx gyrate's -f only accepts one file per this GROMACS build (tested:
    passing multiple files errors 'Too many values') — unlike MDAnalysis's
    Universe(), which concatenates multiple xtc args natively. Use gmx trjcat
    first to merge continuation segments into one xtc; trjcat sorts by
    timestamp and drops duplicate-time frames by default, which is exactly
    right for continuation parts that may share a checkpoint-restart frame."""
    if len(xtc_list) == 1:
        return xtc_list[0]
    out_xtc = Path(tmpdir) / "concat.xtc"
    cmd = [GMX, "trjcat", "-f", *[str(x) for x in xtc_list], "-o", str(out_xtc), "-nobackup"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=tmpdir)
    if result.returncode != 0:
        print(f"  [ERROR] gmx trjcat failed")
        print(result.stderr[-2000:])
        return None
    return out_xtc


def run_gyrate(tpr, xtc_list, out_xvg, tmpdir):
    xtc = concat_xtc(xtc_list, tmpdir)
    if xtc is None:
        return None
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
    tpr = cfg["tpr"]
    xtc_list = [p for p in cfg["xtc"] if p.exists()]

    if not tpr.exists() or not xtc_list:
        print(f"[SKIP] {label}: trajectory files not found")
        return

    out_npz = OUT / f"blg_rg_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} === ({len(xtc_list)} xtc segment(s): {[p.name for p in xtc_list]})")
    with tempfile.TemporaryDirectory() as tmpdir:
        xvg_path = Path(tmpdir) / f"{label}_gyrate.xvg"
        result = run_gyrate(tpr, xtc_list, xvg_path, tmpdir)
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
