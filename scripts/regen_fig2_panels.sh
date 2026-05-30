#!/usr/bin/env bash
# regen_fig2_panels.sh
# Regenerate Fig 2 contact-tracking panels with updated plot_style (no grid, no title).
# Run ONE replica at a time to stay within 11 GB RAM.
# After all panels done, re-assembles PAPER_FIG2_CONTACT_AB.png and _CD.png.

set -euo pipefail
source ~/research-env/bin/activate
cd /home/cpornjar/Workspace/MILK_FROTHING

ROOT="outputs_BLG"
OUT="results/figures/adsorption"
SCRIPT="scripts/detect_adsorption_contact.py"

echo "=== [1/4] CENTER (1000 ns, stride=5) ==="
python3 -u "$SCRIPT" \
    --tpr    "$ROOT/CENTER/MD1000/md_1000ns.tpr" \
    --xtc    "$ROOT/CENTER/MD1000/traj_comp.xtc" \
    --label  CENTER_1000ns --out "$OUT" --stride 5

echo "=== [2/4] R1 (1000 ns, stride=5) ==="
# Use md_replica1.tpr (NVIDIA build) — ext TPR is tpx v138, unsupported by MDAnalysis
python3 -u "$SCRIPT" \
    --tpr    "$ROOT/REPLICA/MD/MD1/md_replica1.tpr" \
    --xtc    "$ROOT/REPLICA/MD/MD1/traj_comp.xtc" \
             "$ROOT/REPLICA/MD/MD1/md_replica1_amd.part0002.xtc" \
             "$ROOT/REPLICA/MD/MD1/md_replica1_amd.part0003.xtc" \
             "$ROOT/REPLICA/MD/MD1/md_replica1_amd.part0004.xtc" \
             "$ROOT/REPLICA/MD/MD1/md_replica1_amd.part0005.xtc" \
             "$ROOT/REPLICA/MD/MD1/md_replica1_amd.part0006.xtc" \
             "$ROOT/REPLICA/MD/MD1/md_replica1_amd.part0007.xtc" \
    --label  R1_1000ns_full --out "$OUT" --stride 5

echo "=== [3/4] R2 (1000 ns, stride=5) ==="
python3 -u "$SCRIPT" \
    --tpr    "$ROOT/REPLICA/MD/MD2/md_replica2.tpr" \
    --xtc    "$ROOT/REPLICA/MD/MD2/traj_comp.xtc" \
             "$ROOT/REPLICA/MD/MD2/md_replica2_ext.part0002.xtc" \
    --label  R2_1000ns --out "$OUT" --stride 5

echo "=== [4/4] R3 (1000 ns, stride=5) ==="
python3 -u "$SCRIPT" \
    --tpr    "$ROOT/REPLICA/MD/MD3/md_replica3.tpr" \
    --xtc    "$ROOT/REPLICA/MD/MD3/traj_comp.xtc" \
             "$ROOT/REPLICA/MD/MD3/md_replica3_ext.part0002.xtc" \
    --label  R3_1000ns --out "$OUT" --stride 5

echo "=== Assembling AB + CD ==="
python3 -u scripts/make_fig2_ab_cd.py

echo "=== DONE — panels regenerated, no grid, no title ==="
