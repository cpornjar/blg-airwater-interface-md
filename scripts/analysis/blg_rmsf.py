"""
precompute_rmsf.py — compute per-residue RMSF for CENTER and R1, save to cache.
Processes one trajectory at a time (no simultaneous universes) to avoid OOM.
Cache files: results/gate_analysis/rmsf_{label}.resids.npy + .rmsf.npy
"""
import sys
import gc
import tempfile
import os
from pathlib import Path
import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis import align, rms
from MDAnalysis.transformations import unwrap

ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = ROOT / "results" / "gate_analysis"

CENTER_TPR  = ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr"
CENTER_XTC  = ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"
R1_TPR      = ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr"
R1_XTC_LIST = [ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc"] + \
              sorted((ROOT / "outputs_BLG/REPLICA/MD/MD1").glob("md_replica1_amd.part00*.xtc"))

STRIDE = 10   # 1 ns resolution — sufficient for RMSF


def compute_and_cache(label, tpr, xtc, cache_prefix, stride=STRIDE):
    cache_resids = Path(cache_prefix + ".resids.npy")
    cache_rmsf   = Path(cache_prefix + ".rmsf.npy")
    if cache_resids.exists() and cache_rmsf.exists():
        print(f"  {label}: cache already exists, skipping")
        return

    print(f"  {label}: loading trajectory …")
    if isinstance(xtc, list):
        u = mda.Universe(str(tpr), *[str(x) for x in xtc])
    else:
        u = mda.Universe(str(tpr), str(xtc))
    prot = u.select_atoms("protein")
    u.trajectory.add_transformations(unwrap(prot))
    print(f"  {label}: {u.trajectory.n_frames} frames | {u.trajectory.totaltime/1000:.0f} ns")

    ca_sel = "protein and name CA"
    with tempfile.NamedTemporaryFile(suffix=".xtc", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        print(f"  {label}: AlignTraj (stride={stride}) …")
        align.AlignTraj(u, u, select=ca_sel, filename=tmp_path).run(step=stride)
        u2 = mda.Universe(u.filename, tmp_path)
        ca  = u2.select_atoms(ca_sel)
        print(f"  {label}: RMSF on {u2.trajectory.n_frames} frames …")
        rmsf_calc = rms.RMSF(ca).run()
        resids = ca.resids
        rmsf   = rmsf_calc.results.rmsf / 10   # Å → nm
    finally:
        os.unlink(tmp_path)

    np.save(str(cache_resids), resids)
    np.save(str(cache_rmsf),   rmsf)
    print(f"  {label}: saved → {cache_prefix}.{{resids,rmsf}}.npy")

    del u, prot, u2, ca, rmsf_calc
    gc.collect()


if __name__ == "__main__":
    print("=== RMSF precomputation (one universe at a time) ===")
    compute_and_cache("CENTER", CENTER_TPR, CENTER_XTC,
                      str(CACHE_DIR / "rmsf_center"))
    compute_and_cache("R1",     R1_TPR,     R1_XTC_LIST,
                      str(CACHE_DIR / "rmsf_r1"))
    print("Done.")
