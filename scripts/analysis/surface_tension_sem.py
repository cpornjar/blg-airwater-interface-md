"""
surface_tension_sem.py
======================
Block-averaged standard error of the mean (SEM) for surface tension gamma(t).

Why: the +/- in blg/cas surface-tension tables is the instantaneous SD of the
per-frame pressure-tensor estimate (~35-39 mN/m). That is a property of the
estimator, not the uncertainty of the mean. Block averaging (non-overlapping
blocks, SEM across block means) gives a defensible error bar for the mean.
Reported at 5/10/20 blocks so the stability of the estimate is visible.

Usage: python -u scripts/analysis/surface_tension_sem.py
Output: results/analysis/surface_tension_sem.npz (+ printed table)
"""
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
AN = ROOT / "results" / "analysis"
RUNS = [("BLG", r) for r in ("CENTER", "R1", "R2", "R3")] + \
       [("CAS", r) for r in ("CENTER", "R1")]
NBLOCKS = (5, 10, 20)


def block_sem(x, nb):
    n = (len(x) // nb) * nb
    means = x[:n].reshape(nb, -1).mean(axis=1)
    return means.mean(), means.std(ddof=1) / np.sqrt(nb)


out = {}
print(f"{'run':12s} {'mean':>6s} {'SD':>6s}  " + "  ".join(f"SEM({nb}blk)" for nb in NBLOCKS))
for sp, r in RUNS:
    f = AN / f"{sp.lower()}_surface_tension_{r}.npz"
    if not f.exists():
        print(f"[skip] {f.name}")
        continue
    d = np.load(f, allow_pickle=True)
    g = np.asarray(d["gamma_mNm"], dtype=float)
    row = [block_sem(g, nb)[1] for nb in NBLOCKS]
    print(f"{sp+' '+r:12s} {g.mean():6.1f} {g.std():6.1f}  " + "  ".join(f"{s:9.2f}" for s in row))
    out[f"{sp}_{r}_mean"] = g.mean()
    out[f"{sp}_{r}_sd"] = g.std()
    out[f"{sp}_{r}_sem10"] = row[1]
    out[f"{sp}_{r}_sem_all"] = np.array(row)
np.savez(AN / "surface_tension_sem.npz", nblocks=np.array(NBLOCKS), **out)
print("saved", AN / "surface_tension_sem.npz")
