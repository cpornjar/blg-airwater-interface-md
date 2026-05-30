"""
sasa_z_correlation.py
=====================
Scatter plot: Hydrophobic SASA vs Distance to Interface — shows that
activation events (high SASA) correlate with closest approach to interface.

This is the key mechanistic evidence figure for Paper 1.
Colours points by time to show temporal progression.

Usage:
    cd Workspace/MILK_FROTHING
    source ~/research-env/bin/activate
    python scripts/sasa_z_correlation.py --run CENTER
    python scripts/sasa_z_correlation.py --run R1
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import MDAnalysis as mda
import freesasa
import argparse, os
from MDAnalysis.transformations import unwrap
from plot_style import (apply_style, COLORS, col_width, double_width,
                        ADSORPTION_THRESHOLD_NM, savefig)
apply_style()

# ── CONFIG ────────────────────────────────────────────────────────────────────
RUNS = {
    "CENTER": {
        "tpr": "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": "outputs_BLG/CENTER/MD1000/traj_comp.xtc",
        "label": "CENTER (1,000 ns)",
        "color_map": "plasma",
    },
    "R1": {
        "tpr": "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
        "xtc": "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
        "label": "Replica 1 (500 ns)",
        "color_map": "viridis",
    },
}

HYDROPHOBIC_RESNAMES = ["ALA","VAL","LEU","ILE","PRO","PHE","MET","TRP"]
STRIDE = 10   # coarser stride OK for scatter
# ──────────────────────────────────────────────────────────────────────────────


def load_data(tpr, xtc, stride):
    u       = mda.Universe(tpr, xtc)
    protein = u.select_atoms("protein")
    water   = u.select_atoms("resname SOL")
    u.trajectory.add_transformations(unwrap(protein))

    mask_hydrophob = np.array([
        atom.resname in HYDROPHOBIC_RESNAMES for atom in protein.atoms])

    radius_map = {"C":1.70,"N":1.55,"O":1.52,"S":1.80,"H":1.20,"P":1.80}
    radii      = np.array([radius_map.get(a.name[0].upper(), 1.70)
                           for a in protein.atoms])

    times, sasa_h, dist = [], [], []

    frames = list(range(0, u.trajectory.n_frames, stride))
    print(f"  Analyzing {len(frames)} frames ...")

    for i, fi in enumerate(frames):
        u.trajectory[fi]
        t_ns = u.trajectory.time / 1000.0

        # SASA
        result    = freesasa.calcCoord(
            protein.positions.flatten().tolist(), radii.tolist())
        sasa_atoms = np.array([result.atomArea(j)
                                for j in range(len(protein.atoms))]) / 100.0
        h_sasa = np.sum(sasa_atoms[mask_hydrophob])

        # Distance to upper interface
        wat_z = water.select_atoms("name OH2 OW O").positions[:, 2]
        upper = np.percentile(wat_z, 98) / 10.0
        prot_z = protein.center_of_mass()[2] / 10.0
        d = upper - prot_z

        times.append(t_ns)
        sasa_h.append(h_sasa)
        dist.append(d)

        if (i + 1) % 20 == 0:
            print(f"    [{i+1}/{len(frames)}] t={t_ns:.0f} ns  "
                  f"HydSASA={h_sasa:.1f} nm²  dist={d:.2f} nm")

    return np.array(times), np.array(sasa_h), np.array(dist)


def plot_single(times, sasa_h, dist, label, cmap_name, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(double_width, 2.8))

    # ── Left: scatter SASA vs distance, coloured by time ─────────────────────
    ax = axes[0]
    sc = ax.scatter(dist, sasa_h, c=times, cmap=cmap_name,
                    s=6, alpha=0.75, linewidths=0, rasterized=True)
    cb = plt.colorbar(sc, ax=ax, pad=0.02)
    cb.set_label("Time (ns)", fontsize=8)
    ax.axvline(ADSORPTION_THRESHOLD_NM, color="black", lw=0.8, ls="--",
               alpha=0.6, label=f"Adsorption threshold ({ADSORPTION_THRESHOLD_NM} nm)")
    ax.set_xlabel("Distance to interface (nm)")
    ax.set_ylabel("Hydrophobic SASA (nm²)")
    ax.set_title("Activation vs. interface approach", fontsize=8)
    ax.legend(fontsize=7)

    # ── Right: time series of both overlaid ───────────────────────────────────
    ax2   = axes[1]
    ax2b  = ax2.twinx()
    ax2.plot(times, sasa_h, color=COLORS["hydrophob"],
             lw=0.5, alpha=0.25, rasterized=True)
    ax2.plot(times, _sg(sasa_h), color=COLORS["hydrophob"],
             lw=1.5, label="Hydrophobic SASA")
    ax2b.plot(times, dist, color=COLORS["distance"],
              lw=0.5, alpha=0.25, rasterized=True)
    ax2b.plot(times, _sg(dist), color=COLORS["distance"],
              lw=1.2, ls="--", label="Dist. to interface")
    ax2b.axhline(ADSORPTION_THRESHOLD_NM, color="black",
                 lw=0.6, ls=":", alpha=0.5)
    ax2.set_xlabel("Time (ns)")
    ax2.set_ylabel("Hydrophobic SASA (nm²)", color=COLORS["hydrophob"])
    ax2b.set_ylabel("Distance to interface (nm)", color=COLORS["distance"])
    ax2.set_title("Time series overlay", fontsize=8)
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2b.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=7)

    plt.suptitle(label, fontsize=8, y=1.01)
    plt.tight_layout(w_pad=0.8)
    savefig(fig, out_path)
    print(f"Saved → {out_path}")

    # Print correlation coefficient
    r = np.corrcoef(sasa_h, dist)[0, 1]
    print(f"  Pearson r (hydrophobic SASA vs dist): {r:.3f}")
    print(f"  Interpretation: negative r means higher SASA when closer to interface")


def _sg(data):
    from plot_style import smooth_sg
    return smooth_sg(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="CENTER",
                        choices=list(RUNS.keys()) + ["ALL"],
                        help="Which run to analyse (CENTER, R1, ALL)")
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    os.makedirs("results/figures/sasa", exist_ok=True)

    runs = RUNS if args.run == "ALL" else {args.run: RUNS[args.run]}

    for key, cfg in runs.items():
        out = f"results/figures/sasa/{key}_sasa_z_correlation.png"
        print(f"\nProcessing: {cfg['label']}")
        times, sasa_h, dist = load_data(cfg["tpr"], cfg["xtc"], STRIDE)
        plot_single(times, sasa_h, dist, cfg["label"], cfg["color_map"], out)
