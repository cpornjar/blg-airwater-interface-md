"""
combined_compare.py
===================
BLG vs β-Casein comparison table — loads both proteins' analysis .npz
files and prints a side-by-side summary for Paper 1 Fig 4.

Handles missing CAS data gracefully: columns show [DATA PENDING] until
cas_*.npz files are produced after production MD finishes.

Metrics compared (Fig 4 table):
  - Surface tension γ (mN/m)
  - DSSP: helix / sheet / coil (%)
  - Protein–protein HBonds (mean ± std)
  - Protein–water HBonds (mean ± std)
  - Interface water–water HBonds (mean ± std)
  - Signature feature SASA (nm²): BLG calyx (res 39,41,56,58,92,103,105,107,125)
                                    vs CAS N-term (res 1-25)
  - Contact fraction (%)
  - Contact event count

Usage:
    python scripts/analysis/combined_compare.py

Output: results/analysis/comparison_table.npz
        prints table to stdout
"""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
ANA  = ROOT / "results" / "analysis"
GATE = ROOT / "results" / "gate_analysis"

PENDING = "DATA PENDING"


def load(path, key):
    """Load scalar from npz, return None if file or key missing."""
    try:
        d = np.load(path, allow_pickle=True)
        v = d[key]
        return float(v) if v.ndim == 0 else v
    except Exception:
        return None


def fmt(mean, std=None):
    if mean is None:
        return PENDING
    if std is None or std == 0:
        return f"{mean:.2f}"
    return f"{mean:.2f} ± {std:.2f}"


def fmt_pct(val):
    if val is None:
        return PENDING
    return f"{val*100:.1f}%"


def main():
    print("\n" + "="*70)
    print("  BLG vs β-Casein — Comparative Analysis (Paper 1, Fig 4)")
    print("="*70)

    rows = []

    # ── Surface tension ──────────────────────────────────────────────────
    blg_st   = load(ANA / "blg_surface_tension_CENTER.npz", "gamma_mean")
    blg_st_s = load(ANA / "blg_surface_tension_CENTER.npz", "gamma_std")
    cas_st   = load(ANA / "cas_surface_tension_CENTER.npz", "gamma_mean")
    cas_st_s = load(ANA / "cas_surface_tension_CENTER.npz", "gamma_std")
    rows.append(("Surface tension (mN/m)", fmt(blg_st, blg_st_s), fmt(cas_st, cas_st_s)))

    # ── DSSP ─────────────────────────────────────────────────────────────
    for key, label in [("mean_helix", "Helix (%)"), ("mean_sheet", "Sheet (%)"),
                       ("mean_coil",  "Coil  (%)")]:
        blg_v = load(ANA / "blg_dssp_CENTER.npz", key)
        cas_v = load(ANA / "cas_dssp_CENTER.npz", key)
        rows.append((f"DSSP {label}", fmt_pct(blg_v), fmt_pct(cas_v)))

    # ── HBonds ───────────────────────────────────────────────────────────
    for key, label in [
        ("mean_prot_prot",      "Prot–prot HBonds"),
        ("mean_prot_water",     "Prot–water HBonds"),
        ("mean_water_interface","Interface H₂O HBonds"),
    ]:
        blg_v = load(ANA / "blg_hbonds_CENTER.npz", key)
        cas_v = load(ANA / "cas_hbonds_CENTER.npz", key)
        rows.append((label, fmt(blg_v), fmt(cas_v)))

    # ── Signature feature SASA ────────────────────────────────────────────
    blg_csasa   = load(ANA / "blg_calyx_sasa_CENTER.npz", "calyx_sasa_nm2")
    blg_csasa_s = None
    if blg_csasa is not None:
        arr = np.load(ANA / "blg_calyx_sasa_CENTER.npz")["calyx_sasa_nm2"]
        blg_csasa, blg_csasa_s = float(arr.mean()), float(arr.std())

    cas_nsasa   = load(ANA / "cas_nterm_sasa_CENTER.npz", "mean_nm2")
    cas_nsasa_s = load(ANA / "cas_nterm_sasa_CENTER.npz", "std_nm2")
    rows.append(("Signature SASA (nm²)",
                 fmt(blg_csasa, blg_csasa_s) + " [calyx]",
                 fmt(cas_nsasa, cas_nsasa_s) + (" [N-term 1-25]" if cas_nsasa else "")))

    # ── Contact ───────────────────────────────────────────────────────────
    # BLG: locked value from 4-replica gate analysis
    blg_events = 613   # verified, CLAUDE.md locked value
    blg_cf_arr = []
    for replica in ["CENTER", "R1", "R2", "R3"]:
        gf = GATE / f"{replica}_gate.npz"
        if gf.exists():
            d = np.load(gf)
            if "contact_mask" in d:
                blg_cf_arr.append(d["contact_mask"].mean())
            elif "dmin_nm" in d:
                blg_cf_arr.append((d["dmin_nm"] <= 0.30).mean())
    blg_cf = float(np.mean(blg_cf_arr)) if blg_cf_arr else None

    cas_events = load(ANA / "cas_contact_CENTER.npz", "n_contact_events")
    cas_cf     = load(ANA / "cas_contact_CENTER.npz", "contact_fraction")

    rows.append(("Contact events (all replicas)",
                 f"{blg_events} (4×1µs)",
                 fmt(cas_events) + (" events" if cas_events else "")))
    rows.append(("Contact fraction",
                 fmt_pct(blg_cf),
                 fmt_pct(cas_cf)))

    # ── Print table ───────────────────────────────────────────────────────
    col0 = max(len(r[0]) for r in rows) + 2
    col1 = max(max(len(r[1]) for r in rows), len("BLG CENTER")) + 2
    print(f"\n  {'Metric':<{col0}}{'BLG CENTER':<{col1}}{'CAS CENTER'}")
    print(f"  {'-'*col0}{'-'*col1}{'-'*30}")
    for label, blg_val, cas_val in rows:
        pending = cas_val == PENDING
        marker = " ←" if pending else ""
        print(f"  {label:<{col0}}{blg_val:<{col1}}{cas_val}{marker}")

    n_pending = sum(1 for _, _, c in rows if c == PENDING)
    n_total   = len(rows)
    print(f"\n  {n_total - n_pending}/{n_total} metrics complete  "
          f"({'CAS data pending' if n_pending else 'ALL COMPLETE ✓'})")

    # ── Save ─────────────────────────────────────────────────────────────
    out = ANA / "comparison_table.npz"
    save_dict = {}
    for label, blg_val, cas_val in rows:
        key = label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("–", "_").replace("/", "_")
        save_dict[f"blg_{key}"] = blg_val
        save_dict[f"cas_{key}"] = cas_val
    np.savez(out, **save_dict)
    print(f"\n  Saved: {out.relative_to(ROOT)}\n")


if __name__ == "__main__":
    main()
