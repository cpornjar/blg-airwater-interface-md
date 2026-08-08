"""
blg_rmsd.py
===========
Cα RMSD for BLG, all 4 replicas, four regions — implements the methodology
already written in docs/METHODS.md:66-67 but never turned into a script
(no blg_rmsd.py existed before this; the "Patch RMSD ~0.24 nm flat" and
"helix RMSD stays <=0.14 nm" numbers already quoted in CLAUDE.md /
COMFHA_Science_Notes.md were not traceable to any committed script).

Regions:
  backbone — all protein Cα (primary fit selection — see below)
  sheet    — Cα of residues DSSP-classified as beta-strand/bridge (E/B) in
             the REFERENCE frame (frame 0). Derived from the already-cached
             results/analysis/blg_dssp_{label}.npz rather than a hand-picked
             "strands A-H" range, which is not recorded anywhere in this
             project with exact residue boundaries. NOTE: docs/METHODS.md
             says "strands A-I" — that's very likely a documentation bug:
             docs/COMFHA_Science_Notes.md independently describes the fold
             as "8 beta-strands (A-H)" plus a *separate* C-terminal alpha
             helix that lipocalin nomenclature also happens to label
             "helix I" — i.e. "I" names the helix, not a 9th strand. Worth
             fixing that line in METHODS.md; not done here (docs, not code).
  helix    — Cα of residues 130-140 (docs/METHODS.md, the C-terminal helix)
  patch    — Cα of the calyx-lining residues 39,41,56,58,92,103,105,107,125
             (same list as scripts/analysis/blg_calyx_sasa.py's CALYX_RESIDS)

Reference frame: frame 0 of each trajectory (self-referenced per replica,
not a shared cross-replica reference) — matches docs/METHODS.md and is the
field-standard choice for a "did this replica drift from its own start"
stability plot; Rg and PCA already cover cross-replica comparison.

Fit: MDAnalysis rms.RMSD superposes once on the full Cα backbone (the
primary `select`), then reports sheet/helix/patch RMSD via `groupselections`
using that SAME rotation (no independent re-fit per region). This measures
"how much does this region move within the globally-aligned structure" —
the right question for "does the calyx patch move independently of the
rest of the protein," not "how rigid is the patch on its own."

Usage:
    python -u scripts/analysis/blg_rmsd.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_rmsd_{label}.npz
  keys: time_ns, rmsd_backbone, rmsd_sheet, rmsd_helix, rmsd_patch (nm)
        sheet_resids (int array, resolved region used, for audit)
"""

import argparse
import gc
import sys
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import rms
from MDAnalysis.transformations import unwrap

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

HELIX_RESIDS = list(range(130, 141))
PATCH_RESIDS = [39, 41, 56, 58, 92, 103, 105, 107, 125]  # blg_calyx_sasa.py CALYX_RESIDS
SHEET_CODES = {'E', 'B'}

STRIDE = 10  # matches blg_dssp.py / blg_rmsf.py — 1 ns resolution

# Same trajectory paths already proven correct in blg_dssp.py (base tpr,
# not the tpx-119-unreadable _ext.tpr for R2/R3).
TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"],
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
        "xtc": [ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc"] +
               sorted((ROOT / "outputs_BLG/REPLICA/MD/MD1").glob("md_replica1_amd.part00*.xtc")),
    },
    "R2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2.tpr",
        "xtc": [ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
                ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.part0002.xtc"],
    },
    "R3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3.tpr",
        "xtc": [ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
                ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.part0002.xtc"],
    },
}


def sheet_resids_from_dssp(label, fallback_resids):
    """β-sheet Cα region = DSSP E/B classification on the REFERENCE frame
    (frame 0), read from the already-computed results/analysis/blg_dssp_
    {label}.npz. Falls back to computing DSSP fresh on frame 0 only if that
    cache doesn't exist yet (should not happen — dssp already ran for all 4
    replicas this session)."""
    dssp_npz = OUT / f"blg_dssp_{label}.npz"
    if dssp_npz.exists():
        d = np.load(dssp_npz)
        # blg_dssp.py runs DSSP.run(step=STRIDE) with start=None (=0), so the
        # first sampled frame IS true frame 0 — matches the RMSD ref_frame=0
        # used below exactly, not an approximation.
        codes0 = d["dssp_codes"][0]
        resids = d["residue_ids"]
        sheet = resids[[c in SHEET_CODES for c in codes0]]
        return sheet
    print(f"  [WARN] {label}: no cached blg_dssp_{label}.npz — "
          f"falling back to full backbone for the 'sheet' region")
    return fallback_resids


def analyse_label(label):
    cfg = TRAJS[label]
    tpr = cfg["tpr"]
    xtc_list = [p for p in cfg["xtc"] if p.exists()]
    if not tpr.exists() or not xtc_list:
        print(f"[SKIP] {label}: tpr/xtc not found")
        return

    out_npz = OUT / f"blg_rmsd_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")
    u = mda.Universe(str(tpr), *[str(x) for x in xtc_list])
    protein = u.select_atoms("protein")
    u.trajectory.add_transformations(unwrap(protein))
    print(f"  Frames: {u.trajectory.n_frames}  Residues: {protein.n_residues}")

    ca_all = protein.select_atoms("name CA")
    all_resids = ca_all.resids

    sheet_resids = sheet_resids_from_dssp(label, all_resids)
    helix_present = np.intersect1d(all_resids, HELIX_RESIDS)
    patch_present = np.intersect1d(all_resids, PATCH_RESIDS)
    if len(patch_present) != len(PATCH_RESIDS):
        print(f"  [WARN] {label}: only {len(patch_present)}/{len(PATCH_RESIDS)} "
              f"calyx patch residues present in this structure")

    sheet_sel = "name CA and resid " + " ".join(str(r) for r in sheet_resids)
    helix_sel = "name CA and resid " + " ".join(str(r) for r in helix_present)
    patch_sel = "name CA and resid " + " ".join(str(r) for r in patch_present)

    print(f"  Regions: sheet={len(sheet_resids)} CA, helix={len(helix_present)} CA, "
          f"patch={len(patch_present)} CA (of {len(all_resids)} total)")

    print(f"  Computing RMSD (stride={STRIDE}) …")
    R = rms.RMSD(
        protein, protein,
        select="name CA",
        groupselections=[sheet_sel, helix_sel, patch_sel],
        ref_frame=0,
    )
    R.run(step=STRIDE, verbose=True)

    # R.results.rmsd columns: [frame, time_ps, backbone, sheet, helix, patch]  (Å)
    arr = R.results.rmsd
    time_ns = arr[:, 1] / 1000.0
    rmsd_backbone = arr[:, 2] / 10.0
    rmsd_sheet    = arr[:, 3] / 10.0
    rmsd_helix    = arr[:, 4] / 10.0
    rmsd_patch    = arr[:, 5] / 10.0

    print(f"  Mean RMSD (nm): backbone={rmsd_backbone.mean():.3f} "
          f"sheet={rmsd_sheet.mean():.3f} helix={rmsd_helix.mean():.3f} "
          f"patch={rmsd_patch.mean():.3f}")

    np.savez(
        out_npz,
        time_ns=time_ns,
        rmsd_backbone=rmsd_backbone,
        rmsd_sheet=rmsd_sheet,
        rmsd_helix=rmsd_helix,
        rmsd_patch=rmsd_patch,
        sheet_resids=sheet_resids,
        helix_resids=helix_present,
        patch_resids=patch_present,
    )
    print(f"  Saved: {out_npz.name}")

    del u, protein, ca_all, R, arr
    gc.collect()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="all",
                     choices=["CENTER", "R1", "R2", "R3", "all"])
    args = ap.parse_args()
    labels = list(TRAJS) if args.label == "all" else [args.label]
    for lab in labels:
        analyse_label(lab)


if __name__ == "__main__":
    main()
