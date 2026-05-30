"""
rmsd_analysis.py
=================
วิเคราะห์ RMSD ของ 1BEB โปรตีนใน 4 ส่วน:
  1. Backbone ทั้งโปรตีน (ภาพรวม)
  2. Beta-sheet รวม
  3. Alpha-helix หลัก
  4. Hydrophobic patch (Calyx region)

Requirements:
    pip install MDAnalysis matplotlib numpy

Usage:
    python rmsd_analysis.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from plot_style import apply_style, COLORS, double_width, savefig, smooth_sg
apply_style()

# ─────────────────────────────────────────
#  CONFIG  ← ปรับตรงนี้
# ─────────────────────────────────────────
TPR_FILE   = "md_1000ns.tpr"
XTC_FILE   = "traj_comp.xtc"
OUTPUT_PNG = "rmsd_analysis.png"

# Residue numbers ของ 1BEB (standard)
# ปรับได้ถ้า numbering ในไฟล์ของคุณต่างออกไป
BETA_SHEET_RES = (
    "resid 2:8 or resid 16:21 or resid 29:35 or resid 46:52 or "
    "resid 62:67 or resid 75:82 or resid 92:98 or resid 106:113 or "
    "resid 138:145"
)
HELIX_RES      = "resid 130:137"
HYDROPHOBIC_RES = "resid 39 or resid 41 or resid 56 or resid 58 or resid 92 or resid 103 or resid 105 or resid 107 or resid 125"

STRIDE = 1   # อ่านทุก frame (เพิ่มเป็น 5 หรือ 10 ถ้าช้า)
# ─────────────────────────────────────────


def load_universe():
    print(f"[1/4] Loading: {XTC_FILE}")
    u = mda.Universe(TPR_FILE, XTC_FILE)
    print(f"      {u.trajectory.n_frames} frames | "
          f"dt = {u.trajectory.dt:.1f} ps | "
          f"Total = {u.trajectory.totaltime/1000:.1f} ns")
    return u


def run_rmsd(u, selection, label):
    """คำนวณ RMSD ของ selection โดย align backbone ทั้งโปรตีนก่อน"""
    print(f"    → Computing RMSD: {label}")

    # Reference = frame แรก
    ref = mda.Universe(TPR_FILE, XTC_FILE)

    R = rms.RMSD(
        u,
        ref,
        select="backbone",           # align โดยใช้ backbone ทั้งโปรตีน
        groupselections=[selection],  # วัด RMSD ของ selection นี้
        ref_frame=0
    )
    R.run(step=STRIDE)

    times = R.results.rmsd[:, 1] / 1000.0   # ps → ns
    rmsd  = R.results.rmsd[:, 3] / 10.0     # Å → nm
    return times, rmsd


def analyze(u):
    print("[2/4] Running RMSD calculations ...")

    from MDAnalysis.transformations import unwrap
    u.trajectory.add_transformations(unwrap(u.select_atoms("protein")))

    selections = {
        "Backbone (ทั้งโปรตีน)" : "backbone",
        "Beta-sheet"             : f"backbone and ({BETA_SHEET_RES})",
        "Alpha-helix"            : f"backbone and ({HELIX_RES})",
        "Hydrophobic patch"      : f"name CA and ({HYDROPHOBIC_RES})",
    }

    results = {}
    for label, sel in selections.items():
        t, r = run_rmsd(u, sel, label)
        results[label] = (t, r)

    return results


def plot(results):
    print("[3/4] Plotting ...")

    color_map = {
        "Backbone (ทั้งโปรตีน)" : COLORS["backbone"],
        "Beta-sheet"             : COLORS["beta"],
        "Alpha-helix"            : COLORS["helix"],
        "Hydrophobic patch"      : COLORS["patch"],
    }
    label_map = {
        "Backbone (ทั้งโปรตีน)" : "Backbone",
        "Beta-sheet"             : "Beta-sheet (strands A–H)",
        "Alpha-helix"            : "Alpha-helix (res. 130–142)",
        "Hydrophobic patch"      : "Hydrophobic patch (calyx)",
    }

    fig, axes = plt.subplots(2, 2, figsize=(double_width, 5.0), sharex=True)
    axes = axes.flatten()

    for ax, (label, (times, rmsd)) in zip(axes, results.items()):
        color = color_map[label]
        s     = smooth_sg(rmsd)
        mean  = np.mean(rmsd)

        ax.plot(times, rmsd, color=color, lw=0.5, alpha=0.25, rasterized=True)
        ax.plot(times, s,    color=color, lw=1.5, label="Smoothed")
        ax.axhline(mean, color="0.4", lw=0.8, ls="--",
                   label=f"Mean = {mean:.3f} nm")

        ax.set_title(label_map[label], fontsize=8)
        ax.set_ylabel("RMSD (nm)")
        ax.legend(loc="upper left")

    for ax in axes[2:]:
        ax.set_xlabel("Time (ns)")

    fig.align_ylabels(axes)
    plt.tight_layout(h_pad=0.8, w_pad=0.8)
    savefig(fig, OUTPUT_PNG)
    print(f"[4/4] Saved → {OUTPUT_PNG}")


def print_summary(results):
    print("\n── RMSD Summary ─────────────────────────────────")
    for label, (times, rmsd) in results.items():
        print(f"  {label:<30} "
              f"Mean = {np.mean(rmsd):.3f} nm | "
              f"Max = {np.max(rmsd):.3f} nm | "
              f"Std = {np.std(rmsd):.3f} nm")
    print("──────────────────────────────────────────────────\n")


if __name__ == "__main__":
    u = load_universe()
    results = analyze(u)
    print_summary(results)
    plot(results)
