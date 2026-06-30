"""
cas_hbonds.py
=============
Hydrogen bond counts for three interaction groups, β-casein CENTER.
Mirrors blg_hbonds.py exactly — same groups, same thresholds.

Groups (Fig 4 comparison table):
  1. protein–protein
  2. protein–water
  3. interface water–water (within 1.5 nm of vacuum interface)

β-casein is an IDP with more exposed backbone — expect higher
protein–water HB count than BLG.

Frame-index bug (blg_hbonds.py post-mortem, June 11): count_per_frame()
must index the sampled-frame array by `frame_col // STRIDE`, NOT raw
frame_col. This is correct in this script — do NOT change the indexing.

Usage:
    python -u scripts/analysis/cas_hbonds.py [--label CENTER]

Output: results/analysis/cas_hbonds_{label}.npz
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

OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

STRIDE = 5
INTERFACE_WINDOW_NM = 1.5

# Add R1 here once outputs_CAS/R1/MD1000/ is set up
TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_CAS/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_CAS/CENTER/MD1000/traj_comp.xtc"],
    },
}


def find_interface_z(u):
    water_o = u.select_atoms("resname SOL and (name OH2 OW O)")
    u.trajectory[0]
    return np.percentile(water_o.positions[:, 2], 98)


def count_per_frame(hba_result, n_frames_sampled):
    counts = np.zeros(n_frames_sampled, dtype=int)
    if len(hba_result) == 0:
        return counts
    frame_col = hba_result[:, 0].astype(int)
    unique, cnts = np.unique(frame_col, return_counts=True)
    idx = unique // STRIDE   # raw frame number → sampled-frame index
    for i, c in zip(idx, cnts):
        if i < n_frames_sampled:
            counts[i] = c
    return counts


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

    out_npz = OUT / f"cas_hbonds_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    u = (mda.Universe(str(tpr), str(xtc_list[0]))
         if len(xtc_list) == 1
         else mda.Universe(str(tpr), *[str(p) for p in xtc_list]))
    u.trajectory.add_transformations(mda_unwrap(u.atoms))

    n_frames = u.trajectory.n_frames
    interface_z_A = find_interface_z(u)
    print(f"  Frames: {n_frames}  Interface Z ≈ {interface_z_A/10:.2f} nm")

    print("  Running protein–protein HBond analysis ...")
    hba_pp = HydrogenBondAnalysis(
        u,
        donors_sel="protein", acceptors_sel="protein",
        d_a_cutoff=3.5, d_h_a_angle_cutoff=150, update_selections=False,
    )
    hba_pp.run(step=STRIDE, verbose=True)

    print("  Running protein–water HBond analysis ...")
    hba_pw = HydrogenBondAnalysis(
        u,
        donors_sel="(protein) or (resname SOL and name OH2 OW O)",
        acceptors_sel="(protein) or (resname SOL and name OH2 OW O)",
        d_a_cutoff=3.5, d_h_a_angle_cutoff=150, update_selections=False,
    )
    hba_pw.run(step=STRIDE, verbose=True)

    iz_sel = (f"resname SOL and name OH2 OW O and "
              f"prop z > {interface_z_A - INTERFACE_WINDOW_NM*10:.2f} and "
              f"prop z < {interface_z_A + 5:.2f}")
    print(f"  Running interface water–water HBond analysis ...")
    hba_ww = HydrogenBondAnalysis(
        u,
        donors_sel=iz_sel, acceptors_sel=iz_sel,
        d_a_cutoff=3.5, d_h_a_angle_cutoff=150, update_selections=True,
    )
    hba_ww.run(step=STRIDE, verbose=True)

    sampled_frames = range(0, n_frames, STRIDE)
    times = np.array([u.trajectory[i].time for i in sampled_frames]) / 1000.0
    n_sampled = len(times)

    n_pp     = count_per_frame(hba_pp.results.hbonds, n_sampled)
    n_pw_all = count_per_frame(hba_pw.results.hbonds, n_sampled)
    n_ww     = count_per_frame(hba_ww.results.hbonds, n_sampled)
    n_pw     = np.maximum(n_pw_all - n_pp, 0)

    print(f"\n  Mean HBond counts:")
    print(f"    Protein–protein:   {n_pp.mean():.1f} ± {n_pp.std():.1f}")
    print(f"    Protein–water:     {n_pw.mean():.1f} ± {n_pw.std():.1f}")
    print(f"    Interface H2O–H2O: {n_ww.mean():.1f} ± {n_ww.std():.1f}")

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
    ap.add_argument("--label", default="CENTER", choices=list(TRAJS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
