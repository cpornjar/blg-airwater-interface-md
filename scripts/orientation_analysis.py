"""
orientation_analysis.py
========================
วิเคราะห์ Orientation ของ 1BEB โปรตีนใน Slab System โดยวัด:
  1. มุมระหว่าง Hydrophobic patch vector กับแกน Z
  2. มุมระหว่าง Principal axis ของโปรตีนกับแกน Z
  3. Z-position ของโปรตีน (เพื่อเปรียบเทียบกับมุม)
  4. Combined plot: Z-position vs Orientation angle

Requirements:
    pip install MDAnalysis matplotlib numpy

Usage:
    python orientation_analysis.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import MDAnalysis as mda
from MDAnalysis.transformations import unwrap
from plot_style import apply_style, COLORS, col_width, savefig, smooth_sg
apply_style()

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
TPR_FILE   = "md_1000ns.tpr"
XTC_FILE   = "traj_comp.xtc"
OUTPUT_PNG = "orientation_analysis.png"

# Calyx (hydrophobic patch) residues ของ 1BEB
CALYX_RESIDS = [39, 41, 56, 58, 92, 103, 105, 107, 125]

# Reference residues ฝั่งตรงข้าม (hydrophilic face)
# ใช้ residues บริเวณ loop ที่ exposed และ hydrophilic
HYDROPHIL_RESIDS = [1, 10, 20, 30, 60, 80, 120, 150, 160]

STRIDE = 1   # ทุก frame เพราะคำนวณเร็ว
# ─────────────────────────────────────────


def load_universe():
    print(f"[1/4] Loading: {XTC_FILE}")
    u = mda.Universe(TPR_FILE, XTC_FILE)
    # Unwrap trajectory เพื่อแก้ PBC
    protein_atoms = u.select_atoms("protein")
    u.trajectory.add_transformations(unwrap(protein_atoms))
    print(f"      {u.trajectory.n_frames} frames | "
          f"dt = {u.trajectory.dt:.1f} ps | "
          f"Total = {u.trajectory.totaltime/1000:.1f} ns")
    return u


def calc_angle_with_z(vector):
    """คำนวณมุม (องศา) ระหว่าง vector กับแกน Z"""
    z_axis = np.array([0.0, 0.0, 1.0])
    # normalize
    v = vector / (np.linalg.norm(vector) + 1e-10)
    cos_theta = np.clip(np.dot(v, z_axis), -1.0, 1.0)
    angle = np.degrees(np.arccos(cos_theta))
    # คืนค่าในช่วง 0-90 (symmetric)
    return min(angle, 180 - angle)


def calc_principal_axis(positions):
    """คำนวณ principal axis (eigenvector ที่ 1) ของกลุ่ม atoms"""
    com = np.mean(positions, axis=0)
    centered = positions - com
    inertia = np.dot(centered.T, centered)
    eigenvalues, eigenvectors = np.linalg.eigh(inertia)
    # eigenvector ที่ correspond กับ eigenvalue ใหญ่สุด = แกนยาวสุด
    principal = eigenvectors[:, np.argmax(eigenvalues)]
    return principal


def analyze(u):
    print("[2/4] Analyzing orientation ...")

    protein   = u.select_atoms("protein")
    calyx     = u.select_atoms(
        "protein and name CA and (" +
        " or ".join([f"resid {r}" for r in CALYX_RESIDS]) + ")"
    )
    hydrophil = u.select_atoms(
        "protein and name CA and (" +
        " or ".join([f"resid {r}" for r in HYDROPHIL_RESIDS]) + ")"
    )

    print(f"      Calyx atoms     : {len(calyx)}")
    print(f"      Hydrophil atoms : {len(hydrophil)}")

    times         = []
    z_protein     = []
    angle_hydrophob = []   # มุมของ hydrophobic patch vector กับ Z
    angle_principal = []   # มุมของ principal axis กับ Z

    for ts in u.trajectory[::STRIDE]:
        t_ns = ts.time / 1000.0

        # Z-position ของ protein CoM
        prot_com = protein.center_of_mass()

        # Vector จาก protein CoM → calyx CoM
        # (ชี้ไปทาง hydrophobic face)
        calyx_com = calyx.center_of_mass()
        hydrophob_vec = calyx_com - prot_com

        # Principal axis ของโปรตีนทั้งหมด
        principal = calc_principal_axis(protein.positions)

        times.append(t_ns)
        z_protein.append(prot_com[2] / 10.0)          # Å → nm
        angle_hydrophob.append(calc_angle_with_z(hydrophob_vec))
        angle_principal.append(calc_angle_with_z(principal))

    return (np.array(times),
            np.array(z_protein),
            np.array(angle_hydrophob),
            np.array(angle_principal))


def smooth(data, window=10):
    w = min(window, len(data))
    return np.convolve(data, np.ones(w)/w, mode='same')


def print_summary(times, z_prot, angle_hydrophob, angle_principal):
    print("\n-- Orientation Summary ------------------------------")
    print(f"  Protein Z range       : {z_prot.min():.2f} – {z_prot.max():.2f} nm")
    print(f"  Hydrophob angle mean  : {np.mean(angle_hydrophob):.1f} +/- {np.std(angle_hydrophob):.1f} deg")
    print(f"  Principal angle mean  : {np.mean(angle_principal):.1f} +/- {np.std(angle_principal):.1f} deg")
    print(f"")
    print(f"  Interpretation:")
    print(f"  Hydrophob angle ~ 0  deg → patch pointing UP   (toward vacuum)")
    print(f"  Hydrophob angle ~ 90 deg → patch pointing SIDE (parallel to interface)")
    print(f"  Hydrophob angle ~ 90 deg can mean random tumbling in bulk")
    print("-----------------------------------------------------\n")


def plot(times, z_prot, angle_hydrophob, angle_principal):
    print("[3/4] Plotting ...")

    fig, axes = plt.subplots(2, 1, figsize=(col_width * 2, 4.5), sharex=True)

    # ── Panel 1: Hydrophobic patch angle ─────────────────
    ax1 = axes[0]
    ax1.plot(times, angle_hydrophob, color=COLORS["hydrophob"],
             lw=0.5, alpha=0.25, rasterized=True)
    ax1.plot(times, smooth_sg(angle_hydrophob), color=COLORS["hydrophob"],
             lw=1.5, label="Smoothed")
    ax1.axhline(np.mean(angle_hydrophob), color="0.4", lw=0.8, ls="--",
                label=f"Mean = {np.mean(angle_hydrophob):.1f}°")
    ax1.axhline(45, color=COLORS["patch"], lw=0.8, ls=":",
                alpha=0.7, label="45° (isotropic)")
    ax1.set_ylabel("Patch angle (°)")
    ax1.set_ylim(0, 90)
    ax1.set_yticks([0, 30, 45, 60, 90])
    ax1.set_title("Hydrophobic patch vector vs Z-axis  "
                  "(0° = toward interface, 90° = sideways)", fontsize=8)
    ax1.legend(loc="upper right")

    # ── Panel 2: Principal axis angle ────────────────────
    ax2 = axes[1]
    ax2.plot(times, angle_principal, color=COLORS["z_protein"],
             lw=0.5, alpha=0.25, rasterized=True)
    ax2.plot(times, smooth_sg(angle_principal), color=COLORS["z_protein"],
             lw=1.5, label="Smoothed")
    ax2.axhline(np.mean(angle_principal), color="0.4", lw=0.8, ls="--",
                label=f"Mean = {np.mean(angle_principal):.1f}°")
    ax2.axhline(45, color=COLORS["patch"], lw=0.8, ls=":",
                alpha=0.7, label="45° (isotropic)")
    ax2.set_ylabel("Principal axis angle (°)")
    ax2.set_xlabel("Time (ns)")
    ax2.set_ylim(0, 90)
    ax2.set_yticks([0, 30, 45, 60, 90])
    ax2.set_title("Principal axis vs Z-axis  "
                  "(0° = vertical, 90° = horizontal)", fontsize=8)
    ax2.legend(loc="upper right")

    fig.align_ylabels(axes)
    plt.tight_layout(h_pad=0.5)
    savefig(fig, OUTPUT_PNG)
    print(f"[4/4] Saved -> {OUTPUT_PNG}")


if __name__ == "__main__":
    u = load_universe()
    times, z_prot, angle_hydrophob, angle_principal = analyze(u)
    print_summary(times, z_prot, angle_hydrophob, angle_principal)
    plot(times, z_prot, angle_hydrophob, angle_principal)
