"""
detect_adsorption_1d.py
========================
Analysis script for SET 1D above-water simulations.
Detects adsorption events, measures timing, identifies first-contact residues,
and compares 1Da (patch-down) vs 1Db (patch-up control).

Tests the two-factor gating mechanism:
  1Da: patch toward interface → expect fast adsorption
  1Db: patch away from interface → expect slow/no adsorption

Usage (from MILK_FROTHING root):
    source ~/research-env/bin/activate
    python scripts/detect_adsorption_1d.py
    python scripts/detect_adsorption_1d.py --variant 1Da   # single variant
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import MDAnalysis as mda
from MDAnalysis.analysis import distances

ROOT    = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from plot_style import apply_style, COLORS, col_width, savefig, smooth_sg
    apply_style()
except ImportError:
    pass

# ── Config ────────────────────────────────────────────────────────────────────
VARIANTS = {
    "1Da": {
        "tpr": ROOT / "outputs_BLG/SET1D/set1d_1Da_start.gro",
        "xtc": ROOT / "outputs_BLG/SET1D/1Da/md_1Da.xtc",
        "label": "SET1D-a (patch DOWN → interface)",
        "color": "#E74C3C",
        "expected": "fast adsorption",
    },
    "1Db": {
        "tpr": ROOT / "outputs_BLG/SET1D/set1d_1Db_start.gro",
        "xtc": ROOT / "outputs_BLG/SET1D/1Db/md_1Db.xtc",
        "label": "SET1D-b (patch UP, control)",
        "color": "#2E86AB",
        "expected": "slow/no adsorption",
    },
}

ADSORPTION_DIST_NM   = 0.5    # threshold: protein within 0.5 nm of interface
ADSORPTION_PERSIST_NS = 10.0  # must stay adsorbed for this long
CALYX_RESIDS = [39, 41, 56, 58, 92, 103, 105, 107, 125]   # hydrophobic patch

FIG_DIR = ROOT / "results" / "figures" / "set1d"
FIG_DIR.mkdir(parents=True, exist_ok=True)


def load(tpr, xtc):
    print(f"  Loading: {xtc.name}")
    if not xtc.exists():
        print(f"  [SKIP] XTC not yet available: {xtc}")
        return None
    u = mda.Universe(str(tpr), str(xtc))
    print(f"  {u.trajectory.n_frames} frames | dt={u.trajectory.dt:.1f} ps | "
          f"total={u.trajectory.totaltime/1000:.1f} ns")
    return u


def get_upper_interface_z(u):
    """99th percentile Z of water oxygens = upper interface."""
    water = u.select_atoms("resname SOL and name OW")
    zs = []
    for ts in u.trajectory[::50]:   # stride for speed
        zs.extend(water.positions[:, 2] / 10)
    return np.percentile(zs, 99)


def analyze_variant(key, cfg):
    print(f"\n{'='*55}")
    print(f"  {cfg['label']}")
    print(f"{'='*55}")

    u = load(cfg["tpr"], cfg["xtc"])
    if u is None:
        return None

    protein = u.select_atoms("protein")
    calyx   = protein.select_atoms(
        "(" + " or ".join([f"resid {r}" for r in CALYX_RESIDS]) + ")"
    )
    water   = u.select_atoms("resname SOL and name OW")

    upper_iface_nm = get_upper_interface_z(u)
    print(f"  Upper interface Z : {upper_iface_nm:.3f} nm")

    times, z_prot, dist_to_iface, calyx_angle = [], [], [], []

    for ts in u.trajectory:
        t_ns = ts.time / 1000.0
        prot_com_z   = protein.center_of_mass()[2] / 10
        # distance from lowest protein atom to interface
        min_prot_z   = protein.positions[:, 2].min() / 10
        dist         = min_prot_z - upper_iface_nm   # positive = above, negative = penetrated

        # calyx vector angle with -Z (toward water)
        calyx_com    = calyx.center_of_mass()
        prot_com     = protein.center_of_mass()
        vec          = (calyx_com - prot_com)
        vec_norm     = vec / np.linalg.norm(vec)
        angle        = np.degrees(np.arccos(np.clip(-vec_norm[2], -1, 1)))

        times.append(t_ns)
        z_prot.append(prot_com_z)
        dist_to_iface.append(dist)
        calyx_angle.append(angle)

    times        = np.array(times)
    dist_to_iface = np.array(dist_to_iface)
    calyx_angle  = np.array(calyx_angle)

    # ── Adsorption detection ──────────────────────────────────────────────────
    adsorbed_mask = dist_to_iface <= ADSORPTION_DIST_NM
    adsorption_time_ns = None
    persist_frames = int(ADSORPTION_PERSIST_NS / (u.trajectory.dt / 1000))

    for i in range(len(times) - persist_frames):
        if adsorbed_mask[i:i + persist_frames].all():
            adsorption_time_ns = times[i]
            break

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n  ── Adsorption Analysis ──────────────────────────────")
    print(f"  Min dist to interface : {dist_to_iface.min():.3f} nm  "
          f"(at t = {times[np.argmin(dist_to_iface)]:.1f} ns)")
    if adsorption_time_ns is not None:
        print(f"  ✓ ADSORBED at t = {adsorption_time_ns:.1f} ns  "
              f"(stayed ≤ {ADSORPTION_DIST_NM} nm for ≥ {ADSORPTION_PERSIST_NS} ns)")
    else:
        print(f"  ✗ Not adsorbed in {times[-1]:.1f} ns trajectory")
        print(f"    (expected: {cfg['expected']})")
    print(f"  Calyx angle mean : {np.mean(calyx_angle):.1f} ± {np.std(calyx_angle):.1f}°")
    print(f"    (0° = patch pointing toward water interface)")
    print(f"  ─────────────────────────────────────────────────────")

    return {
        "key": key,
        "label": cfg["label"],
        "color": cfg["color"],
        "times": times,
        "dist": dist_to_iface,
        "calyx_angle": calyx_angle,
        "adsorption_time": adsorption_time_ns,
        "min_dist": dist_to_iface.min(),
        "min_dist_t": times[np.argmin(dist_to_iface)],
        "upper_iface": upper_iface_nm,
    }


def plot_comparison(results):
    valid = [r for r in results if r is not None]
    if not valid:
        print("No data to plot.")
        return

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=False)
    fig.suptitle("SET 1D — Two-Factor Gating Mechanism Test\n"
                 "Above-water BLG: patch-down (1Da) vs patch-up control (1Db)",
                 fontsize=13, fontweight="bold")

    for r in valid:
        axes[0].plot(r["times"], r["dist"], color=r["color"],
                     lw=1.2, alpha=0.8, label=r["label"])
        axes[1].plot(r["times"], r["calyx_angle"], color=r["color"],
                     lw=1.2, alpha=0.8, label=r["label"])
        if r["adsorption_time"] is not None:
            axes[0].axvline(r["adsorption_time"], color=r["color"],
                            lw=1.5, ls="--", alpha=0.7,
                            label=f"Adsorbed @ {r['adsorption_time']:.0f} ns")

    axes[0].axhline(ADSORPTION_DIST_NM, color="0.4", lw=1, ls=":",
                    label=f"Adsorption threshold ({ADSORPTION_DIST_NM} nm)")
    axes[0].axhline(0, color="0.6", lw=0.8, ls="-", alpha=0.5)
    axes[0].set_ylabel("Min dist to interface (nm)", fontsize=11)
    axes[0].set_title("Distance to Air-Water Interface", fontsize=11)
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)

    axes[1].axhline(90, color="0.5", lw=0.8, ls="--", alpha=0.5,
                    label="90° = patch parallel to interface")
    axes[1].axhline(0, color="#E74C3C", lw=0.8, ls="--", alpha=0.5,
                    label="0° = patch pointing toward water")
    axes[1].set_ylabel("Calyx patch angle to -Z (°)", fontsize=11)
    axes[1].set_xlabel("Time (ns)", fontsize=11)
    axes[1].set_title("Hydrophobic Patch Orientation", fontsize=11)
    axes[1].set_ylim(0, 180)
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    out = FIG_DIR / "SET1D_comparison.png"
    fig.savefig(str(out), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nComparison figure saved → {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=["1Da", "1Db"],
                        help="Analyze single variant only")
    args = parser.parse_args()

    keys = [args.variant] if args.variant else list(VARIANTS.keys())
    results = []
    for k in keys:
        r = analyze_variant(k, VARIANTS[k])
        results.append(r)

    if len(results) == 2:
        plot_comparison(results)

    # Print two-factor gating conclusion
    print("\n── Two-Factor Gating Summary ────────────────────────────────")
    for r in results:
        if r is None:
            continue
        status = f"ADSORBED @ {r['adsorption_time']:.0f} ns" if r["adsorption_time"] \
                 else f"NOT adsorbed ({r['times'][-1]:.0f} ns trajectory)"
        print(f"  {r['key']}: {status} | min dist = {r['min_dist']:.3f} nm")
    print("─────────────────────────────────────────────────────────────")


if __name__ == "__main__":
    main()
