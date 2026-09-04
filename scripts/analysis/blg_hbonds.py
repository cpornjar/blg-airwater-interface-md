"""
blg_hbonds.py
=============
Hydrogen bond counts for three interaction groups, all BLG replicas.

Groups (Fig 4 — quantitative comparison):
  1. protein-protein (self-interaction)
  2. protein-water
  3. interface water-water (within 1.5 nm of vacuum interface)

REWRITTEN 2026-08-25 — was MDAnalysis HydrogenBondAnalysis for all 3 groups;
now uses native `gmx hbond` for protein-protein and protein-water. Two real
problems drove this:

  (a) PERFORMANCE: the MDAnalysis protein-water stage (donors_sel=acceptors_sel
      = "protein or water", the biggest combined selection) was thrashing this
      8GB machine's RAM/swap on the CASEIN system (2x BLG's atom count) —
      degrading from ~15s/frame to ~50s/frame over a run, never completing in
      three attempts (two tool-tracked background runs killed at ~1.5h/32%,
      one detached nohup run reached 59%/6h48m before being killed on purpose
      due to worsening swap thrashing). `gmx hbond` runs the full 1000ns
      CENTER trajectory (2001 frames) in under 90 seconds — a compiled binary,
      not a Python object accumulating results per frame.

  (b) CORRECTNESS BUG in the old protein-protein number: MDAnalysis's
      donors_sel="protein" auto-guesses donor atoms from atom names/geometry,
      and its guesser completely missed the backbone amide nitrogen (CHARMM36
      names it `HN`, or `H1/H2/H3` at the N-terminus) as a donor hydrogen —
      confirmed directly: guessed donors were ONLY side-chain heavy atoms
      (Gln/Asn amide N, Ser/Thr/Tyr OH, Arg guanidinium, Trp indole N — 43
      atoms total), zero backbone N despite 156 backbone N atoms each bonded
      to an amide H. This silently excluded the entire secondary-structure-
      defining backbone H-bond network (what alpha helices and beta sheets
      literally are) from what was labeled "protein-protein H-bonds." The old
      CENTER value (589.1) is NOT trustworthy and should not be cited.
      `gmx hbond`'s topology-based group (real bonded connectivity from the
      .tpr, not name-pattern guessing) correctly finds all 207 protein donors
      including every backbone N, giving 107.3 — physically sane for ~36%
      sheet + ~12% helix over 156 residues.

  There was ALSO a second, separate bug in the old protein-water number:
  donors_sel=acceptors_sel were BOTH the combined "protein or water" set, so
  `n_pw = n_pw_all - n_pp` left protein-water PLUS all bulk water-water
  H-bonding (tens of thousands of pairs in a ~97000-atom water box), not a
  pure cross-term. `gmx hbond` with two DISTINCT groups (Protein, SOL) gives
  the correct cross-term directly — confirmed "all hydrogen bonds between the
  two groups" is direction-agnostic (protein-donor/water-acceptor AND
  water-donor/protein-acceptor both counted), per `gmx hbond -h`.

  Interface water-water is UNCHANGED — still MDAnalysis with
  update_selections=True, because that's a genuine dynamic-membership
  question (which water molecules currently sit in a thin Z-slab, molecules
  diffuse in and out) that a static gmx index group can't represent, and it
  was never the bottleneck (all 3 kill points happened during the
  protein-water stage, before this stage was ever reached).

Cutoffs are physically equivalent, not just coincidentally similar: GROMACS's
default -r 0.35nm / -a 30deg (Hydrogen-Donor-Acceptor deviation from linear)
is the same H-bond definition as MDAnalysis's d_a_cutoff=3.5 / d_h_a_angle_cutoff=150
(Donor-Hydrogen...Acceptor, 150deg minimum = <=30deg deviation from 180deg
linear) — verified by matching the interface-water group's already-locked
methodology.

Usage:
    python -u scripts/analysis/blg_hbonds.py [--label CENTER|R1|R2|R3|all]

Output: results/analysis/blg_hbonds_{label}.npz
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

STRIDE = 5           # every 5 frames of the native 100ps output = 500ps sampling
GMX_DT_PS = 500       # gmx hbond -dt, must match STRIDE * native dt exactly

TRAJS = {
    "CENTER": {
        "tpr": ROOT / "outputs_BLG/CENTER/MD1000/md_1000ns.tpr",
        "xtc": [ROOT / "outputs_BLG/CENTER/MD1000/traj_comp.xtc"],
    },
    "R1": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD1/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0002.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0003.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0004.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0005.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0006.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD1/md_replica1_amd.part0007.xtc",
        ],
    },
    "R2": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD2/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD2/md_replica2_ext.part0002.xtc",
        ],
    },
    "R3": {
        "tpr": ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3.tpr",
        "xtc": [
            ROOT / "outputs_BLG/REPLICA/MD/MD3/traj_comp.xtc",
            ROOT / "outputs_BLG/REPLICA/MD/MD3/md_replica3_ext.part0002.xtc",
        ],
    },
}

INTERFACE_WINDOW_NM = 1.5


# -----------------------------------------------------------------------
# gmx hbond helpers
# -----------------------------------------------------------------------

def get_group_index(tpr, group_name):
    """Parse `gmx make_ndx` default group listing for an exact group name match."""
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
    """gmx hbond takes one -f file; concatenate multi-part replicas first."""
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


# -----------------------------------------------------------------------
# Interface water-water (unchanged, MDAnalysis, dynamic reselection)
# -----------------------------------------------------------------------

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


# -----------------------------------------------------------------------
# Main per-label analysis
# -----------------------------------------------------------------------

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

    out_npz = OUT / f"blg_hbonds_{label}.npz"
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
    ap.add_argument("--label", default="all",
                     choices=["CENTER", "R1", "R2", "R3", "all"])
    args = ap.parse_args()
    labels = list(TRAJS) if args.label == "all" else [args.label]
    for lab in labels:
        analyse_label(lab)


if __name__ == "__main__":
    main()
