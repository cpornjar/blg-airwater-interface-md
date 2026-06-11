"""
blg_pca.py
==========
Principal Component Analysis of BLG conformational space.

Two modes (select with --mode):

  density (default):
    PCA on per-frame Z-density profiles (protein + water).
    Requires blg_density_{label}.npz to exist first.
    Reveals how protein-water density relationship evolves at the interface.
    Output: PC1/PC2 per frame, variance explained.

  structural:
    Standard GROMACS PCA on Cα coordinates.
    Uses gmx covar → gmx anaeig -proj.
    Output: PC1/PC2 projections as time series.

For Fig 3: use density mode to show protein-water density correlation.
The PC1 vs PC2 scatter colored by SASA/contact is the target figure.

Usage:
    python -u scripts/analysis/blg_pca.py [--label CENTER|R1|R2|R3|all] [--mode density|structural]

Output: results/analysis/blg_pca_{mode}_{label}.npz
  keys: time_ns, pc1, pc2, variance_explained (2,), pca_components
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


def parse_xvg(path, skip_cols=1):
    """Read xvg: returns (time, data_array). skip_cols=1 to skip time column."""
    times, rows = [], []
    with open(path) as f:
        for line in f:
            if line.startswith(('#', '@')):
                continue
            parts = line.split()
            if len(parts) >= 2:
                times.append(float(parts[0]))
                rows.append([float(v) for v in parts[skip_cols:]])
    return np.array(times), np.array(rows)


# ── Density PCA ───────────────────────────────────────────────────────────────

def density_pca(label):
    """PCA on stacked (protein_density, water_density) Z-profiles per label."""
    from sklearn.decomposition import PCA as skPCA

    density_npz = OUT / f"blg_density_{label}.npz"
    if not density_npz.exists():
        print(f"  [ERROR] Density cache not found: {density_npz}")
        print(f"  Run blg_density.py --label {label} first.")
        return

    d = np.load(density_npz)
    # density_npz stores the time-averaged profile, not per-frame
    # We need per-frame data — density mode requires gate npz SASA as proxy time axis
    # and loads the averaged profile only. This mode is most useful as a cross-replica
    # comparison rather than per-frame PCA.
    # Load all replicas and do cross-replica density PCA.

    print(f"  Note: density PCA is cross-replica (comparing mean profiles).")
    print(f"  For per-frame density PCA, use structural mode (gmx covar on Cα).")

    # Build feature matrix across replicas: each row = one replica's density profile
    all_labels = [l for l in TRAJS if (OUT / f"blg_density_{l}.npz").exists()]
    if len(all_labels) < 2:
        print(f"  [SKIP] Need at least 2 density profiles for cross-replica PCA.")
        return

    features = []
    for lab in all_labels:
        d = np.load(OUT / f"blg_density_{lab}.npz")
        # Stack protein + water density into one feature vector
        features.append(np.concatenate([d["protein_density"], d["water_density"]]))

    X = np.array(features)   # (n_replicas, n_features)
    pca = skPCA(n_components=min(2, len(all_labels)))
    pca.fit(X)
    projections = pca.transform(X)

    print(f"  Variance explained: PC1={pca.explained_variance_ratio_[0]*100:.1f}%"
          + (f"  PC2={pca.explained_variance_ratio_[1]*100:.1f}%" if len(all_labels) > 2 else ""))

    out_npz = OUT / f"blg_pca_density_{label}.npz"
    np.savez(
        out_npz,
        labels=np.array(all_labels),
        projections=projections,
        components=pca.components_,
        variance_explained=pca.explained_variance_ratio_,
    )
    print(f"  Saved: {out_npz.name}")


# ── Structural PCA (GROMACS covar + anaeig) ───────────────────────────────────

def structural_pca(label):
    """GROMACS Cα PCA via gmx covar + gmx anaeig."""
    cfg = TRAJS[label]
    tpr, xtc = cfg["tpr"], cfg["xtc"]

    if not tpr.exists() or not xtc.exists():
        print(f"  [SKIP] {label}: trajectory files not found")
        return

    out_npz = OUT / f"blg_pca_structural_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Step 1: gmx covar — compute covariance matrix on backbone Cα
        print(f"  Running gmx covar for {label} ...")
        eigenval_xvg = tmpdir / "eigenval.xvg"
        eigenvec_trr = tmpdir / "eigenvec.trr"
        average_pdb  = tmpdir / "average.pdb"
        cmd_covar = [
            GMX, "covar",
            "-f", str(xtc), "-s", str(tpr),
            "-o", str(eigenval_xvg),
            "-v", str(eigenvec_trr),
            "-av", str(average_pdb),
            "-nobackup",
        ]
        result = subprocess.run(
            cmd_covar,
            input="Backbone\n",   # select Backbone (Cα + N + C)
            capture_output=True, text=True, cwd=str(tmpdir),
        )
        if result.returncode != 0:
            print(f"  [ERROR] gmx covar failed")
            print(result.stderr[-2000:])
            return

        # Step 2: gmx anaeig — project trajectory onto PC1 and PC2
        print(f"  Running gmx anaeig for {label} ...")
        proj_xvg = tmpdir / "proj.xvg"
        cmd_anaeig = [
            GMX, "anaeig",
            "-v", str(eigenvec_trr),
            "-f", str(xtc), "-s", str(tpr),
            "-proj", str(proj_xvg),
            "-first", "1", "-last", "2",
            "-nobackup",
        ]
        result = subprocess.run(
            cmd_anaeig,
            input="Backbone\nBackbone\n",
            capture_output=True, text=True, cwd=str(tmpdir),
        )
        if result.returncode != 0:
            print(f"  [ERROR] gmx anaeig failed")
            print(result.stderr[-2000:])
            return

        # Parse projection file and eigenvalues
        time_ps, proj_data = parse_xvg(proj_xvg, skip_cols=1)
        _, eigenvals = parse_xvg(eigenval_xvg, skip_cols=1)

    time_ns = time_ps / 1000.0
    pc1 = proj_data[:, 0] if proj_data.shape[1] > 0 else np.zeros(len(time_ns))
    pc2 = proj_data[:, 1] if proj_data.shape[1] > 1 else np.zeros(len(time_ns))

    total_var = eigenvals[:, 0].sum() if eigenvals.ndim == 2 else eigenvals.sum()
    var_pc1   = eigenvals[0, 0] / total_var if eigenvals.ndim == 2 else eigenvals[0] / total_var
    var_pc2   = eigenvals[1, 0] / total_var if eigenvals.ndim == 2 else eigenvals[1] / total_var

    print(f"  PC1: {var_pc1*100:.1f}%  PC2: {var_pc2*100:.1f}% variance explained")
    print(f"  Time range: {time_ns[0]:.1f}–{time_ns[-1]:.1f} ns")

    np.savez(
        out_npz,
        time_ns=time_ns,
        pc1=pc1,
        pc2=pc2,
        variance_explained=np.array([var_pc1, var_pc2]),
        eigenvalues=eigenvals.flatten() if eigenvals.ndim == 2 else eigenvals,
    )
    print(f"  Saved: {out_npz.name}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="all",
                    choices=["CENTER", "R1", "R2", "R3", "all"])
    ap.add_argument("--mode", default="structural",
                    choices=["density", "structural"])
    args = ap.parse_args()

    labels = list(TRAJS) if args.label == "all" else [args.label]

    for lab in labels:
        print(f"\n=== {lab} — {args.mode} PCA ===")
        if args.mode == "density":
            density_pca(lab)
        else:
            structural_pca(lab)


if __name__ == "__main__":
    main()
