"""
scripts/figures/utils.py
=========================
Shared, species-parameterized figure infrastructure for the BLG vs β-casein
comparative figure set (Figs 2-4, per docs/paper1_expansion_plan.md). Sits on
top of plot_style.py — imports its rcParams/palette/save helpers rather than
duplicating them. Existing single-species scripts (blg_fig2_contact.py etc.)
are untouched; new comparative figure scripts should build on this instead of
re-deriving the loader/legend boilerplate each currently repeats (see
blg_fig_publication_2026-07.py:48-53 for the pattern this factors out).

Two problems this solves:
  1. A comparative BLG+CAS figure needs both species' cached results loaded
     the same way. Write that loader once, here.
  2. CAS has no trajectory data yet (production running on the cluster,
     ~14 days out as of 2026-08-08). Figure code written against this module
     can be built and tested against BLG now, and will pick up CAS the
     moment its .npz files land — available() reports what's actually on
     disk so a script can render a CAS panel as "pending" instead of
     crashing on a missing file or, worse, silently omitting the panel.

Color convention (extends, does not replace, the rule already documented in
plot_style.COLORS): hue = replica ROLE (center/replica1/replica2/replica3),
meaning the same thing in both species — CAS only ever populates the first
two. Species identity is carried by linestyle + marker instead, so a reader
never has to hold two independent color keys in their head when BLG and CAS
series share one legend.
"""

from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from plot_style import COLORS  # noqa: E402

GATE_DIR = ROOT / "results" / "gate_analysis"
ANA_DIR = ROOT / "results" / "analysis"

INK = "#222222"    # near-black, matches blg_fig_publication_2026-07.py
MUTED = "#8A8A8A"   # secondary/pending annotation grey, same source

# ── per-species configuration ────────────────────────────────────────────────
SPECIES = {
    "BLG": dict(
        display="β-Lactoglobulin",
        short="BLG",
        replicas=["CENTER", "R1", "R2", "R3"],
        has_gate=True,          # results/gate_analysis/{run}_gate.npz exists
        analysis_prefix="blg",
        linestyle="-",
        marker="o",
    ),
    "CAS": dict(
        display="β-Casein",
        short="CAS",
        replicas=["CENTER", "R1"],   # 2 replicas only — locked decision, saves cluster time
        has_gate=False,         # no gate/contact pipeline defined for CAS (yet)
        analysis_prefix="cas",
        linestyle="--",
        marker="s",
    ),
}

_RUN_COLOR = {
    "CENTER": COLORS["center"],
    "R1": COLORS["replica1"],
    "R2": COLORS["replica2"],
    "R3": COLORS["replica3"],
}


def run_color(run):
    """Color for a replica ROLE (CENTER/R1/R2/R3) — shared across species."""
    return _RUN_COLOR[run]


def run_label(species, run):
    tag = "CENTER" if run == "CENTER" else f"Replica {run[1:]}"
    return f"{SPECIES[species]['short']} {tag}"


def _analysis_path(species, kind, run):
    prefix = SPECIES[species]["analysis_prefix"]
    return ANA_DIR / f"{prefix}_{kind}_{run}.npz"


def available(species, kind):
    """Which replicas of `kind` (e.g. 'density', 'rg', 'surface_tension')
    actually have cached output on disk right now, for this species."""
    cfg = SPECIES[species]
    return [r for r in cfg["replicas"] if _analysis_path(species, kind, r).exists()]


def load_analysis(species, kind, run):
    """Load one cached results/analysis/{prefix}_{kind}_{run}.npz file."""
    path = _analysis_path(species, kind, run)
    if not path.exists():
        raise FileNotFoundError(
            f"{path.relative_to(ROOT)} not found — {species}/{run}/{kind} "
            f"not computed yet. Check available('{species}', '{kind}') first."
        )
    return dict(np.load(path))


def load_gate(species, run):
    """Load one results/gate_analysis/{run}_gate.npz — BLG only; CAS has no
    gate/contact pipeline defined (see docs/paper1_expansion_plan.md)."""
    cfg = SPECIES[species]
    if not cfg["has_gate"]:
        raise NotImplementedError(f"{species} has no gate_analysis pipeline")
    path = GATE_DIR / f"{run}_gate.npz"
    if not path.exists():
        raise FileNotFoundError(f"{path.relative_to(ROOT)} not found")
    return dict(np.load(path))


def replica_legend_handles(species, runs=None):
    """Line2D handles for a species' replicas, consistent across figures."""
    from matplotlib.lines import Line2D
    cfg = SPECIES[species]
    runs = runs or cfg["replicas"]
    return [
        Line2D([0], [0], color=run_color(r), lw=1.6, ls=cfg["linestyle"],
               marker=cfg["marker"], markersize=4, label=run_label(species, r))
        for r in runs
    ]


def species_style_legend():
    """Handles explaining the solid=BLG / dashed=CAS convention — add once
    per multi-panel comparative figure (e.g. via a shared fig.legend call)."""
    from matplotlib.lines import Line2D
    return [
        Line2D([0], [0], color=INK, lw=1.6, ls=cfg["linestyle"],
               marker=cfg["marker"], markersize=4, label=cfg["display"])
        for cfg in SPECIES.values()
    ]


def pending_panel(ax, species, note=None):
    """Render a 'data pending' placeholder panel — for comparative figures
    built before CAS production finishes. Keeps the figure's layout stable
    now and obviously-not-final, instead of silently dropping the panel."""
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    msg = note or f"{SPECIES[species]['display']}\ndata pending"
    ax.text(0.5, 0.5, msg, ha="center", va="center", fontsize=8,
            color=MUTED, style="italic", transform=ax.transAxes)


if __name__ == "__main__":
    # Smoke test / at-a-glance status — what does this module actually see
    # on disk right now, for each species, across the analyses P.P.'s figure
    # plan (docs/paper1_expansion_plan.md) needs.
    kinds = ["density", "rg", "dssp", "surface_tension", "calyx_sasa",
             "hbonds", "pca_structural", "cluster_contact", "contact",
             "nterm_sasa"]
    for species in SPECIES:
        print(f"\n{species} ({SPECIES[species]['display']}):")
        for kind in kinds:
            runs = available(species, kind)
            status = ", ".join(runs) if runs else "—"
            print(f"  {kind:16s} {status}")
        if SPECIES[species]["has_gate"]:
            gate_runs = [r for r in SPECIES[species]["replicas"]
                         if (GATE_DIR / f"{r}_gate.npz").exists()]
            print(f"  {'gate':16s} {', '.join(gate_runs) or '—'}")
