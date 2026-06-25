"""
blg_calyx_sasa.py
==================
Per-frame SASA of the BLG calyx (hydrophobic pocket), restricted to the
9 calyx-lining residues used throughout this project's calyx-orientation
analyses (blg_gate_analysis.py, blg_set1d_prep.py, blg_fig3_rmsf.py).

SASA is computed for the WHOLE protein per frame (so burial by the rest
of the chain is physically correct, and the result is PBC-corrected via
mda_unwrap), then summed over calyx-atom indices only. This is a
different, smaller quantity than blg_gate_analysis.py's whole-protein
hydrophobic-patch SASA (24-37 nm²) -- this is "how exposed is the calyx
itself".

Verifies the "Calyx SASA: 4.22 +/- 1.02 nm² (CENTER)" figure quoted in
paper/NARRATIVE_REPORT.md (Claim 3), which has no traceable PBC-corrected
source script -- this is the first one.

Usage:
    python -u scripts/analysis/blg_calyx_sasa.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_calyx_sasa_{label}.npz
  keys: time_ns, calyx_sasa_nm2
"""

import argparse
import gc
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.transformations import unwrap as mda_unwrap
import freesasa

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

CALYX_RESIDS = [39, 41, 56, 58, 92, 103, 105, 107, 125]
RADIUS_MAP = {"C": 1.70, "N": 1.55, "O": 1.52, "S": 1.80, "H": 1.20, "P": 1.80}
STRIDE = 5  # 0.5 ns per analysed frame, matches blg_gate_analysis.py

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


def analyse_label(label):
    cfg = TRAJS[label]
    print(f"\n=== {label} ===", flush=True)
    u = (mda.Universe(str(cfg["tpr"]), str(cfg["xtc"][0])) if len(cfg["xtc"]) == 1
         else mda.Universe(str(cfg["tpr"]), *[str(p) for p in cfg["xtc"]]))
    print(f"  Frames: {u.trajectory.n_frames} | dt = {u.trajectory.dt:.1f} ps "
          f"| total = {u.trajectory.totaltime/1000:.1f} ns | stride={STRIDE}", flush=True)

    protein = u.select_atoms("protein")
    u.trajectory.add_transformations(mda_unwrap(protein))
    calyx_mask = np.array([a.resid in CALYX_RESIDS for a in protein.atoms])
    print(f"  Calyx atoms: {calyx_mask.sum()} / {len(protein.atoms)} "
          f"(residues {CALYX_RESIDS})", flush=True)

    radii = [RADIUS_MAP.get(a.name[0].upper(), 1.70) for a in protein.atoms]

    times, calyx_sasa = [], []
    n_done = 0
    for ts in u.trajectory[::STRIDE]:
        coords = protein.positions
        result = freesasa.calcCoord(coords.flatten().tolist(), radii)
        sasa_atoms = np.array([result.atomArea(i) for i in range(len(protein.atoms))])
        calyx_sasa.append(float(sasa_atoms[calyx_mask].sum()) / 100.0)
        times.append(ts.time / 1000.0)
        n_done += 1
        if n_done % 200 == 0:
            print(f"    frame {n_done} | t={times[-1]:.0f} ns | "
                  f"calyx SASA={calyx_sasa[-1]:.2f} nm²", flush=True)

    t = np.array(times)
    s = np.array(calyx_sasa)
    out_npz = OUT / f"blg_calyx_sasa_{label}.npz"
    np.savez(out_npz, time_ns=t, calyx_sasa_nm2=s)
    print(f"  Calyx SASA: {s.mean():.2f} +/- {s.std():.2f} nm²  (n={len(s)})", flush=True)
    print(f"  Saved: {out_npz.name}", flush=True)

    del u
    gc.collect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="CENTER",
                    choices=["CENTER", "R1", "R2", "R3", "all"])
    args = ap.parse_args()

    labels = list(TRAJS) if args.label == "all" else [args.label]
    for lab in labels:
        analyse_label(lab)


if __name__ == "__main__":
    main()
