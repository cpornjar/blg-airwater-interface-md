"""
make_benchmark_report.py
========================
Generate a benchmark comparison PDF/PNG:
  NVIDIA RTX 5090 (CUDA) vs AMD gfx1201 (HIP) vs CPU-only
  Rocky 9, GROMACS 2026.1, BLG solvated system (~100k atoms)

Output: results/bench_report/BENCHMARK_REPORT.pdf / .png
Usage:
    python scripts/make_benchmark_report.py --cpu-ns-day 1.424
"""

import argparse
import sys
from pathlib import Path
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import numpy as np

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "results" / "bench_report"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = OUT_DIR / "BENCHMARK_REPORT.png"
OUT_PDF = OUT_DIR / "BENCHMARK_REPORT.pdf"

BENCHMARKS = [
    {
        "short":    "CPU only",
        "sublabel": "Intel Xeon W-2245 @ 3.90 GHz\n16 threads (OpenMP)",
        "accel":    "None",
        "ns_day":   None,
        "color":    "#95A5A6",
        "dark":     "#717D7E",
    },
    {
        "short":    "AMD GPU (HIP)",
        "sublabel": "AMD Radeon RX 9070 XT\ngfx1201, RDNA4, 16 GB VRAM",
        "accel":    "HIP",
        "ns_day":   53.9,
        "color":    "#E74C3C",
        "dark":     "#C0392B",
    },
    {
        "short":    "NVIDIA GPU (CUDA)",
        "sublabel": "NVIDIA GeForce RTX 5090\nBlackwell, 32 GB VRAM",
        "accel":    "CUDA",
        "ns_day":   517.8,
        "color":    "#2E86AB",
        "dark":     "#1A5276",
    },
]

DATE_STR = date.today().strftime("%B %d, %Y")
FOOTER1  = "Rocky Linux 9  ·  GROMACS 2026.1  ·  KU HPC Cluster  ·  Same TPR for all runs"
FOOTER2  = "System: β-lactoglobulin + TIP3P water + Na⁺/Cl⁻  (~100,000 atoms, NPT, PME electrostatics)"


def make_figure(cpu_ns_day: float):
    BENCHMARKS[0]["ns_day"] = cpu_ns_day
    ns_days  = [b["ns_day"] for b in BENCHMARKS]
    speedups = [v / cpu_ns_day for v in ns_days]
    colors   = [b["color"]  for b in BENCHMARKS]
    darks    = [b["dark"]   for b in BENCHMARKS]
    n = len(BENCHMARKS)

    fig = plt.figure(figsize=(13, 9))
    fig.patch.set_facecolor("#FAFAFA")

    gs = gridspec.GridSpec(
        2, 2, figure=fig,
        left=0.07, right=0.97, top=0.91, bottom=0.15,
        hspace=0.52, wspace=0.42,
        height_ratios=[1.0, 1.0],
        width_ratios=[1.1, 0.9],
    )

    # ── Title ─────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.955,
             "GROMACS 2026.1 — GPU vs CPU Performance Benchmark",
             ha="center", fontsize=15, fontweight="bold", color="#1C2833")
    fig.text(0.5, 0.928,
             "β-Lactoglobulin solvated system  ·  Rocky Linux 9  ·  KU HPC",
             ha="center", fontsize=10, color="#555555")

    # ═══════════════════════════════════════════════════════════════════════════
    # (A) Main bar — log scale, full width top row
    # ═══════════════════════════════════════════════════════════════════════════
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_facecolor("white")

    x = np.arange(n)
    bars = ax1.bar(x, ns_days, color=colors, edgecolor=darks,
                   linewidth=1.6, width=0.52, zorder=3)

    ax1.set_yscale("log")
    ax1.set_xlim(-0.55, n - 0.45)
    ax1.set_ylim(0.4, max(ns_days) * 200)
    ax1.set_xticks(x)
    ax1.set_xticklabels(
        [b["short"] for b in BENCHMARKS],
        fontsize=12, fontweight="bold"
    )
    ax1.set_ylabel("Simulation speed (ns / day)", fontsize=11, labelpad=8)
    ax1.set_title("(A)  Raw performance", fontsize=11, fontweight="bold",
                  loc="left", pad=6, color="#2C3E50")
    ax1.grid(axis="y", which="both", alpha=0.18, zorder=0, color="#888888")
    ax1.set_axisbelow(True)
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.tick_params(axis="y", labelsize=9)

    # Annotations: big text badge floating well above each bar
    for i, (bar, val, spd, dk) in enumerate(zip(bars, ns_days, speedups, darks)):
        bx  = bar.get_x() + bar.get_width() / 2
        by  = bar.get_height()

        # Place label at a fixed fraction above bar top (log scale)
        label_y = by * 4.5

        # Main number
        ax1.text(bx, label_y, f"{val:.1f}",
                 ha="center", va="bottom",
                 fontsize=17, fontweight="bold", color=dk, zorder=6)
        # "ns/day" unit
        ax1.text(bx, label_y * 0.98, "ns/day",
                 ha="center", va="top",
                 fontsize=8.5, color="#555555", zorder=6)
        # Speedup badge
        if spd > 1:
            badge_y = label_y * 14
            ax1.text(bx, badge_y,
                     f"{spd:.0f}× faster\nthan CPU",
                     ha="center", va="bottom",
                     fontsize=9, color=dk,
                     bbox=dict(boxstyle="round,pad=0.35", fc=colors[i],
                               ec=dk, alpha=0.18, lw=1.2),
                     zorder=6)

    # Hardware sublabel inside bar (only for tall bars)
    for i, (bar, b) in enumerate(zip(bars, BENCHMARKS)):
        if b["ns_day"] > 10:
            bx = bar.get_x() + bar.get_width() / 2
            ax1.text(bx, b["ns_day"] * 0.55, b["sublabel"],
                     ha="center", va="top",
                     fontsize=7.5, color="white", linespacing=1.4,
                     zorder=7)

    # ═══════════════════════════════════════════════════════════════════════════
    # (B) Horizontal speedup bars
    # ═══════════════════════════════════════════════════════════════════════════
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_facecolor("white")

    y = np.arange(n)
    hbars = ax2.barh(y, speedups, color=colors, edgecolor=darks,
                     linewidth=1.4, height=0.48, zorder=3)
    ax2.set_yticks(y)
    ax2.set_yticklabels([b["short"] for b in BENCHMARKS],
                        fontsize=10.5, fontweight="bold")
    ax2.set_xlabel("Speedup relative to CPU-only (×)", fontsize=10, labelpad=6)
    ax2.set_title("(B)  Speedup over CPU", fontsize=11, fontweight="bold",
                  loc="left", pad=6, color="#2C3E50")
    ax2.set_xlim(0, max(speedups) * 1.28)
    ax2.grid(axis="x", alpha=0.2, zorder=0, color="#888888")
    ax2.set_axisbelow(True)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.tick_params(axis="x", labelsize=9)
    ax2.invert_yaxis()

    for bar, spd, dk in zip(hbars, speedups, darks):
        label = f"  {spd:.0f}×" if spd >= 10 else f"  {spd:.1f}×"
        ax2.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                 label, va="center", fontsize=11, fontweight="bold", color=dk)

    # ═══════════════════════════════════════════════════════════════════════════
    # (C) Hardware details table (manual drawing — avoids matplotlib table bugs)
    # ═══════════════════════════════════════════════════════════════════════════
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_facecolor("white")
    ax3.axis("off")
    ax3.set_title("(C)  Hardware & results", fontsize=11, fontweight="bold",
                  loc="left", pad=6, color="#2C3E50")

    # Manual table via ax3 coordinates (0–1)
    row_h   = 0.215
    col_xs  = [0.0,  0.58, 0.79]
    col_ws  = [0.56, 0.19, 0.21]
    hdr_y   = 0.90
    hdr_h   = 0.095
    gap     = 0.010

    col_headers = ["Hardware", "ns / day", "Speedup"]

    def draw_cell(ax, x, y, w, h, text, fc, tc, fs=9.5, bold=False,
                  halign="left", subtext=None):
        ax.add_patch(mpatches.FancyBboxPatch(
            (x + 0.004, y + 0.006), w - 0.008, h - 0.012,
            boxstyle="round,pad=0.004", fc=fc, ec="#DDDDDD", lw=0.7,
            transform=ax.transAxes, zorder=2
        ))
        tx = x + 0.018 if halign == "left" else x + w / 2
        # anchor main text near top of cell, subtext near bottom
        top_y    = y + h - 0.022
        bottom_y = y + 0.022
        if subtext:
            ax.text(tx, top_y, text,
                    transform=ax.transAxes,
                    ha=halign, va="top",
                    fontsize=fs, fontweight="bold" if bold else "normal",
                    color=tc, zorder=3)
            ax.text(tx, bottom_y, subtext,
                    transform=ax.transAxes,
                    ha=halign, va="bottom",
                    fontsize=7.5, color="#888888", zorder=3)
        else:
            ax.text(tx, y + h / 2, text,
                    transform=ax.transAxes,
                    ha=halign, va="center",
                    fontsize=fs, fontweight="bold" if bold else "normal",
                    color=tc, zorder=3)

    # Header
    for cx, cw, hdr in zip(col_xs, col_ws, col_headers):
        draw_cell(ax3, cx, hdr_y, cw, hdr_h, hdr,
                  fc="#2C3E50", tc="white", fs=9.5, bold=True,
                  halign="center" if hdr != "Hardware" else "left")

    # Short hardware names (line 1) and detail (line 2)
    hw_names = [
        ("CPU only (16 threads)",      "Xeon W-2245 · 3.90 GHz · OpenMP"),
        ("AMD Radeon RX 9070 XT",      "gfx1201 · RDNA4 · 16 GB VRAM · HIP"),
        ("NVIDIA RTX 5090",            "Blackwell · 32 GB VRAM · CUDA"),
    ]

    for ri, (b, (hw_main, hw_sub)) in enumerate(zip(BENCHMARKS, hw_names)):
        ry = hdr_y - (ri + 1) * (row_h + gap)
        row_fc = "#F5F6F7" if ri % 2 == 0 else "white"

        # Color strip
        ax3.add_patch(mpatches.FancyBboxPatch(
            (0.0, ry + 0.006), 0.014, row_h - 0.012,
            boxstyle="square,pad=0.0", fc=b["color"], ec="none",
            transform=ax3.transAxes, zorder=4
        ))

        # Hardware cell (two-line)
        draw_cell(ax3, col_xs[0], ry, col_ws[0], row_h,
                  "   " + hw_main, row_fc, "#1C2833",
                  fs=9, bold=True, halign="left", subtext="   " + hw_sub)

        # ns/day cell
        draw_cell(ax3, col_xs[1], ry, col_ws[1], row_h,
                  f"{b['ns_day']:.1f}", row_fc, b["dark"],
                  fs=12, bold=True, halign="center")

        # Speedup cell
        spd = b["ns_day"] / cpu_ns_day
        draw_cell(ax3, col_xs[2], ry, col_ws[2], row_h,
                  f"{spd:.0f}×", row_fc, b["dark"],
                  fs=12, bold=True, halign="center")

    # ── Footer ────────────────────────────────────────────────────────────────
    fig.text(0.5, 0.072, FOOTER1,
             ha="center", fontsize=8.5, color="#555555", style="italic")
    fig.text(0.5, 0.048, FOOTER2,
             ha="center", fontsize=8, color="#777777", style="italic")
    fig.text(0.97, 0.022, DATE_STR,
             ha="right", fontsize=8, color="#AAAAAA")
    fig.text(0.03, 0.022, "COMFHA · KU HPC",
             ha="left", fontsize=8, color="#AAAAAA")

    return fig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpu-ns-day", type=float, default=None)
    args = parser.parse_args()
    if args.cpu_ns_day is None:
        print("ERROR: --cpu-ns-day required"); sys.exit(1)

    print(f"Building report  CPU={args.cpu_ns_day:.3f} ns/day ...")
    fig = make_figure(args.cpu_ns_day)
    fig.savefig(str(OUT_PDF), dpi=300, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    fig.savefig(str(OUT_PNG), dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)

    cpu = args.cpu_ns_day
    amd = BENCHMARKS[1]["ns_day"]
    nv  = BENCHMARKS[2]["ns_day"]
    print(f"  CPU  : {cpu:.3f} ns/day (1×)")
    print(f"  AMD  : {amd:.1f}  ns/day ({amd/cpu:.0f}×)")
    print(f"  NVID : {nv:.1f}  ns/day ({nv/cpu:.0f}×)")
    print(f"  PDF → {OUT_PDF}")
    print(f"  PNG → {OUT_PNG}")


if __name__ == "__main__":
    main()
