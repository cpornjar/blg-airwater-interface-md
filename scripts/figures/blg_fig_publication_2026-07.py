"""
blg_fig_publication_2026-07.py
==============================
Publication-quality BLG figures for the IFSC2026 supervisor conversation and
eventual journal reuse.  Loads ONLY the existing cached .npz results — runs no
new trajectory analysis — and renders to results/figures/pubready/.

The scientific story these figures must carry (all numbers locked in CLAUDE.md):
  The originally hypothesised "two-factor gate" (BLG commits when its hydrophobic
  calyx opens AND it orients favourably) was DISPROVEN after fixing a PBC artifact.
  Across 4.00 us of unbiased MD, BLG keeps a persistently accessible calyx, forms
  hundreds of transient contacts, but never commits to the interface — and calyx
  opening (SASA) and orientation (theta) are statistically uncorrelated
  (r = +0.006, 95% CI [-0.09, +0.11], rules out |r| > 0.11).

Figures produced (PNG @300 dpi + PDF):
  FIG1_null_correlation   — HEADLINE: SASA vs theta joint decorrelation
  FIG2_structural_stability — Rg, calyx SASA, total SASA, secondary structure
  FIG3_contact_no_commit  — min protein-interface distance, 4 replicas
  FIG4_physical_validation — surface tension (block SEM) + density profile

Usage:
  /Users/mac2022-1/opt/anaconda3/envs/research-env/bin/python3 \
      scripts/figures/blg_fig_publication_2026-07.py
"""

from pathlib import Path
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D

# ── project style helper (scripts/ is on the path when run from repo root) ────
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from plot_style import apply_style, COLORS, double_width, smooth_sg  # noqa: E402

apply_style()

GATE_DIR = ROOT / "results" / "gate_analysis"
ANA_DIR  = ROOT / "results" / "analysis"
OUT_DIR  = ROOT / "results" / "figures" / "pubready"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── consistent per-run identity ──────────────────────────────────────────────
RUNS = ["CENTER", "R1", "R2", "R3"]
RUN_LABEL = {"CENTER": "CENTER", "R1": "Replica 1",
             "R2": "Replica 2", "R3": "Replica 3"}
RUN_COLOR = {"CENTER": COLORS["center"], "R1": COLORS["replica1"],
             "R2": COLORS["replica2"], "R3": COLORS["replica3"]}

INK   = "#222222"   # near-black for text / axes emphasis
MUTED = "#8A8A8A"   # secondary annotation grey

CONTACT_NM = 0.3    # threshold that DEFINES the 613 locked contact events
LONG_NS    = 10.0   # long-event threshold

# documented two-factor gate-open criterion (blg_gate_analysis.py, GATE_SUMMARY.txt)
GATE_SASA_THR  = 35.0   # nm² hydrophobic-residue SASA — "activated" (calyx exposed)
GATE_ANGLE_THR = 30.0   # deg orientation angle — "aligned" (calyx faces interface)


def _save(fig, stem):
    png = OUT_DIR / f"{stem}.png"
    pdf = OUT_DIR / f"{stem}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.06)
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.06)
    print(f"    saved  {png.relative_to(ROOT)}")
    print(f"    saved  {pdf.relative_to(ROOT)}")
    plt.close(fig)


def _soft_legend(ax, *args, **kw):
    """Legend with a soft translucent backing, no hard border — legible over
    dense traces without the "bordered card" look of a full frame."""
    leg = ax.legend(*args, **kw)
    frame = leg.get_frame()
    frame.set_edgecolor("none")
    frame.set_facecolor("white")
    frame.set_alpha(0.78)
    return leg


def load_gate():
    out = {}
    for r in RUNS:
        d = np.load(GATE_DIR / f"{r}_gate.npz")
        out[r] = dict(time=d["time"], sasa=d["sasa"],
                      angle=d["angle"], min_dist=d["min_dist"].astype(float))
    return out


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — HEADLINE: the null correlation
# ─────────────────────────────────────────────────────────────────────────────
def fig1_null_correlation(gate):
    """SASA vs orientation angle, pooled over all 4 replicas (8006 frames).

    Design rationale (why this reads as a NULL in 5 s, not just a cloud):
      * hexbin = honest raw joint density backdrop;
      * the load-bearing device is the binned-mean overlay — theta averaged in
        6 SASA quantile bins is DEAD FLAT near 90 deg, which says "orientation
        does not track calyx opening" far louder than a small r in a corner;
      * marginal histograms show each variable is well-sampled on its own;
      * the rigorous inferential result (block-bootstrap r, CI, effective N)
        is annotated explicitly so the 8006-point cloud cannot imply false
        precision. No naive regression CI band is drawn (it would be a razor
        sliver that silently contradicts the locked block-bootstrap CI).
    """
    sasa = np.concatenate([gate[r]["sasa"] for r in RUNS])
    ang  = np.concatenate([gate[r]["angle"] for r in RUNS])
    n = sasa.size
    r_pooled = np.corrcoef(sasa, ang)[0, 1]

    fig = plt.figure(figsize=(double_width, 4.7))
    gs = gridspec.GridSpec(
        2, 2, figure=fig,
        width_ratios=[4.2, 1.0], height_ratios=[1.0, 4.2],
        wspace=0.04, hspace=0.04)
    ax = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax)
    ax_rt  = fig.add_subplot(gs[1, 1], sharey=ax)

    # main joint density
    hb = ax.hexbin(sasa, ang, gridsize=42, cmap="Blues", mincnt=1,
                   linewidths=0.15, edgecolors="white")

    # documented gate-open criterion region — literally empty (0 / 8006 frames).
    # Color role: "summary_ink" (inferential marker), never a data-category hue
    # — this must not read as the same thing as a replica color elsewhere in
    # the figure set.
    n_gate = int(((sasa >= GATE_SASA_THR) & (ang <= GATE_ANGLE_THR)).sum())
    xr = sasa.max() + 0.4
    ax.add_patch(Rectangle(
        (GATE_SASA_THR, 0), xr - GATE_SASA_THR, GATE_ANGLE_THR,
        facecolor=COLORS["summary_ink"], alpha=0.08,
        edgecolor=COLORS["summary_ink"], lw=1.1, ls=(0, (4, 2)), zorder=4))
    ax.annotate(
        f"gate-open criterion: {n_gate}/{sasa.size:,} frames",
        xy=(GATE_SASA_THR + 0.15, GATE_ANGLE_THR),
        xytext=(GATE_SASA_THR - 4.3, GATE_ANGLE_THR + 16),
        fontsize=7.0, color=COLORS["summary_ink"], ha="left",
        arrowprops=dict(arrowstyle="->", color=COLORS["summary_ink"], lw=0.9))

    # binned-mean overlay — the null-legibility device.
    # NB: no per-bin error bars — theta's integrated autocorrelation is ~50
    # frames (~25 ns), so frame-level bars would imply false precision. The
    # rigorous uncertainty (r, CI, Neff) belongs in the caption, not stamped
    # on the plot — this is a purely descriptive "is the trend flat?" guide,
    # labelled directly on the line rather than boxed in a corner.
    edges = np.quantile(sasa, np.linspace(0, 1, 7))
    edges[-1] += 1e-6
    idx = np.digitize(sasa, edges) - 1
    xs = np.array([sasa[idx == b].mean() for b in range(6)])
    ys = np.array([ang[idx == b].mean() for b in range(6)])
    ax.axhline(90, color=COLORS["neutral_light"], lw=0.8, ls=":", zorder=2)
    ax.plot(xs, ys, "o-", color=COLORS["summary_ink"],
            mfc="white", mec=COLORS["summary_ink"], mew=1.4, ms=6,
            lw=1.8, zorder=5)
    # Plain text in open space (sparse region, y>150) rather than tied to the
    # last marker — anchoring to a data point near the right edge clipped
    # against the axes boundary once the string got long.
    ax.text(0.045, 0.955,
            r"mean $\theta$ per SASA sextile   ($r = +0.006$)",
            transform=ax.transAxes, fontsize=7.4,
            color=COLORS["summary_ink"], va="top", ha="left")

    ax.set_xlabel(r"Hydrophobic-residue SASA (nm$^2$)")
    ax.set_ylabel(r"Calyx orientation angle $\theta$ (deg)")
    ax.set_ylim(0, 180)
    ax.set_yticks([0, 45, 90, 135, 180])

    # marginal histograms — neutral grey: these show sampling coverage, not
    # a data category, so they deliberately stay off the categorical-hue
    # family used for replica identity elsewhere in the figure set.
    ax_top.hist(sasa, bins=60, color=COLORS["neutral_light"], alpha=0.9,
                edgecolor="white", linewidth=0.2)
    ax_rt.hist(ang, bins=60, orientation="horizontal",
               color=COLORS["neutral_light"], alpha=0.9,
               edgecolor="white", linewidth=0.2)
    # NB: do NOT call set_xticks([])/set_yticks([]) here — locators are shared
    # with the main axis, so that would wipe the main panel's tick numbers.
    for a in (ax_top, ax_rt):
        a.tick_params(which="both", bottom=False, left=False, top=False,
                      right=False, labelbottom=False, labelleft=False,
                      labeltop=False, labelright=False)
        for s in a.spines.values():
            s.set_visible(False)
    ax.tick_params(which="both", top=False, right=False)

    # No in-figure title, no boxed stat card, no legend — the caption carries
    # r / CI / Neff; the plot carries only what a reader needs to see the
    # flatness directly (see paper-figure skill: "no title inside figures").

    cax = fig.add_axes([0.905, 0.10, 0.014, 0.30])
    cb = fig.colorbar(hb, cax=cax)
    cb.set_label("frames per bin", fontsize=7.2)
    cb.ax.tick_params(labelsize=6.5)

    _save(fig, "FIG1_null_correlation")
    return r_pooled, n


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — structural stability montage
# ─────────────────────────────────────────────────────────────────────────────
def fig2_structural_stability(gate):
    rg = np.load(ANA_DIR / "blg_rg_CENTER.npz")
    cx = np.load(ANA_DIR / "blg_calyx_sasa_CENTER.npz")
    ds = np.load(ANA_DIR / "blg_dssp_CENTER.npz")

    fig, axes = plt.subplots(2, 2, figsize=(double_width, 5.0))
    (axA, axB), (axC, axD) = axes

    def band(ax, t, y, color, label, sem_nb=5):
        ax.plot(t, y, color=color, lw=0.5, alpha=0.30, zorder=1)
        ax.plot(t, smooth_sg(y, 51, 3), color=color, lw=1.4, zorder=3,
                label=label)
        m = y.mean(); sd = y.std()
        ax.axhline(m, color=INK, lw=0.8, ls="--", alpha=0.7, zorder=2)
        ax.fill_between(t, m - sd, m + sd, color=color, alpha=0.10, zorder=0)
        return m, sd

    # (A) radius of gyration — CENTER; annotate the drawn-data statistics
    t = rg["time_ns"]; y = rg["rg_nm"]
    m, sd = band(axA, t, y, COLORS["rg"], "Rg (CENTER)")
    # block SEM (nb=5) on the drawn series
    yb = y[:len(y) // 5 * 5].reshape(5, -1).mean(1)
    sem = yb.std(ddof=1) / np.sqrt(5)
    axA.set_ylabel(r"Radius of gyration (nm)")
    axA.set_ylim(m - 0.11, m + 0.11)
    axA.text(0.035, 0.93,
             rf"$\langle R_g\rangle = {m:.3f}$ nm"
             rf"  (SEM {sem:.3f}, SD {sd:.3f})""\n""globally compact — no unfolding",
             transform=axA.transAxes, va="top", fontsize=7.6, color=INK,
             linespacing=1.4)

    # (B) calyx-region SASA — stays open
    t = cx["time_ns"]; y = cx["calyx_sasa_nm2"]
    m, sd = band(axB, t, y, COLORS["calyx"], "Calyx SASA (CENTER)")
    axB.set_ylabel(r"Calyx-region SASA (nm$^2$)")
    axB.text(0.035, 0.93,
             rf"$\langle \mathrm{{SASA}}_{{calyx}}\rangle = {m:.2f} \pm {sd:.2f}$ nm$^2$"
             "\n""hydrophobic pocket stays accessible",
             transform=axB.transAxes, va="top", fontsize=7.6, color=INK,
             linespacing=1.4)

    # (C) total protein SASA — all four replicas (pooled null backdrop)
    for r in RUNS:
        g = gate[r]
        axC.plot(g["time"], smooth_sg(g["sasa"], 41, 3),
                 color=RUN_COLOR[r], lw=1.0, alpha=0.9, label=RUN_LABEL[r])
    all_sasa = np.concatenate([gate[r]["sasa"] for r in RUNS])
    axC.set_ylabel(r"Hydrophobic-residue SASA (nm$^2$)")
    axC.set_xlabel("Time (ns)")
    axC.text(0.035, 0.93,
             rf"range 24–37 nm$^2$ · $\langle \mathrm{{SASA}} \rangle$ = {all_sasa.mean():.1f} nm$^2$"
             "\n""(PBC-corrected; the artifact gave 45–62)",
             transform=axC.transAxes, va="top", fontsize=7.6, color=INK,
             linespacing=1.4)
    _soft_legend(axC, ncol=2, fontsize=6.6, loc="lower right",
                 handlelength=1.4, columnspacing=1.0)

    # (D) secondary structure fractions over time.
    # Color role: DSSP composition is an ordered/compositional variable, not
    # a replica identity, so it gets its own palette (accent + two neutrals)
    # instead of reusing "beta"/"helix" — those hues already mean "Replica 3"
    # and "Replica 1" elsewhere in this figure set.
    t = ds["time_ns"]
    axD.plot(t, 100 * ds["frac_coil"], color=COLORS["neutral_light"], lw=1.1,
             label=f"coil  {100*float(ds['mean_coil']):.1f}%")
    axD.plot(t, 100 * ds["frac_sheet"], color=COLORS["neutral_dark"], lw=1.1,
             label=f"β-sheet  {100*float(ds['mean_sheet']):.1f}%")
    axD.plot(t, 100 * ds["frac_helix"], color=COLORS["dssp_accent"], lw=1.3,
             label=f"helix  {100*float(ds['mean_helix']):.1f}%")
    axD.set_ylabel("Secondary structure (%)")
    axD.set_xlabel("Time (ns)")
    axD.set_ylim(0, 65)
    _soft_legend(axD, fontsize=6.9, loc="center right", handlelength=1.4)
    axD.text(0.035, 0.93, "native β-fold preserved",
             transform=axD.transAxes, va="top", fontsize=7.6, color=INK)

    for ax, tag in zip([axA, axB, axC, axD], "abcd"):
        ax.set_xlim(left=0)
        ax.text(-0.16, 1.02, f"({tag})", transform=ax.transAxes,
                fontsize=10, fontweight="bold", va="bottom", ha="left")
    axA.set_xlabel("Time (ns)")
    axB.set_xlabel("Time (ns)")

    fig.tight_layout(w_pad=2.2, h_pad=1.8)
    _save(fig, "FIG2_structural_stability")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 3 — contact without commitment
# ─────────────────────────────────────────────────────────────────────────────
def fig3_contact_no_commit(gate):
    """Min protein->interface distance, four replicas as small multiples.

    Same 0.3 nm contact threshold that DEFINES the 613 locked events.  Hundreds
    of transient dips touch/cross the threshold; none deepen into a committed,
    progressively-adsorbing state — the visual embodiment of the paper title.
    """
    fig, axes = plt.subplots(4, 1, figsize=(double_width, 5.4), sharex=True)

    for ax, r in zip(axes, RUNS):
        g = gate[r]
        t, d = g["time"], g["min_dist"]
        # Contact-zone shading is a reference region, not a data category —
        # summary_ink keeps it out of the replica-color family (R1's own
        # trace already uses this same hue family for identity, elsewhere).
        ax.axhspan(-1, CONTACT_NM, color=COLORS["summary_ink"], alpha=0.06,
                   zorder=0)
        ax.plot(t, d, color=RUN_COLOR[r], lw=0.4, alpha=0.35, zorder=1)
        ax.plot(t, smooth_sg(d, 21, 3), color=RUN_COLOR[r], lw=1.1, zorder=3)
        ax.axhline(CONTACT_NM, color=INK, lw=0.8, ls="--", alpha=0.8, zorder=2)
        ax.set_ylim(-0.6, 1.7)
        ax.set_ylabel("nm", fontsize=8)
        ax.text(0.006, 0.90, RUN_LABEL[r], transform=ax.transAxes,
                va="top", ha="left", fontsize=8.2, color=RUN_COLOR[r],
                fontweight="bold")
        ax.set_xlim(0, 1000)

    axes[-1].set_xlabel("Time (ns)")
    fig.supylabel("Nearest protein atom → interface distance (nm)",
                  fontsize=9, x=0.005)

    handles = [
        Line2D([], [], color=INK, ls="--", lw=0.8,
               label=f"contact threshold ({CONTACT_NM} nm)"),
        Patch(fc=COLORS["summary_ink"], alpha=0.15, label="contact zone"),
    ]
    _soft_legend(axes[0], handles=handles, loc="upper right", fontsize=6.9,
                 ncol=2, handlelength=1.6)

    fig.tight_layout(h_pad=0.5)
    _save(fig, "FIG3_contact_no_commit")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 4 — physical validation (surface tension + density)
# ─────────────────────────────────────────────────────────────────────────────
def fig4_physical_validation():
    st = np.load(ANA_DIR / "blg_surface_tension_CENTER.npz")
    de = np.load(ANA_DIR / "blg_density_CENTER.npz")

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(double_width, 2.9))

    # (A) surface tension — proper block-averaged SEM, NOT the flagged ±38.5
    t = st["time_ns"]; g = st["gamma_mNm"]
    mean = g.mean()
    nb = 5
    gb = g[:len(g) // nb * nb].reshape(nb, -1)
    block_means = gb.mean(1)
    bt = t[:len(t) // nb * nb].reshape(nb, -1).mean(1)

    def _block_sem(x, k):
        xk = x[:len(x) // k * k].reshape(k, -1).mean(1)
        return xk.std(ddof=1) / np.sqrt(k)
    # report the most conservative (largest) block-SEM over several block counts
    sem = max(_block_sem(g, k) for k in (5, 10, 20))

    axA.plot(t, g, color=COLORS["interface"], lw=0.35, alpha=0.20, zorder=1,
             label="instantaneous")
    axA.plot(t, smooth_sg(g, 201, 2), color=COLORS["interface"], lw=1.2,
             zorder=3, label="smoothed")
    # TIP3P literature band (~50–52 mN/m) — reference range, not a data
    # category, so summary_ink rather than a replica/DSSP hue.
    axA.axhspan(50, 52, color=COLORS["summary_ink"], alpha=0.14, zorder=0,
                label="TIP3P literature (50–52)")
    axA.errorbar(bt, block_means, yerr=sem, fmt="s", color=INK,
                 ecolor=INK, ms=4, elinewidth=1.2, capsize=3, zorder=5,
                 label="block means ± SEM")
    axA.axhline(mean, color=INK, lw=1.0, ls="--", alpha=0.8, zorder=4)
    axA.set_xlabel("Time (ns)")
    axA.set_ylabel(r"Surface tension $\gamma$ (mN m$^{-1}$)")
    axA.set_ylim(-40, 140)
    axA.set_xlim(0, 1000)
    axA.text(0.035, 0.955,
             rf"$\gamma = {mean:.1f} \pm {sem:.1f}$ mN m$^{{-1}}$"
             "  — matches real TIP3P water",
             transform=axA.transAxes, va="top", fontsize=7.6, color=INK,
             linespacing=1.4,
             bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="none",
                       alpha=0.82))
    _soft_legend(axA, loc="lower right", fontsize=6.4, handlelength=1.5)
    axA.text(-0.19, 1.02, "(a)", transform=axA.transAxes, fontsize=10,
             fontweight="bold", va="bottom")

    # (B) density profile — twin axis (water ~1005 vs protein ~72.5)
    z = de["z_nm"]; pw = de["water_density"]; pp = de["protein_density"]
    axB.plot(z, pw, color=COLORS["interface"], lw=1.4, label="water")
    axB.set_xlabel("z (nm)")
    axB.set_ylabel(r"Water density (kg m$^{-3}$)", color=COLORS["interface"])
    axB.tick_params(axis="y", labelcolor=COLORS["interface"])
    axB.set_xlim(z.min(), z.max())
    axB.set_ylim(0, 1150)

    axB2 = axB.twinx()
    axB2.fill_between(z, 0, pp, color=COLORS["rg"], alpha=0.30, zorder=0)
    axB2.plot(z, pp, color=COLORS["rg"], lw=1.4, label="protein")
    axB2.set_ylabel(r"Protein density (kg m$^{-3}$)", color=COLORS["rg"])
    axB2.tick_params(axis="y", labelcolor=COLORS["rg"])
    axB2.set_ylim(0, 90)
    zpk = z[pp.argmax()]
    axB.set_ylim(0, 1150)  # headroom reserved below the tallest curve, not above

    axB.text(-0.19, 1.02, "(b)", transform=axB.transAxes, fontsize=10,
             fontweight="bold", va="bottom")

    # merge legends for panel B
    h1, l1 = axB.get_legend_handles_labels()
    h2, l2 = axB2.get_legend_handles_labels()
    _soft_legend(axB, h1 + h2, l1 + l2, loc="upper left", fontsize=6.8,
                 handlelength=1.5)

    fig.tight_layout(w_pad=3.0, rect=(0, 0.09, 1, 1))
    fig.text(0.5, 0.01,
             rf"bulk water 1005 kg m$^{{-3}}$   ·   "
             rf"protein density peak {pp.max():.1f} kg m$^{{-3}}$ at z = {zpk:.2f} nm",
             ha="center", va="bottom", fontsize=8.2, color=MUTED)
    _save(fig, "FIG4_physical_validation")


def main():
    print("Loading cached gate data (4 replicas)…")
    gate = load_gate()
    print("FIG1 — headline null correlation")
    r_pool, n = fig1_null_correlation(gate)
    print(f"    pooled r = {r_pool:+.4f} over {n:,} frames")
    print("FIG2 — structural stability")
    fig2_structural_stability(gate)
    print("FIG3 — contact without commitment")
    fig3_contact_no_commit(gate)
    print("FIG4 — physical validation")
    fig4_physical_validation()
    print(f"\nAll figures written to {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
