"""
detect_adsorption_contact.py
============================
Nearest-atom adsorption detector for slab MD trajectories.

Rationale
---------
Earlier z-position analysis tracked the *centre of mass* distance from protein
to the water/vacuum interface. For a ~4 nm globular protein, CoM at 1.3 nm
above the interface already means surface atoms are in van der Waals contact
with the interface. The CoM metric massively underestimates adsorption.

This script measures the minimum distance from ANY protein heavy atom to the
nearest air-water interface, frame by frame, and flags contact when that
distance drops below 0.3 nm.

Usage
-----
    python detect_adsorption_contact.py --tpr <file.tpr> --xtc <file.xtc> \\
                                        --label CENTER --out results/figures/

    # Two-part trajectory (e.g., R2: 0-500 ns + 500-1000 ns):
    python detect_adsorption_contact.py --tpr <ext.tpr> \\
        --xtc traj_comp.xtc md_replica2_ext.part0002.xtc \\
        --label R2 --out results/figures/adsorption/

Outputs
-------
    <label>_adsorption_contact.png   — two-panel time series
    <label>_adsorption_summary.txt   — first contact, fraction adsorbed, etc.
"""

import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import MDAnalysis as mda

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from plot_style import apply_style, COLORS, double_width, savefig, smooth_sg

apply_style()

CONTACT_THRESHOLD_NM = 0.30   # nearest-atom van der Waals contact
NEAR_THRESHOLD_NM    = 0.50   # secondary "approach" threshold
WATER_UPPER_PCT      = 98
WATER_LOWER_PCT      = 2


def analyse(tpr, xtc, stride=1):
    # xtc may be a single path or a list of paths (MDAnalysis handles both)
    u = mda.Universe(tpr, xtc) if isinstance(xtc, str) else mda.Universe(tpr, *xtc)
    protein = u.select_atoms("protein and not name H*")
    water_o = u.select_atoms("resname SOL and (name OH2 OW O)")

    n = u.trajectory.n_frames
    print(f"  Frames: {n} | dt = {u.trajectory.dt:.1f} ps "
          f"| total = {u.trajectory.totaltime/1000:.1f} ns | stride={stride}")

    times, min_dist, max_pz, min_pz, z_up, z_lo = [], [], [], [], [], []

    for ts in u.trajectory[::stride]:
        pz = protein.positions[:, 2]
        wz = water_o.positions[:, 2]
        zu = np.percentile(wz, WATER_UPPER_PCT)
        zl = np.percentile(wz, WATER_LOWER_PCT)

        # signed distance: positive while atom is inside the slab
        d_up = (zu - pz.max()) / 10.0   # closest atom to upper interface
        d_lo = (pz.min() - zl) / 10.0   # closest atom to lower interface

        times.append(ts.time / 1000.0)
        min_dist.append(min(d_up, d_lo))
        max_pz.append(pz.max() / 10.0)
        min_pz.append(pz.min() / 10.0)
        z_up.append(zu / 10.0)
        z_lo.append(zl / 10.0)

    return {
        "t":      np.array(times),
        "dmin":   np.array(min_dist),
        "pz_max": np.array(max_pz),
        "pz_min": np.array(min_pz),
        "z_up":   np.array(z_up),
        "z_lo":   np.array(z_lo),
    }


def detect_events(t, d, threshold=CONTACT_THRESHOLD_NM):
    """Return list of (start_ns, end_ns, min_dist_nm) for contiguous windows
    where d ≤ threshold."""
    below = d <= threshold
    if not below.any():
        return []
    edges = np.diff(below.astype(int))
    starts = list(np.where(edges == 1)[0] + 1)
    ends   = list(np.where(edges == -1)[0] + 1)
    if below[0]:
        starts.insert(0, 0)
    if below[-1]:
        ends.append(len(d))
    return [(t[s], t[e-1], d[s:e].min()) for s, e in zip(starts, ends)]


def write_summary(data, label, out_dir):
    t, d = data["t"], data["dmin"]
    events_contact = detect_events(t, d, CONTACT_THRESHOLD_NM)
    events_near    = detect_events(t, d, NEAR_THRESHOLD_NM)

    idx_min = int(np.argmin(d))
    lines = [
        f"== Adsorption analysis: {label} ==",
        f"  Trajectory span        : {t[0]:.1f} – {t[-1]:.1f} ns ({len(t)} frames)",
        f"  Min nearest-atom dist  : {d.min():.3f} nm  @ t = {t[idx_min]:.1f} ns",
        f"  Frames below 0.30 nm   : {(d <= 0.30).sum()} / {len(d)}  "
        f"({100*(d <= 0.30).mean():.2f}%)",
        f"  Frames below 0.50 nm   : {(d <= 0.50).sum()} / {len(d)}  "
        f"({100*(d <= 0.50).mean():.2f}%)",
        f"  Frames below 1.00 nm   : {(d <= 1.00).sum()} / {len(d)}  "
        f"({100*(d <= 1.00).mean():.2f}%)",
        "",
        f"  Contact events (≤ {CONTACT_THRESHOLD_NM} nm): {len(events_contact)}",
    ]
    for i, (s, e, m) in enumerate(events_contact, 1):
        lines.append(f"    #{i:2d}  {s:7.1f} – {e:7.1f} ns  (Δ {e-s:6.1f} ns)  "
                     f"min = {m:.3f} nm")
    lines.append("")
    lines.append(f"  Approach events (≤ {NEAR_THRESHOLD_NM} nm): {len(events_near)}")
    for i, (s, e, m) in enumerate(events_near, 1):
        lines.append(f"    #{i:2d}  {s:7.1f} – {e:7.1f} ns  (Δ {e-s:6.1f} ns)  "
                     f"min = {m:.3f} nm")

    out = "\n".join(lines)
    print(out)
    (out_dir / f"{label}_adsorption_summary.txt").write_text(out + "\n")


def plot(data, label, out_dir):
    t, d = data["t"], data["dmin"]
    pz_max, pz_min = data["pz_max"], data["pz_min"]
    zu, zl = data["z_up"], data["z_lo"]

    pct_contact = 100.0 * (d <= CONTACT_THRESHOLD_NM).mean()
    n_events    = len(detect_events(t, d, CONTACT_THRESHOLD_NM))

    fig, axes = plt.subplots(2, 1, figsize=(double_width, 4.6),
                             sharex=True,
                             gridspec_kw={"hspace": 0.08, "height_ratios": [1.1, 1.0]})

    # ── Panel 1: protein vertical extent vs interface bands ─────────────
    ax1 = axes[0]
    ax1.fill_between(t, zl, zu, color=COLORS["interface"], alpha=0.08,
                     label="Water slab extent")
    ax1.plot(t, pz_max, color=COLORS["replica1"], lw=0.5, alpha=0.35)
    ax1.plot(t, smooth_sg(pz_max), color=COLORS["replica1"], lw=1.3,
             label="Topmost protein atom")
    ax1.plot(t, pz_min, color=COLORS["replica3"], lw=0.5, alpha=0.35)
    ax1.plot(t, smooth_sg(pz_min), color=COLORS["replica3"], lw=1.3,
             label="Bottommost protein atom")
    ax1.plot(t, smooth_sg(zu), color=COLORS["interface"], lw=1.0, ls="--",
             alpha=0.65, label="Interface (upper/lower)")
    ax1.plot(t, smooth_sg(zl), color=COLORS["interface"], lw=1.0, ls="--",
             alpha=0.65)
    ax1.set_ylabel("Z position (nm)")
    ax1.legend(loc="upper right", fontsize=6.5, framealpha=0.92,
               edgecolor="0.75", handlelength=1.5, ncol=2)

    # ── Panel 2: nearest-atom distance ──────────────────────────────────
    ax2 = axes[1]

    # shade contact windows first (behind traces)
    for s, e, _ in detect_events(t, d, CONTACT_THRESHOLD_NM):
        ax2.axvspan(s, e, color=COLORS["distance"], alpha=0.18, zorder=0)

    ax2.axhline(0.0, color="0.5", lw=0.5, alpha=0.5, zorder=1)
    ax2.axhline(CONTACT_THRESHOLD_NM, color="0.25", lw=0.9, ls="--", zorder=2,
                label=f"Contact threshold ({CONTACT_THRESHOLD_NM} nm)")
    ax2.axhline(NEAR_THRESHOLD_NM, color="0.55", lw=0.8, ls=":", zorder=2,
                label=f"Approach ({NEAR_THRESHOLD_NM} nm)")

    ax2.plot(t, d, color=COLORS["distance"], lw=0.5, alpha=0.35, zorder=3,
             rasterized=True)
    ax2.plot(t, smooth_sg(d), color=COLORS["distance"], lw=1.4, zorder=4,
             label="Min protein–interface distance")

    ax2.set_xlabel("Time (ns)")
    ax2.set_ylabel("Nearest atom → interface (nm)")
    # Legend placed OUTSIDE axes below x-label — no interior data overlap possible
    ax2.legend(bbox_to_anchor=(0.5, -0.30), loc="upper center", ncol=3,
               fontsize=6.5, framealpha=0.92, edgecolor="0.75")
    ax2.set_ylim(bottom=min(-0.35, d.min() - 0.15))
    ax2.set_xlim(t[0], t[-1])

    # Reserve bottom margin for the outside legend
    plt.tight_layout(rect=[0, 0.19, 1, 1])
    savefig(fig, out_dir / f"{label}_adsorption_contact.png")
    print(f"  → wrote {out_dir / f'{label}_adsorption_contact.png'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tpr", required=True)
    ap.add_argument("--xtc", required=True, nargs="+",
                    help="One or more XTC files (concatenated in order)")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", default="results/figures/adsorption")
    ap.add_argument("--stride", type=int, default=1)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    xtc = args.xtc[0] if len(args.xtc) == 1 else args.xtc
    print(f"[{args.label}] loading {xtc}")
    data = analyse(args.tpr, xtc, stride=args.stride)
    write_summary(data, args.label, out_dir)
    plot(data, args.label, out_dir)


if __name__ == "__main__":
    main()
