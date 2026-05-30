"""
run_r1_interim.py
==================
Run Z-position, RMSD, and SASA analysis on R1's
extended trajectory (0–650 ns: original 500 ns + AMD extension).

Output labels:  REPLICA_1_649ns_*
Output dir:     results/figures/{z_position,rmsd,sasa}/

Usage (from MILK_FROTHING root):
    source ~/research-env/bin/activate
    python scripts/run_r1_interim.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

TPR = ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr"
XTC = ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_r1_649ns.xtc"
LABEL = "REPLICA_1_649ns"

FIG = ROOT / "results" / "figures"
(FIG / "z_position").mkdir(parents=True, exist_ok=True)
(FIG / "rmsd").mkdir(parents=True, exist_ok=True)
(FIG / "sasa").mkdir(parents=True, exist_ok=True)

if not TPR.exists():
    sys.exit(f"TPR not found: {TPR}")
if not XTC.exists():
    sys.exit(f"XTC not found: {XTC}")

print(f"TPR : {TPR}")
print(f"XTC : {XTC}")
print(f"Label: {LABEL}\n")

# ── Z-position ────────────────────────────────────────────────────────────────
print("=" * 55)
print("  Z-POSITION")
print("=" * 55)
import track_z_position as tz
tz.TPR_FILE   = str(TPR)
tz.XTC_FILE   = str(XTC)
tz.OUTPUT_PNG = str(FIG / "z_position" / f"{LABEL}_z_position.png")
tz.STRIDE     = 1
u = tz.load_universe()
times, z_prot, z_upper, z_lower = tz.analyze(u)
tz.print_summary(times, z_prot, z_upper, z_lower)
tz.plot(times, z_prot, z_upper, z_lower)

# ── RMSD ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  RMSD")
print("=" * 55)
import rmsd_analysis as ra
ra.TPR_FILE   = str(TPR)
ra.XTC_FILE   = str(XTC)
ra.OUTPUT_PNG = str(FIG / "rmsd" / f"{LABEL}_rmsd.png")
u_rmsd = ra.load_universe()
results = ra.analyze(u_rmsd)
ra.print_summary(results)
ra.plot(results)

# ── SASA ──────────────────────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  SASA")
print("=" * 55)
import sasa_analysis as sa
sa.TPR_FILE   = str(TPR)
sa.XTC_FILE   = str(XTC)
sa.OUTPUT_PNG = str(FIG / "sasa" / f"{LABEL}_sasa.png")
u_sasa = sa.load_universe()
times_s, total, hydrophob, hydrophil, calyx = sa.analyze(u_sasa)
sa.print_summary(times_s, total, hydrophob, hydrophil, calyx)
sa.plot(times_s, total, hydrophob, hydrophil, calyx)

print(f"\nDone. Figures in:\n  {FIG}")
