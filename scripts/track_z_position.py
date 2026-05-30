"""
track_z_position.py
====================
ติดตาม Z-position ของ Protein Center of Mass และ Water Slab
จาก GROMACS trajectory ของระบบ Air-Water Interface (1BEB)

Requirements:
    pip install MDAnalysis matplotlib numpy

Usage:
    python track_z_position.py

ปรับ CONFIG ด้านล่างให้ตรงกับไฟล์ของคุณก่อนรัน
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import MDAnalysis as mda
from MDAnalysis.analysis import distances
from plot_style import apply_style, COLORS, col_width, add_adsorption_line, savefig, smooth_sg
apply_style()

# ─────────────────────────────────────────
#  CONFIG  ← ปรับตรงนี้
# ─────────────────────────────────────────
TPR_FILE   = "md_1000ns.tpr"       # หรือ .gro ก็ได้
XTC_FILE   = "traj_comp.xtc"       # trajectory file
OUTPUT_PNG = "z_position_track.png"

PROTEIN_SEL = "protein"             # MDAnalysis selection string
WATER_SEL   = "resname SOL"         # TIP3P ใช้ SOL

# ถ้าอยากดูเฉพาะช่วงเวลา (ns) — ตั้ง None เพื่อดูทั้งหมด
START_NS = None
END_NS   = None

# ความถี่ในการอ่าน frame (1 = ทุก frame, 10 = ทุก 10 frame)
STRIDE = 1
# ─────────────────────────────────────────


def load_universe():
    print(f"[1/4] Loading trajectory: {XTC_FILE}")
    u = mda.Universe(TPR_FILE, XTC_FILE)
    print(f"      {u.trajectory.n_frames} frames | "
          f"dt = {u.trajectory.dt:.1f} ps | "
          f"Total = {u.trajectory.totaltime/1000:.1f} ns")
    return u


def get_frame_range(u):
    dt_ns = u.trajectory.dt / 1000.0
    start = int(START_NS / dt_ns) if START_NS is not None else 0
    stop  = int(END_NS   / dt_ns) if END_NS   is not None else u.trajectory.n_frames
    return start, stop


def analyze(u):
    protein = u.select_atoms(PROTEIN_SEL)
    water   = u.select_atoms(WATER_SEL)

    start, stop = get_frame_range(u)

    times, z_protein, z_water_upper, z_water_lower = [], [], [], []

    print(f"[2/4] Analyzing frames {start}–{stop} (stride={STRIDE}) ...")

    for ts in u.trajectory[start:stop:STRIDE]:
        t_ns = ts.time / 1000.0

        # Protein Center of Mass Z
        prot_z = protein.center_of_mass()[2]

        # Water slab interface: ใช้ percentile ของ Z ของ water oxygen
        wat_z = water.select_atoms("name OH2 OW O").positions[:, 2]
        upper = np.percentile(wat_z, 98)   # upper interface
        lower = np.percentile(wat_z, 2)    # lower interface

        times.append(t_ns)
        z_protein.append(prot_z)
        z_water_upper.append(upper)
        z_water_lower.append(lower)

    return (np.array(times),
            np.array(z_protein),
            np.array(z_water_upper),
            np.array(z_water_lower))


def calc_distance_to_interface(z_protein, z_upper, z_lower):
    """ระยะห่างจากโปรตีนถึง interface ที่ใกล้กว่า (บวก = ยังอยู่ใน water)"""
    dist_upper = z_upper - z_protein
    dist_lower = z_protein - z_lower
    # ใกล้ interface ไหนมากกว่า
    closer = np.where(dist_upper < dist_lower, dist_upper, dist_lower)
    return closer / 10.0   # Å → nm


def plot(times, z_prot, z_upper, z_lower):
    print("[3/4] Plotting ...")

    z_prot_nm  = z_prot  / 10.0
    z_upper_nm = z_upper / 10.0
    z_lower_nm = z_lower / 10.0
    dist_nm    = calc_distance_to_interface(z_prot, z_upper, z_lower)

    fig, axes = plt.subplots(2, 1, figsize=(col_width * 2, 4.5), sharex=True)

    # ── Panel 1: Z-position ──────────────────────────────
    ax1 = axes[0]
    ax1.fill_between(times, z_upper_nm, z_lower_nm,
                     alpha=0.12, color=COLORS["interface"], label="Water slab")
    ax1.axhline(np.mean(z_upper_nm), color=COLORS["interface"],
                lw=0.7, ls="--", alpha=0.5)
    ax1.axhline(np.mean(z_lower_nm), color=COLORS["interface"],
                lw=0.7, ls="--", alpha=0.5, label="Mean interface")
    ax1.plot(times, z_prot_nm, color=COLORS["z_protein"], lw=1.0,
             alpha=0.4, rasterized=True)
    ax1.plot(times, smooth_sg(z_prot_nm), color=COLORS["z_protein"],
             lw=1.5, label="Protein CoM (Z)")
    ax1.set_ylabel("Z position (nm)")
    ax1.legend(loc="upper right")

    # ── Panel 2: Distance to nearest interface ───────────
    ax2 = axes[1]
    ax2.plot(times, dist_nm, color=COLORS["distance"], lw=1.0,
             alpha=0.35, rasterized=True)
    ax2.plot(times, smooth_sg(dist_nm), color=COLORS["distance"], lw=1.5)
    add_adsorption_line(ax2, horizontal=True)
    # Annotate minimum distance point
    idx_min = np.argmin(dist_nm)
    ax2.annotate(f"min {dist_nm[idx_min]:.2f} nm\n@ {times[idx_min]:.0f} ns",
                 xy=(times[idx_min], dist_nm[idx_min]),
                 xytext=(times[idx_min] + max(times)*0.05, dist_nm[idx_min] + 0.3),
                 fontsize=7, arrowprops=dict(arrowstyle="-", lw=0.7),
                 ha="left")
    ax2.set_xlabel("Time (ns)")
    ax2.set_ylabel("Distance to interface (nm)")
    ax2.legend(loc="upper right")

    fig.align_ylabels(axes)
    plt.tight_layout(h_pad=0.5)
    savefig(fig, OUTPUT_PNG)
    print(f"[4/4] Saved → {OUTPUT_PNG}")


def print_summary(times, z_prot, z_upper, z_lower):
    dist = calc_distance_to_interface(z_prot, z_upper, z_lower)
    print("\n── Summary ──────────────────────────────────────")
    print(f"  Simulation analyzed : {times[0]:.1f} – {times[-1]:.1f} ns")
    print(f"  Protein Z range     : {z_prot.min()/10:.2f} – {z_prot.max()/10:.2f} nm")
    print(f"  Min dist to interface: {dist.min():.3f} nm  (at t = {times[dist.argmin()]:.1f} ns)")
    print(f"  Adsorbed (dist ≤ 0) : {'YES' if dist.min() <= 0 else 'NOT YET'}")
    print("─────────────────────────────────────────────────\n")


if __name__ == "__main__":
    u = load_universe()
    times, z_prot, z_upper, z_lower = analyze(u)
    print_summary(times, z_prot, z_upper, z_lower)
    plot(times, z_prot, z_upper, z_lower)
