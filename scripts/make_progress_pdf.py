"""Quick progress PDF for P.P. — BLG CENTER validation results (June 2026)."""
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "results/figures/blg_fig_hbonds_CENTER.png"
OUT = ROOT / "progress-reports/BLG_CENTER_validation_progress.pdf"

rows = [
    ["#", "Result", "Number"],
    ["1", "HBonds (+ figure)", "prot-prot 589±25, prot-water 40,831±120,\ninterface H2O-H2O 9,540±328"],
    ["2", "PCA (structural)", "PC1 35.1%, PC2 13.4%"],
    ["3", "Cluster (contact frames)", "1 dominant cluster, 220/304 frames (72%)"],
    ["4", "DSSP", "Helix 11.8% / Sheet 36.7% / Coil 51.5%"],
    ["5", "Surface tension", "γ = 51.9 ± 38.5 mN/m"],
    ["6", "Density profile", "Water bulk 1005 kg/m3, protein peak 72.5 kg/m3 @ z=1.76 nm"],
    ["7", "Rg", "1.504 ± 0.022 nm (CENTER)"],
    ["8", "Calyx SASA", "3.81 ± 0.46 nm2 (CENTER only)"],
]

fig = plt.figure(figsize=(8.5, 14))
fig.suptitle("BLG CENTER Validation — Progress Summary (June 2026)", fontsize=13, y=0.995)

# Row 1: existing hbonds timeseries figure
ax_img = fig.add_axes([0.05, 0.70, 0.9, 0.27])
ax_img.imshow(mpimg.imread(FIG))
ax_img.axis("off")
ax_img.set_title("1. HBond counts, CENTER (1000 ns)", fontsize=9)

# Row 2: four scalar-summary panels (results 2-8, grouped by comparable unit)
ax_dssp = fig.add_axes([0.07, 0.55, 0.20, 0.12])
dssp_labels, dssp_vals = ["Helix", "Sheet", "Coil"], [11.8, 36.7, 51.5]
ax_dssp.bar(dssp_labels, dssp_vals, color=["#4477AA", "#CC6677", "#888888"])
ax_dssp.set_ylabel("%")
ax_dssp.set_title("4. DSSP", fontsize=9)

ax_pca = fig.add_axes([0.33, 0.55, 0.18, 0.12])
ax_pca.bar(["PC1", "PC2"], [35.1, 13.4], color="#228833")
ax_pca.set_ylabel("Variance %")
ax_pca.set_title("2. PCA", fontsize=9)

ax_clu = fig.add_axes([0.56, 0.55, 0.18, 0.12])
ax_clu.bar(["Dominant", "Other"], [72, 28], color=["#EE6677", "#BBBBBB"])
ax_clu.set_ylabel("% frames")
ax_clu.set_title("3. Cluster", fontsize=9)

ax_dens = fig.add_axes([0.79, 0.55, 0.18, 0.12])
ax_dens.bar(["Water bulk", "Protein peak"], [1005, 72.5], color=["#66CCEE", "#AA3377"])
ax_dens.set_ylabel("kg/m3")
ax_dens.set_title("6. Density", fontsize=8)
ax_dens.tick_params(axis="x", labelsize=6)

# Row 3: three independent scalar bars with error bars (different units, kept separate)
ax_rg = fig.add_axes([0.07, 0.40, 0.18, 0.12])
ax_rg.bar(["Rg"], [1.504], yerr=[0.022], capsize=4, color="#4477AA")
ax_rg.set_ylabel("nm")
ax_rg.set_title("7. Rg", fontsize=9)

ax_sasa = fig.add_axes([0.33, 0.40, 0.18, 0.12])
ax_sasa.bar(["Calyx SASA"], [3.81], yerr=[0.46], capsize=4, color="#CCBB44")
ax_sasa.set_ylabel("nm2")
ax_sasa.set_title("8. Calyx SASA", fontsize=9)

ax_gamma = fig.add_axes([0.59, 0.40, 0.18, 0.12])
ax_gamma.bar(["Surface\ntension"], [51.9], yerr=[38.5], capsize=4, color="#AA3377")
ax_gamma.set_ylabel("mN/m")
ax_gamma.set_title("5. Surface tension", fontsize=8)

# Table at bottom
ax_tab = fig.add_axes([0.05, 0.02, 0.9, 0.33])
ax_tab.axis("off")
table = ax_tab.table(cellText=rows, loc="center", cellLoc="left", colWidths=[0.05, 0.28, 0.67])
table.auto_set_font_size(False)
table.set_fontsize(8)
table.scale(1, 2.0)
for (r, c), cell in table.get_celld().items():
    if r == 0:
        cell.set_text_props(weight="bold")

OUT.parent.mkdir(exist_ok=True)
fig.savefig(OUT)
print(f"Saved {OUT}")
