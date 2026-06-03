"""
make_fig3_activation.py
========================
Paper Fig 3 — R1 4-panel showing loop-mediated, calyx-localised activation:
  (a) Hydrophobic SASA bursts over 650 ns, recurring every 30-40 ns
  (b) Radius of gyration — flat at ~1.496 nm (compact, no global unfolding)
  (c) Per-residue RMSF: CENTER vs R1 overlay (Loop BC dominant in bulk,
      CD/EF region elevated near interface)
  (d) Hydrophobic patch RMSD — slow ratchet 0.305 -> 0.326 nm over 500-650 ns

Data: SET 1A (CENTER, 1000 ns) and SET 1B R1 (650 ns combined trajectory)
Output: results/figures/PAPER_FIG3_ACTIVATION.png

Usage:
    source ~/research-env/bin/activate
    python scripts/make_fig3_activation.py
"""

import sys
import gc
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import MDAnalysis as mda
from MDAnalysis.analysis import rms, align
from MDAnalysis.transformations import unwrap
import freesasa

ROOT = Path(__file__).resolve().parent.parent

CENTER_TPR = ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr"
CENTER_XTC = ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"
R1_TPR     = ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr"
R1_XTC     = [ROOT / f"outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc"] + \
             sorted((ROOT / "outputs_BLG/REPLICA/MD/MD1").glob("md_replica1_amd.part00*.xtc"))
OUT        = ROOT / "results/figures/PAPER_FIG3_ACTIVATION.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

STRIDE_FAST = 5    # 0.5 ns resolution for SASA/Rg time series
STRIDE_RMSD = 10   # 1 ns for patch RMSD (slower computation OK at coarse)
HYDROPHOBIC_RESNAMES = ["ALA","VAL","ILE","LEU","PRO","PHE","MET","TRP",
                        "CYS","GLY","TYR","HIS"]
RADIUS_MAP = {"C":1.70,"N":1.55,"O":1.52,"S":1.80,"H":1.20,"P":1.80}

CALYX_RESIDS    = [39, 41, 56, 58, 92, 103, 105, 107, 125]
BC_LOOP_RESIDS  = list(range(30, 36))   # residues 30-35
CD_LOOP_RESIDS  = list(range(57, 61))   # residues 57-60

ACTIVATION_SASA = 32.10   # p95 of pooled PBC-corrected SASA (distribution-based threshold)


def calc_hydrophobic_sasa(protein):
    coords = protein.positions
    radii  = [RADIUS_MAP.get(a.name[0].upper(), 1.70) for a in protein.atoms]
    res    = freesasa.calcCoord(coords.flatten().tolist(), radii)
    sasa   = np.array([res.atomArea(i) for i in range(len(protein.atoms))])
    mask   = np.array([a.resname in HYDROPHOBIC_RESNAMES for a in protein.atoms])
    return float(sasa[mask].sum()) / 100.0


def time_series(u, stride):
    protein = u.select_atoms("protein")
    times, sasa, rg = [], [], []
    for ts in u.trajectory[::stride]:
        times.append(ts.time / 1000.0)
        sasa.append(calc_hydrophobic_sasa(protein))
        rg.append(protein.radius_of_gyration() / 10)
    return np.array(times), np.array(sasa), np.array(rg)


def per_residue_rmsf(u, cache_path=None, stride=10):
    """Align trajectory on-disk (no in_memory), then compute Ca RMSF per residue.

    Uses a cache .npy file to skip recomputation on subsequent runs.
    stride=10 → 1 ns resolution (sufficient for RMSF; saves ~10× time).
    """
    import tempfile, os
    if cache_path is not None and Path(cache_path + ".resids.npy").exists():
        resids = np.load(cache_path + ".resids.npy")
        rmsf   = np.load(cache_path + ".rmsf.npy")
        print(f"  RMSF: loaded from cache {cache_path}")
        return resids, rmsf

    ca_sel = "protein and name CA"
    with tempfile.NamedTemporaryFile(suffix=".xtc", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        align.AlignTraj(u, u, select=ca_sel, filename=tmp_path).run(step=stride)
        u2 = mda.Universe(u.filename, tmp_path)
        ca = u2.select_atoms(ca_sel)
        rmsf_calc = rms.RMSF(ca).run()
        resids = ca.resids
        rmsf   = rmsf_calc.results.rmsf / 10   # A -> nm
    finally:
        os.unlink(tmp_path)

    if cache_path is not None:
        np.save(cache_path + ".resids.npy", resids)
        np.save(cache_path + ".rmsf.npy",   rmsf)
        print(f"  RMSF: saved cache to {cache_path}")
    return resids, rmsf


def patch_rmsd(u, stride):
    """Hydrophobic patch RMSD vs first frame."""
    sel = "(" + " or ".join([f"resid {r}" for r in CALYX_RESIDS]) + ") and name CA"
    r = rms.RMSD(u, u, select=sel, ref_frame=0).run(step=stride)
    times = r.results.rmsd[:, 1] / 1000.0   # ps -> ns
    rmsd  = r.results.rmsd[:, 2] / 10        # A -> nm
    return times, rmsd


# ── Load both trajectories ─────────────────────────────────────────────────────
print("Loading CENTER ...")
u_c = mda.Universe(str(CENTER_TPR), str(CENTER_XTC))
prot_c = u_c.select_atoms("protein")
u_c.trajectory.add_transformations(unwrap(prot_c))
print(f"  CENTER: {u_c.trajectory.n_frames} frames | {u_c.trajectory.totaltime/1000:.0f} ns")

print("Loading R1 ...")
u_r = mda.Universe(str(R1_TPR), *[str(x) for x in R1_XTC]) if isinstance(R1_XTC, list) else mda.Universe(str(R1_TPR), str(R1_XTC))
prot_r = u_r.select_atoms("protein")
u_r.trajectory.add_transformations(unwrap(prot_r))
print(f"  R1:     {u_r.trajectory.n_frames} frames | {u_r.trajectory.totaltime/1000:.0f} ns")

# ── R1 time series: SASA + Rg ────────────────────────────────────────────────
print("\nComputing R1 SASA and Rg (stride={})...".format(STRIDE_FAST))
t_r, sasa_r, rg_r = time_series(u_r, STRIDE_FAST)
print(f"  R1 SASA mean {sasa_r.mean():.2f} +/- {sasa_r.std():.2f} nm^2 ; max {sasa_r.max():.2f}")
print(f"  R1 Rg   mean {rg_r.mean():.3f} +/- {rg_r.std():.3f} nm ; range {rg_r.min():.3f}-{rg_r.max():.3f}")

# ── RMSF for both: CENTER vs R1 ─────────────────────────────────────────────
# Save metadata before freeing CENTER universe
center_totaltime = u_c.trajectory.totaltime
r1_totaltime     = u_r.trajectory.totaltime

CACHE_DIR = ROOT / "results" / "gate_analysis"   # reuse existing results dir
print("\nComputing CENTER per-residue RMSF...")
resids_c, rmsf_c = per_residue_rmsf(u_c,
    cache_path=str(CACHE_DIR / "rmsf_center"))
# Release CENTER universe before R1 RMSF — prevents double-universe OOM crash
del u_c, prot_c
gc.collect()

print("Computing R1 per-residue RMSF...")
resids_r, rmsf_r = per_residue_rmsf(u_r,
    cache_path=str(CACHE_DIR / "rmsf_r1"))

print("Computing R1 hydrophobic patch RMSD (stride={})...".format(STRIDE_RMSD))
t_p, rmsd_p = patch_rmsd(u_r, STRIDE_RMSD)
print(f"  Patch RMSD: mean {rmsd_p.mean():.3f} nm ; range {rmsd_p.min():.3f}-{rmsd_p.max():.3f}")

# ── Apply publication style ───────────────────────────────────────────────────
import sys as _sys
_sys.path.insert(0, str(ROOT / "scripts"))
from plot_style import apply_style, COLORS as PC, double_width, savefig_pdf as savefig
apply_style()

# ── Build figure ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(double_width, 4.6))   # JCIS double-col width; 4.6 in → ~4.4 in PDF → 7.6pt fonts, fits on text page
gs = fig.add_gridspec(2, 2, hspace=0.60, wspace=0.35,
                      left=0.09, right=0.97, top=0.97, bottom=0.14)

# (a) SASA bursts ─────────────────────────────────────────────────────────────
ax = fig.add_subplot(gs[0, 0])
ax.fill_between(t_r, 22, sasa_r, alpha=0.25, color="#E74C3C")
ax.plot(t_r, sasa_r, color="#E74C3C", lw=1.0)
ax.axhline(ACTIVATION_SASA, color="0.3", lw=1, ls="--", alpha=0.7)
# Label placed just above the line at t=0 edge (sparse zone above p95)
ax.text(0.98, ACTIVATION_SASA + 0.15,
        f"p95 = {ACTIVATION_SASA:.1f} nm²",
        transform=ax.get_yaxis_transform(), fontsize=7, color="0.35",
        va="bottom", ha="right")

ax.set_xlabel("Time (ns)")
ax.set_ylabel("Hydrophobic SASA (nm²)")
ax.text(0.02, 0.97, "(a)", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top", ha="left")
ax.set_ylim(bottom=21.5)

# (b) Rg flat ────────────────────────────────────────────────────────────────
ax = fig.add_subplot(gs[0, 1])
ax.plot(t_r, rg_r, color="#1ABC9C", lw=1.0, alpha=0.7, label="R$_\\mathrm{g}$")
# smoothed mean
window = max(11, len(rg_r)//20 | 1)
from numpy.lib.stride_tricks import sliding_window_view
if len(rg_r) > window:
    sm = sliding_window_view(rg_r, window).mean(axis=1)
    ax.plot(t_r[window//2:window//2+len(sm)], sm, color="#16A085", lw=2,
            label="Rolling avg.")
ax.axhline(rg_r.mean(), color="#444", lw=1, ls="--", alpha=0.7)
ax.set_xlabel("Time (ns)")
ax.set_ylabel("R$_\\mathrm{g}$ (nm)")
ax.text(0.02, 0.97, "(b)", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top", ha="left")
# Mean annotation placed outside axes at right edge (no overlap with data)
ax.text(1.01, rg_r.mean(), f"mean {rg_r.mean():.3f} nm",
        transform=ax.get_yaxis_transform(), fontsize=7, color="#444",
        va="center", ha="left", clip_on=False)
# Tight y-axis to show flatness
y_pad = 0.04
ax.set_ylim(rg_r.mean() - y_pad, rg_r.mean() + y_pad)
ax.legend(loc="upper right", fontsize=7, framealpha=0.92, edgecolor="0.75",
          handlelength=1.5)

# (c) RMSF CENTER vs R1 ─────────────────────────────────────────────────────
ax = fig.add_subplot(gs[1, 0])
ax.plot(resids_c, rmsf_c, color="#2E86AB", lw=1.2, alpha=0.85,
        label=f"CENTER (bulk, {center_totaltime/1000:.0f} ns)")
ax.plot(resids_r, rmsf_r, color="#E74C3C", lw=1.2, alpha=0.85,
        label=f"R1 (near interface, {r1_totaltime/1000:.0f} ns)")

# highlight Loop BC and Loop CD/EF
ax.axvspan(BC_LOOP_RESIDS[0], BC_LOOP_RESIDS[-1], color="#2E86AB", alpha=0.13,
           label=f"Loop BC ({BC_LOOP_RESIDS[0]}–{BC_LOOP_RESIDS[-1]})")
ax.axvspan(CD_LOOP_RESIDS[0], CD_LOOP_RESIDS[-1], color="#E74C3C", alpha=0.13,
           label=f"Loop CD/EF ({CD_LOOP_RESIDS[0]}–{CD_LOOP_RESIDS[-1]})")

ax.set_xlabel("Residue")
ax.set_ylabel("Cα RMSF (nm)")
ax.text(0.02, 0.97, "(c)", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top", ha="left")
ax.legend(bbox_to_anchor=(0.5, -0.14), loc="upper center", ncol=2,
          fontsize=7, framealpha=0.92, edgecolor="0.75", handlelength=1.5)
ax.set_xlim(0, max(resids_c.max(), resids_r.max()))

# (d) Patch RMSD ratchet ─────────────────────────────────────────────────────
ax = fig.add_subplot(gs[1, 1])
ax.plot(t_p, rmsd_p, color="#8E44AD", lw=1.0, alpha=0.6)
# Smoothed line
sm, sm_times = None, None
if len(rmsd_p) > 11:
    window = max(11, len(rmsd_p)//20 | 1)
    sm = sliding_window_view(rmsd_p, window).mean(axis=1)
    sm_times = t_p[window//2:window//2+len(sm)]
    ax.plot(sm_times, sm, color="#5B2C6F", lw=2, label="Running mean")

# annotate using smoothed running mean (matches plotted line, stays in y-range) — offset inward to avoid clipping
for t_target in [500, 650]:
    if t_target <= t_p.max() and sm is not None:
        idx_sm = int(np.argmin(np.abs(sm_times - t_target)))
        local = sm[idx_sm]   # smoothed value — matches plotted running mean
        ax.plot(sm_times[idx_sm], local, "o", color="#5B2C6F", ms=6, zorder=5)
        # 500 ns: offset UP; 650 ns: offset DOWN — prevents text collision
        x_offset = -65 if t_target == 650 else 20
        y_offset = +0.045 if t_target == 500 else -0.055
        ax.annotate(f"{local:.3f} nm\n@ {t_target} ns",
                    xy=(sm_times[idx_sm], local),
                    xytext=(sm_times[idx_sm] + x_offset, local + y_offset),
                    fontsize=7.5, color="#4A235A",
                    arrowprops=dict(arrowstyle="-", lw=0.7, color="#8E44AD"))

ax.set_ylim(0.10, 0.32)   # crop empty bottom; data lives in 0.15-0.30 nm
ax.set_xlabel("Time (ns)")
ax.set_ylabel("Calyx patch Cα RMSD (nm)")
ax.text(0.02, 0.97, "(d)", transform=ax.transAxes, fontsize=9, fontweight="bold", va="top", ha="left")
ax.legend(bbox_to_anchor=(0.5, -0.14), loc="upper center", ncol=1,
          fontsize=7, framealpha=0.92, edgecolor="0.75")

savefig(fig, OUT)
plt.close(fig)
print(f"\nSaved -> {OUT}")
print(f"  R1 Rg mean: {rg_r.mean():.3f} +/- {rg_r.std():.3f} nm")
print(f"  CENTER RMSF max: {rmsf_c.max():.3f} nm at residue {resids_c[np.argmax(rmsf_c)]}")
print(f"  R1     RMSF max: {rmsf_r.max():.3f} nm at residue {resids_r[np.argmax(rmsf_r)]}")
if len(t_p) > 0 and t_p.max() >= 650:
    idx500 = int(np.argmin(np.abs(t_p - 500)))
    idx650 = int(np.argmin(np.abs(t_p - 650)))
    print(f"  Patch RMSD 500 ns ~ {rmsd_p[idx500-10:idx500+10].mean():.3f} nm")
    print(f"  Patch RMSD 650 ns ~ {rmsd_p[idx650-10:idx650+10].mean():.3f} nm")
