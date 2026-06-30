"""
cas_contact.py
==============
Nearest-atom adsorption contact detector for β-casein slab MD trajectories.
Mirrors blg_contact.py logic exactly — minimum distance from ANY protein
heavy atom to the nearest air-water interface, flagged at 0.30 nm.

β-casein is an IDP: expect more frequent / longer contact events than BLG,
consistent with the "open chain" adsorption narrative.

Usage:
    python -u scripts/analysis/cas_contact.py [--label CENTER]

Output: results/analysis/cas_contact_{label}.npz
  keys: time_ns, dmin_nm, pz_max_nm, pz_min_nm, z_up_nm, z_lo_nm,
        n_contact_events, contact_fraction
"""

import argparse
import gc
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

CONTACT_NM   = 0.30   # van der Waals contact threshold
APPROACH_NM  = 0.50   # secondary approach threshold
WATER_UPPER_PCT = 98
WATER_LOWER_PCT = 2
STRIDE = 1            # every frame — contact events can be short

# Add R1 here once outputs_CAS/R1/MD1000/ is set up
TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_CAS/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_CAS/CENTER/MD1000/traj_comp.xtc"],
    },
}


def analyse_label(label):
    cfg = TRAJS[label]
    tpr = cfg["tpr"]
    xtc_list = [p for p in cfg["xtc"] if p.exists()]

    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found at {tpr}")
        return
    if not xtc_list:
        print(f"[SKIP] {label}: no xtc files found")
        return

    out_npz = OUT / f"cas_contact_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===", flush=True)
    u = (mda.Universe(str(tpr), str(xtc_list[0]))
         if len(xtc_list) == 1
         else mda.Universe(str(tpr), *[str(p) for p in xtc_list]))

    protein = u.select_atoms("protein and not name H*")
    water_o = u.select_atoms("resname SOL and (name OH2 OW O)")
    print(f"  Frames: {u.trajectory.n_frames}  Protein heavy atoms: {len(protein)}")
    print(f"  dt = {u.trajectory.dt:.1f} ps | total = {u.trajectory.totaltime/1000:.1f} ns")

    times, dmin, pz_max, pz_min, z_up, z_lo = [], [], [], [], [], []

    for ts in u.trajectory[::STRIDE]:
        pz = protein.positions[:, 2]
        wz = water_o.positions[:, 2]
        zu = np.percentile(wz, WATER_UPPER_PCT)
        zl = np.percentile(wz, WATER_LOWER_PCT)

        d_up = (zu - pz.max()) / 10.0   # nm, positive = inside slab
        d_lo = (pz.min() - zl) / 10.0

        times.append(ts.time / 1000.0)
        dmin.append(min(d_up, d_lo))
        pz_max.append(pz.max() / 10.0)
        pz_min.append(pz.min() / 10.0)
        z_up.append(zu / 10.0)
        z_lo.append(zl / 10.0)

        if len(times) % 500 == 0:
            print(f"  frame {len(times)} | t={times[-1]:.0f} ns | dmin={dmin[-1]:.3f} nm",
                  flush=True)

    t   = np.array(times)
    d   = np.array(dmin)
    n_contact = int((d <= CONTACT_NM).sum())
    n_events  = _count_events(d, CONTACT_NM)

    print(f"\n  Contact frames (≤{CONTACT_NM} nm): {n_contact}/{len(d)} "
          f"({100*n_contact/len(d):.1f}%)")
    print(f"  Contact events: {n_events}")

    np.savez(
        out_npz,
        time_ns=np.array(times),
        dmin_nm=d,
        pz_max_nm=np.array(pz_max),
        pz_min_nm=np.array(pz_min),
        z_up_nm=np.array(z_up),
        z_lo_nm=np.array(z_lo),
        n_contact_events=n_events,
        contact_fraction=n_contact / len(d),
    )
    print(f"  Saved: {out_npz.name}")

    del u
    gc.collect()


def _count_events(d, threshold):
    below = d <= threshold
    if not below.any():
        return 0
    edges = np.diff(below.astype(int))
    starts = np.where(edges == 1)[0]
    if below[0]:
        starts = np.concatenate([[0], starts])
    return len(starts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="CENTER", choices=list(TRAJS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
