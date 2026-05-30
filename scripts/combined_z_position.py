"""
combined_z_position.py
=======================
Combined Z-position figure: CENTER run + all 3 Plan B replicas in one panel.
Used as Figure 5A in Paper 1.

Expects pre-computed numpy arrays saved by run_replica_analysis.py, OR
reads directly from trajectory files.

Usage (with saved arrays):
    python scripts/combined_z_position.py --from-cache

Usage (from trajectories — slow):
    python scripts/combined_z_position.py
"""

import numpy as np
import matplotlib.pyplot as plt
import os, glob, argparse
from plot_style import (apply_style, COLORS, double_width,
                        add_adsorption_line, savefig, smooth_sg)
apply_style()

OUTPUT_PNG  = "results/figures/z_position/COMBINED_z_position.png"
CACHE_DIR   = "results/cache"

# Trajectory file locations
RUNS = {
    "CENTER (1,000 ns)" : {
        "tpr": "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": "outputs_BLG/CENTER/MD1000/traj_comp.xtc",
        "color": COLORS["center"],
        "lw": 1.8,
    },
    "Replica 1" : {
        "tpr": "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
        "xtc": "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
        "color": COLORS["replica1"],
        "lw": 1.2,
    },
    "Replica 2" : {
        "tpr": "outputs_BLG/REPLICA/MD/MD2/md_replica2.tpr",
        "xtc": "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
        "color": COLORS["replica2"],
        "lw": 1.2,
    },
    "Replica 3" : {
        "tpr": "outputs_BLG/REPLICA/MD/MD3/md_replica3.tpr",
        "xtc": "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
        "color": COLORS["replica3"],
        "lw": 1.2,
    },
}


def load_from_trajectory(tpr, xtc, stride=5):
    import MDAnalysis as mda
    from MDAnalysis.transformations import unwrap

    u       = mda.Universe(tpr, xtc)
    protein = u.select_atoms("protein")
    water   = u.select_atoms("resname SOL")
    u.trajectory.add_transformations(unwrap(protein))

    times, z_prot, dist = [], [], []
    for ts in u.trajectory[::stride]:
        t_ns    = ts.time / 1000.0
        prot_z  = protein.center_of_mass()[2] / 10.0   # Å → nm
        wat_z   = water.select_atoms("name OH2 OW O").positions[:, 2]
        upper   = np.percentile(wat_z, 98) / 10.0
        d       = upper - prot_z
        times.append(t_ns)
        z_prot.append(prot_z)
        dist.append(d)

    return np.array(times), np.array(z_prot), np.array(dist)


def plot(datasets):
    """
    datasets: dict of label -> (times_ns, dist_to_interface_nm)
    """
    fig, ax = plt.subplots(figsize=(double_width, 2.8))

    for label, (times, dist, color, lw) in datasets.items():
        ls = "-" if "CENTER" in label else "--"
        ax.plot(times, dist, color=color, lw=lw * 0.4, alpha=0.2,
                rasterized=True)
        ax.plot(times, smooth_sg(dist, window=31), color=color,
                lw=lw, ls=ls, label=label)

    add_adsorption_line(ax, horizontal=True)

    # Annotate minimum per replica
    for label, (times, dist, color, lw) in datasets.items():
        idx = np.argmin(dist)
        ax.scatter(times[idx], dist[idx], color=color, s=25, zorder=5,
                   edgecolors="white", linewidths=0.5)
        va = "bottom" if dist[idx] > 0.8 else "top"
        ax.annotate(f"{dist[idx]:.2f} nm",
                    xy=(times[idx], dist[idx]),
                    xytext=(0, 5 if va == "bottom" else -5),
                    textcoords="offset points",
                    fontsize=6.5, color=color, ha="center", va=va)

    ax.set_xlabel("Time (ns)")
    ax.set_ylabel("Distance to interface (nm)")
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper right", ncol=2)

    os.makedirs(os.path.dirname(OUTPUT_PNG), exist_ok=True)
    savefig(fig, OUTPUT_PNG)
    print(f"Saved → {OUTPUT_PNG}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-cache", action="store_true",
                        help="Load pre-computed arrays from results/cache/")
    args = parser.parse_args()

    # Change to workspace root
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)

    datasets = {}
    for label, cfg in RUNS.items():
        cache_file = os.path.join(CACHE_DIR, f"{label.replace(' ', '_')}_dist.npz")

        if args.from_cache and os.path.exists(cache_file):
            d = np.load(cache_file)
            times, dist = d["times"], d["dist"]
            print(f"  Loaded from cache: {label}")
        else:
            tpr, xtc = cfg["tpr"], cfg["xtc"]
            if not os.path.exists(xtc):
                print(f"  SKIP (file not found): {xtc}")
                continue
            print(f"  Loading trajectory: {label}")
            times, _, dist = load_from_trajectory(tpr, xtc)
            os.makedirs(CACHE_DIR, exist_ok=True)
            np.savez(cache_file, times=times, dist=dist)

        datasets[label] = (times, dist, cfg["color"], cfg["lw"])

    if datasets:
        plot(datasets)
    else:
        print("No data loaded. Check trajectory paths or run without --from-cache.")
