"""
gate_analysis_all_replicas.py
=============================
Compute SASA, calyx orientation, and nearest-atom distance for each frame of
every replica, then:
  (1) report two-factor gate statistics per replica and aggregate;
  (2) interrogate the R3 21.8 ns gate-open event (120.6–142.4 ns) to verify
      whether the gate was actually open during this event;
  (3) save per-frame data as .npy for re-use and supplementary figures.

Addresses reviewer weaknesses W1 + W2 from review-stage/AUTO_REVIEW.md.

Usage:
    source ~/research-env/bin/activate
    python scripts/gate_analysis_all_replicas.py
"""

from pathlib import Path
import sys
import numpy as np
import MDAnalysis as mda
from MDAnalysis.transformations import unwrap as mda_unwrap
import freesasa

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "results" / "gate_analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Trajectories ──────────────────────────────────────────────────────────────
TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"],
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
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

# ── Constants ─────────────────────────────────────────────────────────────────
CALYX_RESIDS = [39, 41, 56, 58, 92, 103, 105, 107, 125]
HYDROPHOBIC_RESNAMES = ["ALA","VAL","ILE","LEU","PRO","PHE","MET","TRP",
                        "CYS","GLY","TYR","HIS"]
SASA_THR     = 35.0   # nm² — activated
ANGLE_THR    = 30.0   # degrees — aligned
CONTACT_THR  = 0.30   # nm — nearest-atom contact
STRIDE       = 5      # 5 × 100 ps = 0.5 ns per analysed frame
RADIUS_MAP   = {"C":1.70,"N":1.55,"O":1.52,"S":1.80,"H":1.20,"P":1.80}


def calc_frame(protein, calyx, water_o, radii, hydrophobic_mask):
    coords = protein.positions
    # ONE freesasa call per frame, then extract per-atom SASA from the result
    result = freesasa.calcCoord(coords.flatten().tolist(), radii)
    sasa_atoms = np.array([result.atomArea(i) for i in range(len(protein.atoms))])
    sasa_nm2 = float(sasa_atoms[hydrophobic_mask].sum()) / 100.0

    pcom = protein.center_of_mass()
    ccom = calyx.center_of_mass()
    v = ccom - pcom
    v /= np.linalg.norm(v)
    angle = np.degrees(np.arccos(np.clip(-v[2], -1, 1)))

    pz = protein.positions[:, 2]
    wz = water_o.positions[:, 2]
    zu = np.percentile(wz, 98)
    zl = np.percentile(wz, 2)
    d_up = (zu - pz.max()) / 10.0
    d_lo = (pz.min() - zl) / 10.0
    min_dist = min(d_up, d_lo)

    return sasa_nm2, angle, min_dist


def analyse(label, tpr, xtc_list):
    print(f"\n=== {label}: {len(xtc_list)} xtc file(s) ===", flush=True)
    u = (mda.Universe(str(tpr), str(xtc_list[0])) if len(xtc_list) == 1
         else mda.Universe(str(tpr), *[str(p) for p in xtc_list]))
    n_full = u.trajectory.n_frames
    print(f"  Frames: {n_full} | dt = {u.trajectory.dt:.1f} ps "
          f"| total = {u.trajectory.totaltime/1000:.1f} ns | stride={STRIDE}", flush=True)

    protein = u.select_atoms("protein")
    u.trajectory.add_transformations(mda_unwrap(protein))
    calyx   = protein.select_atoms("(" + " or ".join([f"resid {r}" for r in CALYX_RESIDS]) + ")")
    water_o = u.select_atoms("resname SOL and (name OW OH2 O)")

    # pre-compute per-atom static properties (radii, hydrophobic mask)
    radii = [RADIUS_MAP.get(a.name[0].upper(), 1.70) for a in protein.atoms]
    hydrophobic_mask = np.array([a.resname in HYDROPHOBIC_RESNAMES for a in protein.atoms])

    times, sasas, angles, dists = [], [], [], []
    n_done = 0
    for ts in u.trajectory[::STRIDE]:
        s, a, d = calc_frame(protein, calyx, water_o, radii, hydrophobic_mask)
        times.append(ts.time / 1000.0)
        sasas.append(s)
        angles.append(a)
        dists.append(d)
        n_done += 1
        if n_done % 100 == 0:
            print(f"    frame {n_done} | t={times[-1]:.0f} ns | "
                  f"SASA={s:.1f} | angle={a:.0f}° | dmin={d:.2f} nm", flush=True)

    t = np.array(times); s = np.array(sasas); a = np.array(angles); d = np.array(dists)
    np.savez(OUT_DIR / f"{label}_gate.npz",
             time=t, sasa=s, angle=a, min_dist=d)
    print(f"  → saved {OUT_DIR / f'{label}_gate.npz'}", flush=True)
    return t, s, a, d


def gate_stats(label, t, s, a, d):
    n = len(t)
    activated   = s >= SASA_THR
    aligned     = a <= ANGLE_THR
    gate_open   = activated & aligned
    in_contact  = d <= CONTACT_THR
    expected = (activated.mean()) * (aligned.mean())
    obs = gate_open.mean()
    ratio = obs / expected if expected > 0 else float("inf")
    return {
        "label": label,
        "n_frames": n,
        "activated": int(activated.sum()),
        "aligned":   int(aligned.sum()),
        "gate_open": int(gate_open.sum()),
        "in_contact": int(in_contact.sum()),
        "p_activated": activated.mean(),
        "p_aligned":   aligned.mean(),
        "p_gate":      obs,
        "p_independent": expected,
        "ratio_obs_over_indep": ratio,
        "frac_gate_during_contact": (
            (gate_open & in_contact).sum() / max(in_contact.sum(), 1)
        ),
    }


def interrogate_r3_event(t, s, a, d, t0=100.0, t1=150.0,
                         event_start=120.6, event_end=142.4):
    mask = (t >= t0) & (t <= t1)
    tw, sw, aw, dw = t[mask], s[mask], a[mask], d[mask]
    in_event = (tw >= event_start) & (tw <= event_end)

    activated = sw >= SASA_THR
    aligned   = aw <= ANGLE_THR
    gate      = activated & aligned

    n_event = in_event.sum()
    print("\n" + "=" * 70)
    print(f"  R3 EVENT VERIFICATION  ({event_start:.1f} – {event_end:.1f} ns)")
    print("=" * 70)
    print(f"  Analysed frames in event window      : {n_event}")
    print(f"  Frames with SASA  >= {SASA_THR} nm²  : "
          f"{activated[in_event].sum()} / {n_event}  "
          f"({100*activated[in_event].mean():.1f}%)")
    print(f"  Frames with angle <= {ANGLE_THR}°   : "
          f"{aligned[in_event].sum()} / {n_event}  "
          f"({100*aligned[in_event].mean():.1f}%)")
    print(f"  Frames with GATE OPEN (both)         : "
          f"{gate[in_event].sum()} / {n_event}  "
          f"({100*gate[in_event].mean():.1f}%)")
    print(f"  SASA   in event window: mean {sw[in_event].mean():.1f}, "
          f"min {sw[in_event].min():.1f}, max {sw[in_event].max():.1f} nm²")
    print(f"  Angle  in event window: mean {aw[in_event].mean():.0f}°, "
          f"min {aw[in_event].min():.0f}°, max {aw[in_event].max():.0f}°")
    print(f"  Dmin   in event window: mean {dw[in_event].mean():.2f}, "
          f"min {dw[in_event].min():.2f}, max {dw[in_event].max():.2f} nm")
    print("=" * 70)

    return {
        "n_event": int(n_event),
        "activated_in_event": int(activated[in_event].sum()),
        "aligned_in_event":   int(aligned[in_event].sum()),
        "gate_open_in_event": int(gate[in_event].sum()),
        "sasa_mean":  float(sw[in_event].mean()),
        "angle_mean": float(aw[in_event].mean()),
        "dmin_mean":  float(dw[in_event].mean()),
        "verdict": (
            "GATE-OPEN MAJORITY" if gate[in_event].mean() > 0.5 else
            "GATE-OPEN MINORITY" if gate[in_event].mean() > 0.1 else
            "GATE-OPEN RARE/ABSENT — narrative must be qualified"
        ),
    }


def main():
    results = {}
    per_replica = []
    for label, cfg in TRAJS.items():
        cached = OUT_DIR / f"{label}_gate.npz"
        if cached.exists():
            print(f"\n=== {label}: loading cached data {cached.name}")
            z = np.load(cached)
            t, s, a, d = z["time"], z["sasa"], z["angle"], z["min_dist"]
        else:
            t, s, a, d = analyse(label, cfg["tpr"], cfg["xtc"])
        results[label] = (t, s, a, d)
        per_replica.append(gate_stats(label, t, s, a, d))

    # aggregate across all replicas
    t_all = np.concatenate([r[0] for r in results.values()])
    s_all = np.concatenate([r[1] for r in results.values()])
    a_all = np.concatenate([r[2] for r in results.values()])
    d_all = np.concatenate([r[3] for r in results.values()])
    agg = gate_stats("AGGREGATE", t_all, s_all, a_all, d_all)

    # report
    print("\n" + "=" * 80)
    print("  PER-REPLICA TWO-FACTOR GATE STATISTICS")
    print("=" * 80)
    fmt = "{:>10s} | {:>7s} | {:>8s} | {:>8s} | {:>10s} | {:>8s} | {:>8s}"
    print(fmt.format("Replica", "N", "Activ%", "Align%", "GateOpen%",
                     "Indep%", "Obs/Ind"))
    print("-" * 80)
    for r in per_replica + [agg]:
        print(fmt.format(
            r["label"], str(r["n_frames"]),
            f"{100*r['p_activated']:.1f}",
            f"{100*r['p_aligned']:.1f}",
            f"{100*r['p_gate']:.2f}",
            f"{100*r['p_independent']:.2f}",
            f"{r['ratio_obs_over_indep']:.2f}",
        ))
    print("=" * 80)

    # R3 event verification
    t3, s3, a3, d3 = results["R3"]
    r3_event = interrogate_r3_event(t3, s3, a3, d3)

    # write summary file
    summary = OUT_DIR / "GATE_SUMMARY.txt"
    with open(summary, "w") as f:
        f.write("Two-Factor Gate Analysis — All Replicas\n")
        f.write("=" * 80 + "\n")
        f.write(f"Thresholds: SASA >= {SASA_THR} nm², angle <= {ANGLE_THR}°, "
                f"contact <= {CONTACT_THR} nm, stride = {STRIDE} frames "
                f"({STRIDE*0.1:.1f} ns)\n\n")
        f.write(fmt.format("Replica", "N", "Activ%", "Align%", "GateOpen%",
                           "Indep%", "Obs/Ind") + "\n")
        f.write("-" * 80 + "\n")
        for r in per_replica + [agg]:
            f.write(fmt.format(
                r["label"], str(r["n_frames"]),
                f"{100*r['p_activated']:.1f}",
                f"{100*r['p_aligned']:.1f}",
                f"{100*r['p_gate']:.2f}",
                f"{100*r['p_independent']:.2f}",
                f"{r['ratio_obs_over_indep']:.2f}",
            ) + "\n")
        f.write("\n\nR3 21.8 ns EVENT VERIFICATION (120.6 – 142.4 ns)\n")
        f.write("-" * 80 + "\n")
        for k, v in r3_event.items():
            f.write(f"  {k:30s}: {v}\n")
    print(f"\n  → wrote {summary}")


if __name__ == "__main__":
    main()
