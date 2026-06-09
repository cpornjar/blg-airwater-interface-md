"""
block_bootstrap_r.py — block bootstrap for Pearson r (SASA vs angle).
Accounts for trajectory autocorrelation. Reports CI and effective N.

Block length = autocorrelation time of SASA (estimated via first zero crossing).
"""
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GATE_DIR = ROOT / "results" / "gate_analysis"

LABELS = ["CENTER", "R1", "R2", "R3"]
FILES  = [GATE_DIR / f"{lab}_gate.npz" for lab in LABELS]
STRIDE_NS = 0.5   # stride used in gate analysis
N_BOOT    = 10000
SEED      = 42


def acf_zero_crossing(x):
    x = x - x.mean()
    n = len(x)
    acf = np.correlate(x, x, mode='full')[n-1:]
    acf /= acf[0]
    crossings = np.where(acf < 0)[0]
    return int(crossings[0]) if len(crossings) else n // 4


def block_bootstrap_r(sasa, angle, block_len, n_boot=10000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(sasa)
    n_blocks = int(np.ceil(n / block_len))
    starts = np.arange(0, n - block_len + 1)
    rs = []
    for _ in range(n_boot):
        idx_starts = rng.choice(starts, size=n_blocks, replace=True)
        idx = np.concatenate([np.arange(s, min(s + block_len, n)) for s in idx_starts])[:n]
        s, a = sasa[idx], angle[idx]
        r = np.corrcoef(s, a)[0, 1]
        rs.append(r)
    rs = np.array(rs)
    return rs.mean(), np.percentile(rs, 2.5), np.percentile(rs, 97.5)


# Pool data
all_sasa, all_angle = [], []
for fp in FILES:
    d = np.load(fp)
    all_sasa.append(d['sasa'])
    all_angle.append(d['angle'])

sasa_pool  = np.concatenate(all_sasa)
angle_pool = np.concatenate(all_angle)

# Point estimate
r_point = np.corrcoef(sasa_pool, angle_pool)[0, 1]
print(f"Pooled N = {len(sasa_pool)}")
print(f"Point r  = {r_point:+.4f}")

# Autocorrelation time from SASA of each replica
print("\nAutocorrelation times (SASA):")
act_frames_list = []
for lab, fp in zip(LABELS, FILES):
    d = np.load(fp)
    act_f = acf_zero_crossing(d['sasa'])
    act_ns = act_f * STRIDE_NS
    act_frames_list.append(act_f)
    print(f"  {lab}: {act_f} frames = {act_ns:.1f} ns")

block_len = int(np.median(act_frames_list))
print(f"\nUsing block length = {block_len} frames ({block_len * STRIDE_NS:.1f} ns)")

# Block bootstrap on pooled data
print(f"\nRunning {N_BOOT}-sample block bootstrap...")
r_mean, ci_lo, ci_hi = block_bootstrap_r(sasa_pool, angle_pool, block_len, N_BOOT, SEED)

print(f"\nBlock bootstrap result (95% CI):")
print(f"  r = {r_point:+.4f}")
print(f"  95% CI = [{ci_lo:+.4f}, {ci_hi:+.4f}]")
print(f"  Rules out |r| > {max(abs(ci_lo), abs(ci_hi)):.3f}")

# Also run with 2× and 0.5× block length for sensitivity
for mult, label in [(0.5, "0.5×"), (2.0, "2×")]:
    bl = max(1, int(block_len * mult))
    rm, lo, hi = block_bootstrap_r(sasa_pool, angle_pool, bl, N_BOOT, SEED)
    print(f"  Sensitivity ({label} block = {bl} frames): r={rm:+.4f}, 95% CI [{lo:+.4f}, {hi:+.4f}]")

# Effective N estimate
n_eff = len(sasa_pool) / block_len
print(f"\nEffective N ≈ {n_eff:.0f} (vs. raw N = {len(sasa_pool)})")
