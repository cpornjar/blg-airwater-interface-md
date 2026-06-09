"""
prepare_set1d.py
=================
Prepare SET 1D-a and 1D-b starting structures for the above-water BLG simulation.

SET 1D tests the two-factor gating mechanism by controlling starting orientation:
  1D-a : Hydrophobic patch (calyx) facing DOWN (-Z) toward water interface  → fast adsorption expected
  1D-b : Hydrophobic patch (calyx) facing UP   (+Z) away from interface     → control, slow/no adsorption

Method:
  1. Load equilibrated NVT slab (protein inside water, near upper interface)
  2. Isolate protein, rotate to desired calyx orientation using Rodrigues rotation
  3. Translate protein CoM to Z = 23.0 nm (2.06 nm above upper interface at 20.94 nm)
  4. Replace protein positions in slab system, write new GRO files

Usage (from MILK_FROTHING root):
    source ~/research-env/bin/activate
    python scripts/prepare_set1d.py
"""

import numpy as np
import MDAnalysis as mda
from scipy.spatial.transform import Rotation as R
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

# ── Paths ─────────────────────────────────────────────────────────────────────
NVT_TPR = ROOT / "outputs_BLG/REPLICA/NVT_SLAB_REPLICA/nvt_slab_replica.tpr"
NVT_GRO = ROOT / "outputs_BLG/REPLICA/NVT_SLAB_REPLICA/confout.gro"
OUT_DIR  = ROOT / "outputs_BLG/SET1D"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Calyx residues (hydrophobic patch of 1BEB) ────────────────────────────────
# From orientation_analysis.py — verified against BLG crystal structure
CALYX_RESIDS = [39, 41, 56, 58, 92, 103, 105, 107, 125]

# ── Placement parameters ──────────────────────────────────────────────────────
UPPER_IFACE_Z_NM = 20.943   # measured from NVT equilibration (99th pct water O)
TARGET_Z_NM      = 23.0     # protein CoM Z placement (2.06 nm above interface, in vacuum)


def rotation_to_align(v_from: np.ndarray, v_to: np.ndarray) -> np.ndarray:
    """Return 3×3 rotation matrix that rotates unit vector v_from onto v_to."""
    v_from = v_from / np.linalg.norm(v_from)
    v_to   = v_to   / np.linalg.norm(v_to)
    cross  = np.cross(v_from, v_to)
    dot    = np.dot(v_from, v_to)
    if np.linalg.norm(cross) < 1e-8:
        # Vectors are parallel or anti-parallel
        if dot > 0:
            return np.eye(3)
        else:
            # 180° rotation around any perpendicular axis
            perp = np.array([1, 0, 0]) if abs(v_from[0]) < 0.9 else np.array([0, 1, 0])
            axis = np.cross(v_from, perp)
            axis /= np.linalg.norm(axis)
            return R.from_rotvec(np.pi * axis).as_matrix()
    axis  = cross / np.linalg.norm(cross)
    angle = np.arctan2(np.linalg.norm(cross), dot)
    return R.from_rotvec(angle * axis).as_matrix()


def prepare_structure(label: str, calyx_target_z: str) -> None:
    """
    label           : '1Da' or '1Db'
    calyx_target_z  : 'down' (patch faces -Z toward water) or 'up' (patch faces +Z away)
    """
    print(f"\n{'='*55}")
    print(f"  Preparing SET {label} — calyx pointing {calyx_target_z.upper()}")
    print(f"{'='*55}")

    u = mda.Universe(str(NVT_TPR), str(NVT_GRO))
    protein = u.select_atoms("protein")
    solvent = u.select_atoms("not protein")

    # Calyx and protein centers (Å)
    calyx_sel = " or ".join([f"resid {r}" for r in CALYX_RESIDS])
    calyx     = protein.select_atoms(f"({calyx_sel})")
    prot_com  = protein.center_of_mass()       # Å
    calyx_com = calyx.center_of_mass()         # Å

    calyx_vec = calyx_com - prot_com
    calyx_vec_norm = calyx_vec / np.linalg.norm(calyx_vec)

    print(f"  Protein CoM       : Z = {prot_com[2]/10:.3f} nm")
    print(f"  Calyx CoM         : Z = {calyx_com[2]/10:.3f} nm")
    print(f"  Calyx vector (nm) : {calyx_vec/10}")

    # Target direction
    target_vec = np.array([0.0, 0.0, -1.0]) if calyx_target_z == "down" else np.array([0.0, 0.0, 1.0])
    rot_mat = rotation_to_align(calyx_vec_norm, target_vec)

    # Apply rotation around protein CoM
    protein_pos   = protein.positions.copy()          # Å
    centered      = protein_pos - prot_com
    rotated       = centered @ rot_mat.T
    protein_new   = rotated + prot_com                # back to original CoM, still in water

    # Translate CoM to target Z (convert nm → Å)
    box_xy_center_A = np.array([u.dimensions[0] / 2, u.dimensions[1] / 2, 0.0])
    target_com_A    = np.array([
        box_xy_center_A[0],
        box_xy_center_A[1],
        TARGET_Z_NM * 10.0
    ])
    translation     = target_com_A - prot_com
    protein_final   = protein_new + translation

    # Verify calyx now points in target direction
    new_calyx_idx  = [i for i, atom in enumerate(protein.atoms)
                      if atom.resid in CALYX_RESIDS]
    new_calyx_pos  = protein_final[new_calyx_idx]
    new_prot_com   = protein_final.mean(axis=0)
    new_calyx_com  = new_calyx_pos.mean(axis=0)
    new_vec        = (new_calyx_com - new_prot_com)
    new_vec_norm   = new_vec / np.linalg.norm(new_vec)
    angle_to_target = np.degrees(np.arccos(np.clip(np.dot(new_vec_norm, target_vec), -1, 1)))

    print(f"  Rotation applied  : calyx now at {angle_to_target:.1f}° from target (should be ~0°)")
    print(f"  New protein CoM Z : {protein_final.mean(axis=0)[2]/10:.3f} nm")
    print(f"  Upper interface Z : {UPPER_IFACE_Z_NM:.3f} nm")
    print(f"  Gap to interface  : {(protein_final.mean(axis=0)[2]/10 - UPPER_IFACE_Z_NM):.3f} nm")

    # Write modified GRO
    protein.positions = protein_final
    merged = protein + solvent
    out_gro = OUT_DIR / f"set1d_{label}_start.gro"
    merged.write(str(out_gro))
    print(f"  Written → {out_gro}")

    # Sanity: print min Z of protein atoms (should be > ~19 nm to avoid clashing into bulk water)
    min_prot_z_nm = protein_final[:, 2].min() / 10
    max_prot_z_nm = protein_final[:, 2].max() / 10
    print(f"  Protein Z range   : {min_prot_z_nm:.2f} – {max_prot_z_nm:.2f} nm")
    if min_prot_z_nm < UPPER_IFACE_Z_NM:
        print(f"  ⚠ Lowest protein atom ({min_prot_z_nm:.2f} nm) is below interface — EM will resolve clashes")
    else:
        print(f"  ✓ All protein atoms above interface — clean vacuum placement")


if __name__ == "__main__":
    print(f"NVT GRO : {NVT_GRO}")
    print(f"Output  : {OUT_DIR}")
    prepare_structure("1Da", "down")   # patch toward water — fast adsorption
    prepare_structure("1Db", "up")     # patch away from water — control
    print(f"\nDone. Both structures in {OUT_DIR}")
