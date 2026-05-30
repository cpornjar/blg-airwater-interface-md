"""
advanced_analysis.py
=====================
Advanced analysis for 1BEB 1,000 ns trajectory
Focuses on:
  1. Per-residue RMSF  — identify flexible regions
  2. Radius of Gyration (Rg) — measure protein compactness
  3. RMSD + Z-position overlay — correlate unfolding with diffusion
  4. RMSD vs Rg scatter — conformational space exploration
  5. Z-position distribution — compare early/mid/late trajectory

Requirements:
    pip install MDAnalysis matplotlib numpy scipy

Usage:
    python advanced_analysis.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from MDAnalysis.transformations import unwrap
from plot_style import (apply_style, COLORS, col_width, double_width,
                        ACTIVATION_WINDOWS, add_activation_windows, savefig, smooth_sg)
apply_style()

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
TPR_FILE   = "md_1000ns.tpr"
XTC_FILE   = "traj_comp.xtc"
OUTPUT_PNG = "advanced_analysis.png"

STRIDE = 5   # analyze every 5 frames

# Time window of interest (ns)
EVENT_START = 600   # partial unfolding event
EVENT_END   = 800

# Secondary structure residue ranges (1BEB standard)
BETA_REGIONS = [(2,8),(16,21),(29,35),(46,52),
                (62,67),(75,82),(92,98),(106,113),(138,145)]
HELIX_REGION = (130, 137)
# ─────────────────────────────────────────


def load_universe():
    print(f"[1/6] Loading: {XTC_FILE}")
    u = mda.Universe(TPR_FILE, XTC_FILE)
    protein = u.select_atoms("protein")
    u.trajectory.add_transformations(unwrap(protein))
    print(f"      {u.trajectory.n_frames} frames | "
          f"Total = {u.trajectory.totaltime/1000:.1f} ns")
    return u


def calc_rmsf(u):
    """Per-residue RMSF to identify flexible regions"""
    print("[2/6] Computing per-residue RMSF ...")

    # Align trajectory before fixing PBC artifact
    from MDAnalysis.analysis import align
    align.AlignTraj(u, u,
                    select="backbone",
                    in_memory=True).run()

    ca_atoms = u.select_atoms("protein and name CA")
    R = rms.RMSF(ca_atoms)
    R.run(step=STRIDE)
    resids  = ca_atoms.resids
    rmsf_nm = R.results.rmsf / 10.0
    return resids, rmsf_nm


def calc_rg(u):
    """Radius of Gyration over entire trajectory"""
    print("[3/6] Computing Radius of Gyration ...")
    protein = u.select_atoms("protein")
    times, rg = [], []
    for ts in u.trajectory[::STRIDE]:
        times.append(ts.time / 1000.0)
        rg.append(protein.radius_of_gyration() / 10.0)   # Angstrom -> nm
    return np.array(times), np.array(rg)


def calc_z_and_rmsd(u):
    """Backbone RMSD and protein CoM Z-position over trajectory"""
    print("[4/6] Computing RMSD and Z-position ...")
    ref = mda.Universe(TPR_FILE, XTC_FILE)
    R = rms.RMSD(u, ref, select="backbone", ref_frame=0)
    R.run(step=STRIDE)

    times   = R.results.rmsd[:, 1] / 1000.0   # ps -> ns
    rmsd_nm = R.results.rmsd[:, 2] / 10.0     # Angstrom -> nm

    protein = u.select_atoms("protein")
    z_pos = []
    frames = list(range(0, u.trajectory.n_frames, STRIDE))
    for frame_idx in frames:
        u.trajectory[frame_idx]
        z_pos.append(protein.center_of_mass()[2] / 10.0)

    return times, rmsd_nm, np.array(z_pos)


def smooth(data, window=21):
    return smooth_sg(data, window=window)


def print_summary(resids, rmsf, times, rg, rmsd, z_pos):
    threshold = np.mean(rmsf) + 2*np.std(rmsf)
    flexible  = resids[rmsf > threshold]

    print("\n-- Advanced Analysis Summary ----------------------")
    print(f"  RMSF mean +/- std   : {np.mean(rmsf):.3f} +/- {np.std(rmsf):.3f} nm")
    print(f"  Highly flexible res : {list(flexible)}")
    print(f"  Rg mean +/- std     : {np.mean(rg):.3f} +/- {np.std(rg):.3f} nm")
    print(f"  Rg range            : {rg.min():.3f} - {rg.max():.3f} nm")
    print(f"  RMSD mean           : {np.mean(rmsd):.3f} nm")
    print(f"  RMSD max            : {rmsd.max():.3f} nm at t = {times[rmsd.argmax()]:.1f} ns")

    mask_event = (times >= EVENT_START) & (times <= EVENT_END)
    if mask_event.sum() > 0:
        print(f"\n  Unfolding event ({EVENT_START}-{EVENT_END} ns):")
        print(f"    RMSD mean : {np.mean(rmsd[mask_event]):.3f} nm")
        print(f"    Rg mean   : {np.mean(rg[mask_event]):.3f} nm")
        print(f"    Z-pos mean: {np.mean(z_pos[mask_event]):.3f} nm")
    print("---------------------------------------------------\n")


def plot(resids, rmsf, times, rg, rmsd, z_pos):
    print("[5/6] Plotting ...")

    fig = plt.figure(figsize=(double_width, 8.5))
    gs  = GridSpec(3, 2, figure=fig, hspace=0.55, wspace=0.38)

    # ── Panel 1: Per-residue RMSF (full width) ───────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.bar(resids, rmsf, color=COLORS["backbone"], alpha=0.75, width=1.0)
    mean_rmsf = np.mean(rmsf)
    thresh    = mean_rmsf + 2 * np.std(rmsf)
    ax1.axhline(mean_rmsf, color="0.4", lw=0.8, ls="--",
                label=f"Mean = {mean_rmsf:.3f} nm")
    ax1.axhline(thresh, color=COLORS["helix"], lw=0.8, ls=":",
                label=f"Mean + 2σ = {thresh:.3f} nm")
    for i, (s, e) in enumerate(BETA_REGIONS):
        ax1.axvspan(s, e, alpha=0.10, color=COLORS["beta"],
                    label="β-sheet regions" if i == 0 else "")
    ax1.axvspan(*HELIX_REGION, alpha=0.12, color=COLORS["helix"],
                label="α-helix (130–142)")
    # Annotate Loop BC
    ax1.annotate("Loop BC\n(res. 30–35)", xy=(32, rmsf[resids == 32].mean() if 32 in resids else thresh),
                 xytext=(55, thresh * 1.05), fontsize=7,
                 arrowprops=dict(arrowstyle="-", lw=0.6), ha="center")
    ax1.set_xlabel("Residue number")
    ax1.set_ylabel("RMSF (nm)")
    ax1.legend(loc="upper right", ncol=2)

    # ── Panel 2: Radius of Gyration ──────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(times, rg, color=COLORS["rg"], lw=0.5, alpha=0.25, rasterized=True)
    ax2.plot(times, smooth(rg), color=COLORS["rg"], lw=1.5)
    ax2.axhline(np.mean(rg), color="0.4", lw=0.8, ls="--",
                label=f"Mean = {np.mean(rg):.3f} nm")
    add_activation_windows(ax2)
    ax2.set_xlabel("Time (ns)")
    ax2.set_ylabel("R$_g$ (nm)")
    ax2.legend(loc="upper right")

    # ── Panel 3: RMSD + Z-position overlay ───────────────
    ax3  = fig.add_subplot(gs[1, 1])
    ax3b = ax3.twinx()
    ax3.plot(times, smooth(rmsd), color=COLORS["backbone"], lw=1.5, label="RMSD")
    ax3b.plot(times, smooth(z_pos), color=COLORS["z_protein"],
              lw=1.5, alpha=0.8, label="Z-pos")
    add_activation_windows(ax3)
    ax3.set_xlabel("Time (ns)")
    ax3.set_ylabel("RMSD (nm)", color=COLORS["backbone"])
    ax3b.set_ylabel("Z-position (nm)", color=COLORS["z_protein"])
    lines1, labels1 = ax3.get_legend_handles_labels()
    lines2, labels2 = ax3b.get_legend_handles_labels()
    ax3.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    # ── Panel 4: RMSD vs Rg conformational scatter ───────
    ax4  = fig.add_subplot(gs[2, 0])
    step = max(1, len(times) // 800)
    sc   = ax4.scatter(rmsd[::step], rg[::step],
                       c=times[::step], cmap="viridis",
                       s=4, alpha=0.7, linewidths=0, rasterized=True)
    cb   = plt.colorbar(sc, ax=ax4, pad=0.02)
    cb.set_label("Time (ns)", fontsize=8)
    ax4.set_xlabel("RMSD (nm)")
    ax4.set_ylabel("R$_g$ (nm)")
    ax4.set_title("Conformational space  (dark = early, bright = late)",
                  fontsize=7.5)

    # ── Panel 5: Z-position distribution by epoch ────────
    ax5 = fig.add_subplot(gs[2, 1])
    epochs = [
        (times < 300,              COLORS["replica1"], "0–300 ns"),
        ((times >= 300) & (times < 700), COLORS["replica2"], "300–700 ns"),
        (times >= 700,             COLORS["replica3"], "700–1000 ns"),
    ]
    for mask, color, lbl in epochs:
        if mask.sum() > 0:
            ax5.hist(z_pos[mask], bins=25, alpha=0.5, color=color,
                     label=lbl, density=True)
    ax5.set_xlabel("Z-position (nm)")
    ax5.set_ylabel("Probability density")
    ax5.set_title("Z-position distribution by epoch", fontsize=7.5)
    ax5.legend()

    savefig(fig, OUTPUT_PNG)
    print(f"[6/6] Saved -> {OUTPUT_PNG}")


if __name__ == "__main__":
    # Universe สำหรับ RMSF (aligned)
    u_rmsf = mda.Universe(TPR_FILE, XTC_FILE)
    u_rmsf.trajectory.add_transformations(
        unwrap(u_rmsf.select_atoms("protein")))
    resids, rmsf = calc_rmsf(u_rmsf)

    # Universe ใหม่สำหรับ Rg และ Z-position (ไม่ align)
    u_raw = mda.Universe(TPR_FILE, XTC_FILE)
    u_raw.trajectory.add_transformations(
        unwrap(u_raw.select_atoms("protein")))
    times, rg          = calc_rg(u_raw)
    times, rmsd, z_pos = calc_z_and_rmsd(u_raw)

    print_summary(resids, rmsf, times, rg, rmsd, z_pos)
    plot(resids, rmsf, times, rg, rmsd, z_pos)
