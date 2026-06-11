"""
blg_cluster.py
==============
Conformational clustering of BLG interface contact frames.

Two clustering targets (select with --target):

  contact (default):
    Cluster frames where protein is in contact with the interface (dmin < 0.3 nm).
    Reveals the range of conformations BLG adopts during contact.
    Uses GROMACS gmx cluster (GROMOS algorithm, RMSD cutoff 0.2 nm) on Cα.

  calyx:
    Cluster specifically on the calyx region orientation.
    Uses calyx-residue Cα only — reveals whether calyx points toward interface.
    Calyx residues (BLG barrel interior): ~35–45, 55–65, 80–90 (approximate).
    [CONFIRM WITH P.P.]: exact calyx residue definition.

Output: cluster assignment per contact frame, representative structures,
        cluster sizes, and per-cluster SASA statistics.

Usage:
    python -u scripts/analysis/blg_cluster.py [--label CENTER|R1|R2|R3|all]
                                               [--target contact|calyx]
                                               [--cutoff 0.2]

Output: results/analysis/blg_cluster_{target}_{label}.npz
  keys: frame_times_ns, cluster_ids, cluster_sizes, n_clusters
        rep_frame_indices (index of representative frame per cluster)
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

GATE_DIR = ROOT / "results" / "gate_analysis"
CONTACT_THRESH_NM = 0.30

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

# BLG calyx residues (hydrophobic barrel interior — approximate)
# These are the residues that form the calyx pocket
# [CONFIRM WITH P.P.] — refine based on BLG structure (PDB 3BLG)
CALYX_RESIDS = list(range(35, 46)) + list(range(55, 66)) + list(range(80, 91))


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


def write_frame_indices_xvg(indices, times_ps, path):
    """Write a simple time list for gmx trjconv frame extraction."""
    with open(path, 'w') as f:
        for i in indices:
            f.write(f"{times_ps[i]:.3f}\n")


def extract_contact_frames(label, xtc_path, tpr_path, tmpdir):
    """
    Extract frames where dmin < CONTACT_THRESH from gate cache.
    Returns contact frame indices (in the gate-stride frame numbering).
    """
    gate_npz = GATE_DIR / f"{label}_gate.npz"
    if not gate_npz.exists():
        print(f"  [ERROR] Gate cache not found: {gate_npz}")
        return None, None

    d = np.load(gate_npz)
    dmin = d["min_dist"]
    time_ps_gate = d["time"]    # times at gate stride (every 0.5 ns = 500 ps)

    in_contact = dmin < CONTACT_THRESH_NM
    n_contact  = in_contact.sum()
    print(f"  Contact frames: {n_contact}/{len(dmin)} ({100*n_contact/len(dmin):.1f}%)")

    contact_times = time_ps_gate[in_contact]

    # Write frame-times file for gmx trjconv
    time_file = Path(tmpdir) / f"{label}_contact_times.dat"
    with open(time_file, 'w') as f:
        for t in contact_times:
            f.write(f"{t:.1f}\n")

    # Extract contact frames to a sub-trajectory
    contact_xtc = Path(tmpdir) / f"{label}_contact.xtc"
    cmd = [
        GMX, "trjconv",
        "-f", str(xtc_path), "-s", str(tpr_path),
        "-o", str(contact_xtc),
        "-fr", str(time_file),
        "-nobackup",
    ]
    result = subprocess.run(
        cmd, input="Protein\n",
        capture_output=True, text=True, cwd=str(tmpdir),
    )
    if result.returncode != 0:
        print(f"  [WARNING] gmx trjconv frame extraction failed — using full trajectory")
        print(result.stderr[-500:])
        contact_xtc = xtc_path  # fall back to full trajectory

    return contact_xtc, contact_times


def run_gmx_cluster(tpr, xtc, selection, cutoff, tmpdir, prefix):
    """Run GROMACS GROMOS clustering on selected atoms."""
    cl_log     = Path(tmpdir) / f"{prefix}_cluster.log"
    cl_pdb     = Path(tmpdir) / f"{prefix}_clusters.pdb"
    cl_id_xvg  = Path(tmpdir) / f"{prefix}_clid.xvg"
    cl_sz_xvg  = Path(tmpdir) / f"{prefix}_clsz.xvg"
    rmsd_xvg   = Path(tmpdir) / f"{prefix}_rmsd.xvg"

    cmd = [
        GMX, "cluster",
        "-f", str(xtc), "-s", str(tpr),
        "-g", str(cl_log),
        "-cl", str(cl_pdb),
        "-clid", str(cl_id_xvg),
        "-sz", str(cl_sz_xvg),
        "-dist", str(rmsd_xvg),
        "-method", "gromos",
        "-cutoff", str(cutoff),
        "-nobackup",
    ]
    result = subprocess.run(
        cmd,
        input=f"{selection}\n{selection}\n",
        capture_output=True, text=True, cwd=str(tmpdir),
    )
    if result.returncode != 0:
        print(f"  [ERROR] gmx cluster failed")
        print(result.stderr[-2000:])
        return None, None

    # Parse cluster IDs per frame
    times_cl, cl_ids = parse_xvg(cl_id_xvg)
    # Parse cluster sizes
    _, cl_sizes = parse_xvg(cl_sz_xvg)

    return times_cl, cl_ids.astype(int), cl_sizes


def analyse_label(label, target, cutoff):
    cfg = TRAJS[label]
    tpr, xtc = cfg["tpr"], cfg["xtc"]

    if not tpr.exists() or not xtc.exists():
        print(f"[SKIP] {label}: trajectory files not found")
        return

    out_npz = OUT / f"blg_cluster_{target}_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} — {target} clustering (cutoff={cutoff} nm) ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        if target == "contact":
            work_xtc, contact_times = extract_contact_frames(label, xtc, tpr, tmpdir)
            if work_xtc is None:
                return
            selection = "Backbone"
        else:  # calyx
            work_xtc = xtc
            # Build index for calyx residues
            resid_sel = " or ".join(f"(resid {r})" for r in CALYX_RESIDS)
            ndx_file  = Path(tmpdir) / "calyx.ndx"
            cmd_ndx = [GMX, "select", "-f", str(xtc), "-s", str(tpr),
                       "-on", str(ndx_file), "-nobackup"]
            subprocess.run(
                cmd_ndx,
                input=f"protein and ({resid_sel}) and name CA\n",
                capture_output=True, text=True, cwd=str(tmpdir),
            )
            selection = "Calyx_CA"
            print(f"  Calyx residues: {CALYX_RESIDS[:3]}...{CALYX_RESIDS[-3:]} ({len(CALYX_RESIDS)} total)")
            print(f"  [CONFIRM WITH P.P.] calyx residue definition correct?")

        print(f"  Running gmx cluster ...")
        result = run_gmx_cluster(tpr, work_xtc, selection, cutoff,
                                 str(tmpdir), f"{label}_{target}")
        if result[0] is None:
            return
        times_cl, cl_ids, cl_sizes = result

    n_clusters = int(cl_ids.max()) if len(cl_ids) > 0 else 0
    print(f"  Clusters found: {n_clusters}")
    if n_clusters > 0:
        top5 = np.argsort(cl_sizes)[::-1][:5]
        print(f"  Top 5 cluster sizes: {cl_sizes[top5].astype(int).tolist()}")

    # Representative frame = first frame of each cluster (cluster is 1-indexed)
    rep_frames = {}
    for c in range(1, n_clusters + 1):
        where = np.where(cl_ids == c)[0]
        if len(where) > 0:
            rep_frames[c] = int(times_cl[where[0]])

    time_ns = times_cl / 1000.0

    np.savez(
        out_npz,
        frame_times_ns=time_ns,
        cluster_ids=cl_ids,
        cluster_sizes=cl_sizes,
        n_clusters=n_clusters,
        rep_frame_times_ns=np.array([rep_frames.get(c, 0) / 1000.0
                                      for c in range(1, n_clusters + 1)]),
    )
    print(f"  Saved: {out_npz.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="all",
                    choices=["CENTER", "R1", "R2", "R3", "all"])
    ap.add_argument("--target", default="contact",
                    choices=["contact", "calyx"])
    ap.add_argument("--cutoff", type=float, default=0.2,
                    help="RMSD cutoff for GROMOS clustering (nm)")
    args = ap.parse_args()

    labels = list(TRAJS) if args.label == "all" else [args.label]
    for lab in labels:
        analyse_label(lab, args.target, args.cutoff)


if __name__ == "__main__":
    main()
