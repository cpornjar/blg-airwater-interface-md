"""
cas_rg.py
=========
Radius of gyration (Rg) over time for beta-casein, via gmx gyrate.
Mirrors blg_rg.py exactly.

CAS is an IDP started from a single low-pLDDT AlphaFold conformation —
Rg is the standard first sanity check for whether the chain is
compacting/collapsing over the trajectory (a documented failure mode for
CHARMM36+TIP3P on disordered proteins) rather than staying open. No prior
script in this project tracked it; added 2026-08-23 per independent review
flagging the gap before CENTER's numbers get used anywhere.

Usage:
    python -u scripts/analysis/cas_rg.py [--label CENTER|R1]

Output: results/analysis/cas_rg_{label}.npz
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

# Same tpr paths as the other cas_*.py scripts (SP2, q=-2, post-Aug-4 fix).
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

    out_npz = OUT / f"cas_rg_{label}.npz"
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

    print(f"  Rg = {rg_mean:.3f} +/- {rg_std:.3f} nm")
    print(f"  Time range: {time_ns[0]:.1f}-{time_ns[-1]:.1f} ns ({len(time_ns)} frames)")
    print(f"  First 100 ns mean: {rg_nm[time_ns <= 100].mean():.3f} nm | "
          f"Last 100 ns mean: {rg_nm[time_ns >= time_ns[-1] - 100].mean():.3f} nm "
          f"(large drop = possible compaction, check before trusting SASA/contact numbers)")

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
    ap.add_argument("--label", default="CENTER", choices=list(TRAJS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
