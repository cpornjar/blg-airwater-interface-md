"""
run_replica_analysis.py
========================
Runs track_z_position, rmsd_analysis, and sasa_analysis
across all 3 Plan-B replicas and the CENTER 1000ns run.

Outputs go to results/figures/ and results/summaries/.

Usage:
    python scripts/run_replica_analysis.py
    python scripts/run_replica_analysis.py --only-z       # Z-position only
    python scripts/run_replica_analysis.py --replica 1    # single replica

Run from MILK_FROTHING root.
"""

import argparse
import importlib.util
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_FIG = ROOT / "results" / "figures"
RESULTS_SUM = ROOT / "results" / "summaries"

RUNS = {
    "CENTER_1000ns": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc",
    },
    "REPLICA_1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
    },
    "REPLICA_2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
    },
    "REPLICA_3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3.tpr",
        "xtc": ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
    },
}


def load_script(name):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    return spec, mod


def run_z_position(label, tpr, xtc):
    import track_z_position as tz
    tz.TPR_FILE   = str(tpr)
    tz.XTC_FILE   = str(xtc)
    tz.OUTPUT_PNG = str(RESULTS_FIG / "z_position" / f"{label}_z_position.png")
    tz.STRIDE     = 1

    print(f"\n{'='*55}")
    print(f"  Z-POSITION: {label}")
    print(f"{'='*55}")
    u = tz.load_universe()
    times, z_prot, z_upper, z_lower = tz.analyze(u)
    tz.print_summary(times, z_prot, z_upper, z_lower)
    tz.plot(times, z_prot, z_upper, z_lower)


def run_rmsd(label, tpr, xtc):
    import rmsd_analysis as ra
    ra.TPR_FILE   = str(tpr)
    ra.XTC_FILE   = str(xtc)
    ra.OUTPUT_PNG = str(RESULTS_FIG / "rmsd" / f"{label}_rmsd.png")

    print(f"\n{'='*55}")
    print(f"  RMSD: {label}")
    print(f"{'='*55}")
    ra.main()


def run_sasa(label, tpr, xtc):
    import sasa_analysis as sa
    sa.TPR_FILE   = str(tpr)
    sa.XTC_FILE   = str(xtc)
    sa.OUTPUT_PNG = str(RESULTS_FIG / "sasa" / f"{label}_sasa.png")

    print(f"\n{'='*55}")
    print(f"  SASA: {label}")
    print(f"{'='*55}")
    sa.main()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only-z",   action="store_true", help="Run Z-position only")
    parser.add_argument("--only-rmsd",action="store_true", help="Run RMSD only")
    parser.add_argument("--only-sasa",action="store_true", help="Run SASA only")
    parser.add_argument("--replica",  type=str, default=None,
                        help="Run single target: 1, 2, 3, or center")
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT / "scripts"))

    targets = {}
    if args.replica:
        key = "CENTER_1000ns" if args.replica.lower() == "center" else f"REPLICA_{args.replica}"
        targets = {key: RUNS[key]}
    else:
        targets = RUNS

    do_z    = not (args.only_rmsd or args.only_sasa)
    do_rmsd = not (args.only_z    or args.only_sasa)
    do_sasa = not (args.only_z    or args.only_rmsd)

    for label, paths in targets.items():
        tpr, xtc = paths["tpr"], paths["xtc"]
        if not tpr.exists() or not xtc.exists():
            print(f"[SKIP] {label} — files not found")
            continue

        if do_z:
            run_z_position(label, tpr, xtc)
        if do_rmsd:
            try:
                run_rmsd(label, tpr, xtc)
            except Exception as e:
                print(f"[WARN] RMSD failed for {label}: {e}")
        if do_sasa:
            try:
                run_sasa(label, tpr, xtc)
            except Exception as e:
                print(f"[WARN] SASA failed for {label}: {e}")

    print(f"\nAll done. Results in:\n  {RESULTS_FIG}\n  {RESULTS_SUM}")


if __name__ == "__main__":
    main()
