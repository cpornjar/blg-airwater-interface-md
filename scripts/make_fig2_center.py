"""
make_fig2_center.py
====================
Paper Fig 2 — CENTER 1000 ns two-panel:
  (a) Z-position + minimum protein-interface distance
  (b) Hydrophobic SASA with activation windows annotated

Data: SET 1A (CENTER), 1000 ns, traj_comp.xtc
Output: results/figures/PAPER_FIG2_CENTER.png

Usage:
    source ~/research-env/bin/activate
    python scripts/make_fig2_center.py
"""

import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import MDAnalysis as mda
from MDAnalysis.transformations import unwrap
import freesasa

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from plot_style import apply_style, COLORS as PC, double_width, savefig
apply_style()

TPR  = ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr"
XTC  = ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"
OUT  = ROOT / "results/figures/PAPER_FIG2_CENTER.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

STRIDE = 5
HYDROPHOBIC_RESNAMES = ["ALA","VAL","ILE","LEU","PRO","PHE","MET","TRP"]
RADIUS_MAP = {"C":1.70,"N":1.55,"O":1.52,"S":1.80,"H":1.20,"P":1.80}

# Activation windows from CENTER analysis (NARRATIVE_REPORT)
ACTIVATION_WINDOWS = [(254, 264, 39.3),     # t=259 ns burst
                      (754, 784, 39.3),     # t=759-779 ns window
                      (935, 950, 42.7)]     # t=940 ns largest


def calc_hydrophobic_sasa(protein):
    coords = protein.positions
    radii  = [RADIUS_MAP.get(a.name[0].upper(), 1.70) for a in protein.atoms]
    res    = freesasa.calcCoord(coords.flatten().tolist(), radii)
    sasa   = np.array([res.atomArea(i) for i in range(len(protein.atoms))])
    mask   = np.array([a.resname in HYDROPHOBIC_RESNAMES for a in protein.atoms])
    return float(sasa[mask].sum()) / 100.0   # A^2 -> nm^2


def upper_interface_z_nm(water_z_nm):
    """Upper interface = 99th percentile of upper-half water O Z positions."""
    mid = np.median(water_z_nm)
    upper = water_z_nm[water_z_nm > mid]
    return np.percentile(upper, 99)


print(f"Loading: {XTC}")
u = mda.Universe(str(TPR), str(XTC))
protein = u.select_atoms("protein")
u.trajectory.add_transformations(unwrap(protein))
water   = u.select_atoms("resname SOL and name OW")
print(f"  {u.trajectory.n_frames} frames | total {u.trajectory.totaltime/1000:.1f} ns")

print("Computing per-frame metrics...")
times, z_com, min_dist, hyd_sasa = [], [], [], []
for i, ts in enumerate(u.trajectory[::STRIDE]):
    t_ns = ts.time / 1000.0
    com_z = protein.center_of_mass()[2] / 10           # A -> nm
    min_pz = protein.positions[:, 2].min() / 10
    iface = upper_interface_z_nm(water.positions[:, 2] / 10)
    dist = iface - min_pz                              # positive: protein below interface
    s = calc_hydrophobic_sasa(protein)
    times.append(t_ns); z_com.append(com_z)
    min_dist.append(dist); hyd_sasa.append(s)
    if (i+1) % 100 == 0:
        print(f"  frame {i+1} | t={t_ns:.0f} ns | z={com_z:.2f} nm | dist={dist:.2f} nm | SASA={s:.1f} nm^2")

times    = np.array(times)
z_com    = np.array(z_com)
min_dist = np.array(min_dist)
hyd_sasa = np.array(hyd_sasa)

# ── Build figure ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(double_width, 5.6), sharex=True,
                         gridspec_kw={"hspace": 0.10, "top": 0.96, "bottom": 0.10})

# Panel (a) — Z-position and interface distance
ax = axes[0]
ax_r = ax.twinx()
ax.plot(times, z_com, color="#2E86AB", lw=1.2, label="Protein CoM Z")
ax.set_ylabel("Protein CoM Z (nm)", color=PC["interface"])
ax.tick_params(axis="y", labelcolor=PC["interface"])

ax_r.plot(times, min_dist, color=PC["distance"], lw=1.0, alpha=0.85,
          label="Min dist to upper interface")
ax_r.axhline(0.5, color="0.35", lw=0.9, ls="--", alpha=0.7,
             label="Adsorption threshold (0.5 nm)")
ax_r.set_ylabel("Min distance to interface (nm)", color=PC["distance"])
ax_r.tick_params(axis="y", labelcolor=PC["distance"])

# annotate closest approach — offset inward
i_min = int(np.argmin(min_dist))
x_off = -90 if times[i_min] > 800 else 80
ax_r.annotate(f"min {min_dist[i_min]:.2f} nm\n@ {times[i_min]:.0f} ns",
              xy=(times[i_min], min_dist[i_min]),
              xytext=(times[i_min] + x_off, min_dist[i_min] + 0.4),
              fontsize=7.5, color="#7B241C",
              arrowprops=dict(arrowstyle="->", color="#7B241C", lw=0.8))

ax.set_title("(a)  Spontaneous bulk-to-interface approach — CENTER 1000 ns",
             fontweight="bold", loc="left")

# Combined legend — two columns to stay compact
l1, lab1 = ax.get_legend_handles_labels()
l2, lab2 = ax_r.get_legend_handles_labels()
ax.legend(l1+l2, lab1+lab2, fontsize=7.5, loc="upper right",
          ncol=2, framealpha=0.90, handlelength=1.5)

# Panel (b) — Hydrophobic SASA with activation windows
ax = axes[1]
mean_s = hyd_sasa.mean()
std_s  = hyd_sasa.std()

for (t0, t1, s_max) in ACTIVATION_WINDOWS:
    ax.axvspan(t0, t1, color="#FDECEA", alpha=0.7, zorder=0)

ax.fill_between(times, hyd_sasa, alpha=0.25, color="#E74C3C")
ax.plot(times, hyd_sasa, color="#E74C3C", lw=1.0)
ax.axhline(mean_s, color="#444", lw=1, ls="--", alpha=0.7,
           label=f"Mean = {mean_s:.2f} ± {std_s:.2f} nm²")

# annotate activation windows
for (t0, t1, s_max) in ACTIVATION_WINDOWS:
    tc = (t0 + t1) / 2
    ax.annotate(f"{s_max:.1f} nm²", xy=(tc, s_max+1),
                xytext=(tc, s_max + 6), ha="center",
                fontsize=8.5, color="#7B241C",
                arrowprops=dict(arrowstyle="-", color="#7B241C", lw=0.7))

ax.set_ylabel("Hydrophobic SASA (nm²)")
ax.set_xlabel("Time (ns)")
ax.set_title("(b)  Hydrophobic surface activation — three pre-adsorption windows",
             fontweight="bold", loc="left")
ax.legend(fontsize=7.5, loc="upper left", framealpha=0.90)
ax.set_ylim(bottom=0)

savefig(fig, OUT)
print(f"\nSaved -> {OUT}")
print(f"  CoM Z range: {z_com.min():.2f} - {z_com.max():.2f} nm")
print(f"  Min dist range: {min_dist.min():.2f} - {min_dist.max():.2f} nm  (min at t={times[i_min]:.0f} ns)")
print(f"  Hydrophobic SASA: mean {mean_s:.2f} ± {std_s:.2f} nm² ; max {hyd_sasa.max():.2f} nm²")
