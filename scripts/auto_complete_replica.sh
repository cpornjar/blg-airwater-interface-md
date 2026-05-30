#!/usr/bin/env bash
# auto_complete_replica.sh
# ========================
# Called by the cron monitor when a replica hits 1000 ns.
# Usage: bash auto_complete_replica.sh <replica_number>   e.g.  bash auto_complete_replica.sh 2
#
# Steps:
#   1. Pull trajectory parts from cluster via rsync
#   2. Concatenate original traj_comp.xtc + extension part(s) → traj_rN_1000ns.xtc
#   3. Run all 5 analysis scripts on the combined trajectory
#   4. Update RESEARCH_BRIEF.md with new results
#
# Safe to re-run — rsync is idempotent, output files are overwritten.

set -euo pipefail

REPLICA="${1:-}"
if [[ -z "$REPLICA" || ! "$REPLICA" =~ ^[123]$ ]]; then
  echo "Usage: $0 <1|2|3>"
  exit 1
fi

# ── Config ────────────────────────────────────────────────────────────────────
ROOT=~/Workspace/MILK_FROTHING
SCRIPTS=$ROOT/scripts
CLUSTER=guest@158.108.25.40
KEY=~/.ssh/id_ed25519_ku
CLUSTER_BASE=/comfha/users/guest/PAO/MILK_FROTHING/REPLICA/MD
LOCAL_BASE=$ROOT/outputs_BLG/REPLICA/MD

source ~/research-env/bin/activate
cd $ROOT

log() { echo "[$(date '+%H:%M:%S')] $*"; }

# ── Per-replica config ────────────────────────────────────────────────────────
case "$REPLICA" in
  1)
    LOCAL_DIR=$LOCAL_BASE/MD1
    CLUSTER_DIR=$CLUSTER_BASE/MD1
    LABEL="REPLICA_1_1000ns"
    TPR=$LOCAL_DIR/md_replica1.tpr
    ORIG_XTC=$LOCAL_DIR/traj_comp.xtc
    # AMD parts
    EXT_PATTERN="md_replica1_amd.part000*.xtc"
    COMBINED=$LOCAL_DIR/traj_r1_1000ns.xtc
    ;;
  2)
    LOCAL_DIR=$LOCAL_BASE/MD2
    CLUSTER_DIR=$CLUSTER_BASE/MD2
    LABEL="REPLICA_2_1000ns"
    TPR=$LOCAL_DIR/md_replica2.tpr
    ORIG_XTC=$LOCAL_DIR/traj_comp.xtc
    EXT_PATTERN="md_replica2_ext.part*.xtc"
    COMBINED=$LOCAL_DIR/traj_r2_1000ns.xtc
    ;;
  3)
    LOCAL_DIR=$LOCAL_BASE/MD3
    CLUSTER_DIR=$CLUSTER_BASE/MD3
    LABEL="REPLICA_3_1000ns"
    TPR=$LOCAL_DIR/md_replica3.tpr
    ORIG_XTC=$LOCAL_DIR/traj_comp.xtc
    EXT_PATTERN="md_replica3_ext.part*.xtc"
    COMBINED=$LOCAL_DIR/traj_r3_1000ns.xtc
    ;;
esac

log "=== AUTO-COMPLETE: Replica $REPLICA ($LABEL) ==="

# ── Step 1: Pull extension trajectory from cluster ────────────────────────────
log "[1/4] Pulling trajectories from cluster..."
rsync -av --progress \
  -e "ssh -i $KEY" \
  "$CLUSTER:$CLUSTER_DIR/$EXT_PATTERN" \
  "$LOCAL_DIR/" 2>&1 | grep -v "WARNING\|vulnerable"

# Also pull final checkpoint and log
rsync -av -e "ssh -i $KEY" \
  "$CLUSTER:$CLUSTER_DIR/"*.cpt \
  "$CLUSTER:$CLUSTER_DIR/"*.log \
  "$LOCAL_DIR/" 2>&1 | grep -v "WARNING\|vulnerable" || true

log "Pull complete."

# ── Step 2: Concatenate trajectories ─────────────────────────────────────────
log "[2/4] Concatenating trajectories → $(basename $COMBINED)..."

EXT_FILES=$(ls $LOCAL_DIR/$EXT_PATTERN 2>/dev/null | sort)
if [[ -z "$EXT_FILES" ]]; then
  echo "ERROR: No extension XTC files found matching $EXT_PATTERN"
  exit 1
fi

printf 'c\nc\nc\nc\nc\n' | gmx trjcat \
  -f "$ORIG_XTC" $EXT_FILES \
  -o "$COMBINED" \
  -settime 2>&1 | tail -5

log "Concatenation done: $(du -sh $COMBINED | cut -f1)"

# ── Step 3: Run all 5 analysis scripts ────────────────────────────────────────
log "[3/4] Running analysis pipeline on $LABEL..."

FIG=$ROOT/results/figures

# Z-position
python scripts/track_z_position.py <<< "" 2>/dev/null || true
python - <<EOF
import sys; sys.path.insert(0,'scripts')
import track_z_position as tz
tz.TPR_FILE   = '$TPR'
tz.XTC_FILE   = '$COMBINED'
tz.OUTPUT_PNG = '$FIG/z_position/${LABEL}_z_position.png'
tz.STRIDE = 1
u = tz.load_universe()
times, z_prot, z_upper, z_lower = tz.analyze(u)
tz.print_summary(times, z_prot, z_upper, z_lower)
tz.plot(times, z_prot, z_upper, z_lower)
EOF

# RMSD
python - <<EOF
import sys; sys.path.insert(0,'scripts')
import rmsd_analysis as ra
ra.TPR_FILE   = '$TPR'
ra.XTC_FILE   = '$COMBINED'
ra.OUTPUT_PNG = '$FIG/rmsd/${LABEL}_rmsd.png'
u = ra.load_universe()
results = ra.analyze(u)
ra.print_summary(results)
ra.plot(results)
EOF

# SASA
python - <<EOF
import sys; sys.path.insert(0,'scripts')
import sasa_analysis as sa
sa.TPR_FILE   = '$TPR'
sa.XTC_FILE   = '$COMBINED'
sa.OUTPUT_PNG = '$FIG/sasa/${LABEL}_sasa.png'
u = sa.load_universe()
times_s, total, hydrophob, hydrophil, calyx = sa.analyze(u)
sa.print_summary(times_s, total, hydrophob, hydrophil, calyx)
sa.plot(times_s, total, hydrophob, hydrophil, calyx)
EOF

# Orientation
python - <<EOF
import sys, pathlib; sys.path.insert(0,'scripts')
pathlib.Path('$FIG/orientation').mkdir(parents=True, exist_ok=True)
import orientation_analysis as oa
oa.TPR_FILE   = '$TPR'
oa.XTC_FILE   = '$COMBINED'
oa.OUTPUT_PNG = '$FIG/orientation/${LABEL}_orientation.png'
u = oa.load_universe()
times, z_prot, angle_h, angle_p = oa.analyze(u)
oa.print_summary(times, z_prot, angle_h, angle_p)
oa.plot(times, z_prot, angle_h, angle_p)
EOF

# Advanced (RMSF/Rg)
python - <<EOF
import sys, pathlib; sys.path.insert(0,'scripts')
pathlib.Path('$FIG/advanced').mkdir(parents=True, exist_ok=True)
import advanced_analysis as aa
aa.TPR_FILE   = '$TPR'
aa.XTC_FILE   = '$COMBINED'
aa.OUTPUT_PNG = '$FIG/advanced/${LABEL}_advanced.png'
u = aa.load_universe()
resids, rmsf = aa.calc_rmsf(u)
times_rg, rg = aa.calc_rg(u)
times_z, rmsd_bb, z_pos = aa.calc_z_and_rmsd(u)
aa.print_summary(resids, rmsf, times_rg, rg, rmsd_bb, z_pos)
aa.plot(resids, rmsf, times_rg, rg, rmsd_bb, z_pos)
EOF

log "Analysis complete. Figures in $FIG"

# ── Step 4: Update RESEARCH_BRIEF.md ─────────────────────────────────────────
log "[4/4] Updating RESEARCH_BRIEF.md..."

TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
python - <<EOF
brief = open('$ROOT/../RESEARCH_BRIEF.md').read()
marker = '- [ ] Replica $REPLICA'
replacement = '- [x] Replica $REPLICA → 1000 ns COMPLETE — analysis done $TIMESTAMP, figures in results/figures/**/${LABEL}_*'
if marker in brief:
    brief = brief.replace(marker, replacement, 1)
    open('$ROOT/../RESEARCH_BRIEF.md', 'w').write(brief)
    print('RESEARCH_BRIEF.md updated.')
else:
    print('Marker not found in brief — appending note.')
EOF

log "=== Replica $REPLICA auto-complete DONE at $(date '+%H:%M:%S') ==="
