"""
blg_hbonds.py
=============
Hydrogen bond counts for three interaction groups, all BLG replicas.

Groups (Fig 4 — quantitative comparison):
  1. protein–protein (self-interaction)
  2. protein–water
  3. interface water–water (within 1.5 nm of vacuum interface)

Uses MDAnalysis HydrogenBondAnalysis (MDAnalysis 2.x API).
One universe at a time — never load CENTER + R1 simultaneously.

Usage:
    python -u scripts/analysis/blg_hbonds.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_hbonds_{label}.npz
  keys: time_ns,
        n_prot_prot, n_prot_water, n_water_interface
        mean_prot_prot, mean_prot_water, mean_water_interface
"""

import argparse
import gc
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis.hydrogenbonds.hbond_analysis import HydrogenBondAnalysis
from MDAnalysis.transformations import unwrap as mda_unwrap

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

OUT    = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

STRIDE = 5   # every 5 frames (~5 ns) — HBond analysis is slow

TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"],
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_ext.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0002.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0003.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0004.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0005.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0006.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0007.xtc",
        ],
    },
    "R2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.part0002.xtc",
        ],
    },
    "R3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.part0002.xtc",
        ],
    },
}

# Water upper interface ≈ top 98th percentile of water Z (from gate analysis)
# 1.5 nm window below vacuum interface = interface water zone
INTERFACE_WINDOW_NM = 1.5


def find_interface_z(u):
    """Estimate upper water-vacuum interface Z (in Å)."""
    water_o = u.select_atoms("resname SOL and (name OH2 OW O)")
    u.trajectory[0]
    z_vals = water_o.positions[:, 2]
    return np.percentile(z_vals, 98)


def analyse_label(label):
    cfg = TRAJS[label]
    tpr = cfg["tpr"]
    xtc_list = [p for p in cfg["xtc"] if p.exists()]

    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found")
        return
    if not xtc_list:
        print(f"[SKIP] {label}: no xtc files found")
        return

    out_npz = OUT / f"blg_hbonds_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    u = mda.Universe(str(tpr), *[str(x) for x in xtc_list])
    u.trajectory.add_transformations(mda_unwrap(u.atoms))

    n_frames = u.trajectory.n_frames
    interface_z_A = find_interface_z(u)
    print(f"  Frames: {n_frames}  Interface Z ≈ {interface_z_A/10:.2f} nm")
    print(f"  Interface water zone: {(interface_z_A - INTERFACE_WINDOW_NM*10)/10:.2f}–{interface_z_A/10:.2f} nm")

    # 1. Protein–protein HBonds
    print("  Running protein–protein HBond analysis ...")
    hba_pp = HydrogenBondAnalysis(
        u,
        donors_sel="protein",
        acceptors_sel="protein",
        d_a_cutoff=3.5,
        d_h_a_angle_cutoff=150,
        update_selections=False,
    )
    hba_pp.run(step=STRIDE, verbose=True)

    # 2. Protein–water HBonds
    print("  Running protein–water HBond analysis ...")
    hba_pw = HydrogenBondAnalysis(
        u,
        donors_sel="(protein) or (resname SOL and name OH2 OW O)",
        acceptors_sel="(protein) or (resname SOL and name OH2 OW O)",
        d_a_cutoff=3.5,
        d_h_a_angle_cutoff=150,
        update_selections=False,
    )
    hba_pw.run(step=STRIDE, verbose=True)
    # Filter to keep only protein-water pairs
    pp_pw = hba_pw.results.hbonds

    # 3. Interface water–water HBonds
    iz_sel = (f"resname SOL and name OH2 OW O and "
              f"prop z > {interface_z_A - INTERFACE_WINDOW_NM*10:.2f} and "
              f"prop z < {interface_z_A + 5:.2f}")
    print(f"  Running interface water–water HBond analysis ...")
    print(f"    Selection: {iz_sel}")
    hba_ww = HydrogenBondAnalysis(
        u,
        donors_sel=iz_sel,
        acceptors_sel=iz_sel,
        d_a_cutoff=3.5,
        d_h_a_angle_cutoff=150,
        update_selections=True,   # interface Z shifts with trajectory
    )
    hba_ww.run(step=STRIDE, verbose=True)

    # Count HBonds per sampled frame
    sampled_frames = range(0, n_frames, STRIDE)
    times = np.array([u.trajectory[i].time for i in sampled_frames]) / 1000.0  # ns
    n_sampled = len(times)

    def count_per_frame(hba_result, n_frames_sampled):
        counts = np.zeros(n_frames_sampled, dtype=int)
        if len(hba_result) == 0:
            return counts
        frame_col = hba_result[:, 0].astype(int)
        unique, cnts = np.unique(frame_col, return_counts=True)
        for f, c in zip(unique, cnts):
            if f < n_frames_sampled:
                counts[f] = c
        return counts

    n_pp  = count_per_frame(hba_pp.results.hbonds, n_sampled)
    n_pw_all = count_per_frame(pp_pw, n_sampled)
    n_ww  = count_per_frame(hba_ww.results.hbonds, n_sampled)

    # Protein-water = total (prot+water) HBs minus prot-prot
    n_pw = np.maximum(n_pw_all - n_pp, 0)

    print(f"\n  Mean HBond counts:")
    print(f"    Protein–protein:  {n_pp.mean():.1f} ± {n_pp.std():.1f}")
    print(f"    Protein–water:    {n_pw.mean():.1f} ± {n_pw.std():.1f}")
    print(f"    Interface H2O–H2O:{n_ww.mean():.1f} ± {n_ww.std():.1f}")

    np.savez(
        out_npz,
        time_ns=times,
        n_prot_prot=n_pp,
        n_prot_water=n_pw,
        n_water_interface=n_ww,
        mean_prot_prot=n_pp.mean(),
        mean_prot_water=n_pw.mean(),
        mean_water_interface=n_ww.mean(),
    )
    print(f"  Saved: {out_npz.name}")

    del u, hba_pp, hba_pw, hba_ww
    gc.collect()


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
