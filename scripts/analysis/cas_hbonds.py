"""
cas_hbonds.py
=============
Hydrogen bond counts for three interaction groups, beta-casein.
Mirrors blg_hbonds.py exactly — same groups, same thresholds, same engine.

Groups (Fig 4 comparison table):
  1. protein-protein
  2. protein-water
  3. interface water-water (within 1.5 nm of vacuum interface)

REWRITTEN 2026-08-25 — see blg_hbonds.py's docstring for the full story: the
original MDAnalysis-based version (a) thrashed this 8GB machine's RAM on
CASEIN's ~2x-BLG atom count, never completing in 3 attempts (2 tool-tracked
background runs killed at ~1.5h, one detached run reached 59%/6h48m before
being killed on purpose), and (b) had two real correctness bugs shared with
blg_hbonds.py: MDAnalysis's donor-guesser silently missed the backbone amide
N as a donor (confirmed on BLG; same guesser, same CHARMM36 naming, applies
here), and the protein-water term included uncounted bulk water-water
H-bonding. `gmx hbond` (native GROMACS, topology-based donor/acceptor
identification, ~90s for a full 1000ns/2001-frame BLG CENTER run) fixes both.

Interface water-water stays on MDAnalysis with update_selections=True — a
real dynamic-membership question a static gmx index group can't represent,
and never the bottleneck (kills all happened during protein-water).

beta-casein is an IDP with more exposed backbone — expect higher
protein-water HB count than BLG.

Usage:
    python -u scripts/analysis/cas_hbonds.py [--label CENTER|R1]

Output: results/analysis/cas_hbonds_{label}.npz
  keys: time_ns,
        n_prot_prot, n_prot_water, n_water_interface
        mean_prot_prot, mean_prot_water, mean_water_interface
"""

import argparse
import gc
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import MDAnalysis as mda
from MDAnalysis.analysis.hydrogenbonds.hbond_analysis import HydrogenBondAnalysis
from MDAnalysis.transformations import unwrap as mda_unwrap

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

GMX = str(Path.home() / "opt/gromacs-2020.4/bin/gmx")
OUT = ROOT / "results" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)

STRIDE = 5
GMX_DT_PS = 500
INTERFACE_WINDOW_NM = 1.5

TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_CAS/CENTER/MD1000/md_1000ns_v2.tpr",
        "xtc": [ROOT / "outputs_CAS/CENTER/MD1000/traj_comp.xtc"],
    },
    "R1": {
        "tpr": ROOT / "outputs_CAS/R1/MD1000/md_1000ns_r1_v2.tpr",
        "xtc": [ROOT / "outputs_CAS/R1/MD1000/traj_comp.xtc"],
    },
}


def get_group_index(tpr, group_name):
    result = subprocess.run(
        [GMX, "make_ndx", "-f", str(tpr), "-o", "/dev/null"],
        input="q\n", capture_output=True, text=True,
    )
    for line in (result.stdout + result.stderr).splitlines():
        m = re.match(r"\s*(\d+)\s+(\S+)\s*:", line)
        if m and m.group(2) == group_name:
            return int(m.group(1))
    raise RuntimeError(f"Group '{group_name}' not found in {tpr} — "
                        f"gmx make_ndx output:\n{result.stdout}\n{result.stderr}")


def maybe_concat_xtc(xtc_list, tmpdir):
    if len(xtc_list) == 1:
        return xtc_list[0]
    concat_path = Path(tmpdir) / "concat.xtc"
    cmd = [GMX, "trjcat", "-f", *[str(x) for x in xtc_list], "-o", str(concat_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gmx trjcat failed:\n{result.stderr[-2000:]}")
    return concat_path


def parse_hbond_num_xvg(path):
    times_ps, counts = [], []
    with open(path) as f:
        for line in f:
            if line.startswith(("#", "@")) or not line.strip():
                continue
            parts = line.split()
            times_ps.append(float(parts[0]))
            counts.append(int(float(parts[1])))
    return np.array(times_ps), np.array(counts)


def run_gmx_hbond(tpr, xtc, group1_idx, group2_idx, out_xvg, tmpdir):
    cmd = [GMX, "hbond", "-f", str(xtc), "-s", str(tpr),
           "-dt", str(GMX_DT_PS), "-num", str(out_xvg), "-nobackup"]
    result = subprocess.run(
        cmd, input=f"{group1_idx}\n{group2_idx}\n",
        capture_output=True, text=True, cwd=tmpdir,
    )
    if result.returncode != 0:
        raise RuntimeError(f"gmx hbond failed:\n{result.stderr[-2000:]}")
    return parse_hbond_num_xvg(out_xvg)


def find_interface_z(u):
    water_o = u.select_atoms("resname SOL and (name OH2 OW O)")
    u.trajectory[0]
    return np.percentile(water_o.positions[:, 2], 98)


def run_interface_water_hbonds(tpr, xtc_list, n_sampled_expected):
    u = mda.Universe(str(tpr), *[str(x) for x in xtc_list])
    u.trajectory.add_transformations(mda_unwrap(u.atoms))
    n_frames = u.trajectory.n_frames
    interface_z_A = find_interface_z(u)
    print(f"  Interface Z ~ {interface_z_A/10:.2f} nm")

    iz_sel = (f"resname SOL and name OH2 OW O and "
              f"prop z > {interface_z_A - INTERFACE_WINDOW_NM*10:.2f} and "
              f"prop z < {interface_z_A + 5:.2f}")
    print(f"  Running interface water-water HBond analysis (MDAnalysis, dynamic) ...")
    hba_ww = HydrogenBondAnalysis(
        u, donors_sel=iz_sel, acceptors_sel=iz_sel,
        d_a_cutoff=3.5, d_h_a_angle_cutoff=150, update_selections=True,
    )
    hba_ww.run(step=STRIDE, verbose=True)

    sampled_frames = range(0, n_frames, STRIDE)
    times_ns = np.array([u.trajectory[i].time for i in sampled_frames]) / 1000.0
    n_sampled = len(times_ns)

    counts = np.zeros(n_sampled, dtype=int)
    result = hba_ww.results.hbonds
    if len(result) > 0:
        frame_col = result[:, 0].astype(int)
        unique, cnts = np.unique(frame_col, return_counts=True)
        idx = unique // STRIDE
        for i, c in zip(idx, cnts):
            if i < n_sampled:
                counts[i] = c

    del u, hba_ww
    gc.collect()
    return times_ns, counts


def analyse_label(label):
    cfg = TRAJS[label]
    tpr = cfg["tpr"]
    xtc_list = [p for p in cfg["xtc"] if p.exists()]

    if not tpr.exists():
        print(f"[SKIP] {label}: tpr not found")
        return
    if not xtc_list:
        print(f"[SKIP] {label}: no xtc files found")
        return

    out_npz = OUT / f"cas_hbonds_{label}.npz"
    if out_npz.exists():
        print(f"[CACHED] {label}: {out_npz.name} — skipping")
        return

    print(f"\n=== {label} ===")

    protein_idx = get_group_index(tpr, "Protein")
    sol_idx = get_group_index(tpr, "SOL")
    print(f"  Groups: Protein={protein_idx}  SOL={sol_idx}")

    with tempfile.TemporaryDirectory() as tmpdir:
        xtc = maybe_concat_xtc(xtc_list, tmpdir)

        print("  Running protein-protein HBond analysis (gmx hbond) ...")
        t_pp_ps, n_pp = run_gmx_hbond(tpr, xtc, protein_idx, protein_idx,
                                       Path(tmpdir) / "pp.xvg", tmpdir)

        print("  Running protein-water HBond analysis (gmx hbond) ...")
        t_pw_ps, n_pw = run_gmx_hbond(tpr, xtc, protein_idx, sol_idx,
                                       Path(tmpdir) / "pw.xvg", tmpdir)

    times_ns_ww, n_ww = run_interface_water_hbonds(tpr, xtc_list, len(t_pp_ps))

    times_ns = t_pp_ps / 1000.0
    n_frames_common = min(len(times_ns), len(n_pw), len(n_ww))
    times_ns = times_ns[:n_frames_common]
    n_pp = n_pp[:n_frames_common]
    n_pw = n_pw[:n_frames_common]
    n_ww = n_ww[:n_frames_common]

    print(f"\n  Mean HBond counts:")
    print(f"    Protein-protein:   {n_pp.mean():.1f} +/- {n_pp.std():.1f}")
    print(f"    Protein-water:     {n_pw.mean():.1f} +/- {n_pw.std():.1f}")
    print(f"    Interface H2O-H2O: {n_ww.mean():.1f} +/- {n_ww.std():.1f}")

    np.savez(
        out_npz,
        time_ns=times_ns,
        n_prot_prot=n_pp,
        n_prot_water=n_pw,
        n_water_interface=n_ww,
        mean_prot_prot=n_pp.mean(),
        mean_prot_water=n_pw.mean(),
        mean_water_interface=n_ww.mean(),
    )
    print(f"  Saved: {out_npz.name}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default="CENTER", choices=list(TRAJS))
    args = ap.parse_args()
    analyse_label(args.label)


if __name__ == "__main__":
    main()
