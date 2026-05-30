"""
sasa_analysis.py
=================
วิเคราะห์ SASA ของ 1BEB โปรตีนแบ่งเป็น 4 ส่วน:
  1. Total SASA
  2. Hydrophobic SASA
  3. Hydrophilic SASA
  4. Calyx patch SASA

Requirements:
    pip install MDAnalysis matplotlib numpy freesasa

Usage:
    python sasa_analysis.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import MDAnalysis as mda
import freesasa
from plot_style import (apply_style, COLORS, col_width, double_width,
                        ACTIVATION_WINDOWS, add_activation_windows, savefig, smooth_sg)
apply_style()

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
TPR_FILE   = "md_1000ns.tpr"
XTC_FILE   = "traj_comp.xtc"
OUTPUT_PNG = "sasa_analysis.png"

HYDROPHOBIC_RESNAMES = [
    "ALA", "VAL", "LEU", "ILE", "PRO",
    "PHE", "MET", "TRP"
]

CALYX_RESIDS = [39, 41, 56, 58, 92, 103, 105, 107, 125]

STRIDE = 5
# ─────────────────────────────────────────


def load_universe():
    print(f"[1/4] Loading: {XTC_FILE}")
    u = mda.Universe(TPR_FILE, XTC_FILE)
    n = len(range(0, u.trajectory.n_frames, STRIDE))
    print(f"      {u.trajectory.n_frames} frames | "
          f"Analyzing {n} frames (stride={STRIDE}) | "
          f"Total = {u.trajectory.totaltime/1000:.1f} ns")
    return u


def calc_sasa_frame(protein):
    """คำนวณ SASA ของ protein atoms ใน frame ปัจจุบัน ด้วย freesasa"""
    coords = protein.positions   # Angstrom

    radius_map = {
        "C": 1.70, "N": 1.55, "O": 1.52,
        "S": 1.80, "H": 1.20, "P": 1.80,
    }
    radii = []
    for atom in protein.atoms:
        element = atom.name[0].upper()
        radii.append(radius_map.get(element, 1.70))
    radii = np.array(radii)

    result = freesasa.calcCoord(
        coords.flatten().tolist(),
        radii.tolist()
    )

    sasa_atoms = np.array([result.atomArea(i) for i in range(len(protein.atoms))])
    return sasa_atoms / 100.0   # A² → nm²


def analyze(u):
    print("[2/4] Computing SASA ...")

    protein = u.select_atoms("protein")

    mask_hydrophob = np.array([
        atom.resname in HYDROPHOBIC_RESNAMES
        for atom in protein.atoms
    ])
    mask_hydrophil = ~mask_hydrophob
    mask_calyx     = np.array([
        atom.resid in CALYX_RESIDS
        for atom in protein.atoms
    ])

    times          = []
    sasa_total     = []
    sasa_hydrophob = []
    sasa_hydrophil = []
    sasa_calyx     = []

    frames = list(range(0, u.trajectory.n_frames, STRIDE))

    for i, frame_idx in enumerate(frames):
        u.trajectory[frame_idx]
        t_ns = u.trajectory.time / 1000.0

        sasa_atoms = calc_sasa_frame(protein)

        times.append(t_ns)
        sasa_total.append(np.sum(sasa_atoms))
        sasa_hydrophob.append(np.sum(sasa_atoms[mask_hydrophob]))
        sasa_hydrophil.append(np.sum(sasa_atoms[mask_hydrophil]))
        sasa_calyx.append(np.sum(sasa_atoms[mask_calyx]))

        if (i + 1) % 20 == 0 or i == 0:
            print(f"      [{i+1}/{len(frames)}] t = {t_ns:.1f} ns | "
                  f"Total = {sasa_total[-1]:.2f} nm² | "
                  f"Hydrophobic = {sasa_hydrophob[-1]:.2f} nm²")

    return (np.array(times),
            np.array(sasa_total),
            np.array(sasa_hydrophob),
            np.array(sasa_hydrophil),
            np.array(sasa_calyx))


def print_summary(times, total, hydrophob, hydrophil, calyx):
    ratio = np.mean(hydrophob / total) * 100
    print("\n-- SASA Summary ------------------------------------")
    print(f"  Total SASA        : {np.mean(total):.2f} +/- {np.std(total):.2f} nm2")
    print(f"  Hydrophobic SASA  : {np.mean(hydrophob):.2f} +/- {np.std(hydrophob):.2f} nm2")
    print(f"  Hydrophilic SASA  : {np.mean(hydrophil):.2f} +/- {np.std(hydrophil):.2f} nm2")
    print(f"  Calyx patch SASA  : {np.mean(calyx):.2f} +/- {np.std(calyx):.2f} nm2")
    print(f"  Hydrophobic ratio : {ratio:.1f}% of total surface")
    print("----------------------------------------------------\n")


def plot(times, total, hydrophob, hydrophil, calyx):
    print("[3/4] Plotting ...")

    datasets = [
        (total,     COLORS["total_sasa"], "Total SASA (nm²)",       "Entire protein surface"),
        (hydrophob, COLORS["hydrophob"],  "Hydrophobic SASA (nm²)", "Non-polar residues"),
        (hydrophil, COLORS["hydrophil"],  "Hydrophilic SASA (nm²)", "Polar/charged residues"),
        (calyx,     COLORS["calyx"],      "Calyx patch SASA (nm²)", "Hydrophobic pocket (1BEB)"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(double_width, 5.5), sharex=True)
    axes = axes.flatten()

    for ax, (data, color, ylabel, subtitle) in zip(axes, datasets):
        s    = smooth_sg(data)
        mean = np.mean(data)
        ax.plot(times, data, color=color, lw=0.5, alpha=0.25, rasterized=True)
        ax.plot(times, s,    color=color, lw=1.5, label="Smoothed")
        ax.axhline(mean, color="0.4", lw=0.8, ls="--",
                   label=f"Mean = {mean:.2f} nm²")
        # shade activation windows only on hydrophobic panel (key finding)
        if "Hydrophobic" in ylabel:
            add_activation_windows(ax, label=True)
            # annotate the largest spike
            idx_max = np.argmax(data)
            ax.annotate(f"{data[idx_max]:.1f} nm²\n@ {times[idx_max]:.0f} ns",
                        xy=(times[idx_max], data[idx_max]),
                        xytext=(times[idx_max] - max(times)*0.15, data[idx_max] - 5),
                        fontsize=6.5, arrowprops=dict(arrowstyle="-", lw=0.6),
                        ha="center")
        ax.set_ylabel(ylabel)
        ax.set_title(subtitle, fontsize=8, style="italic", pad=2)
        ax.legend(loc="upper right")

    for ax in axes[2:]:
        ax.set_xlabel("Time (ns)")

    fig.align_ylabels(axes)
    plt.tight_layout(h_pad=0.8, w_pad=0.8)
    savefig(fig, OUTPUT_PNG)
    print(f"[4/4] Saved -> {OUTPUT_PNG}")


if __name__ == "__main__":
    u = load_universe()
    times, total, hydrophob, hydrophil, calyx = analyze(u)
    print_summary(times, total, hydrophob, hydrophil, calyx)
    plot(times, total, hydrophob, hydrophil, calyx)
