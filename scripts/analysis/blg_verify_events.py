"""
verify_long_events.py — per-event SASA/angle stats from PBC-corrected .npz files.
Also recomputes Pearson r(SASA, angle) for the aggregate dataset.
"""
import sys
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parent.parent.parent
GATE_DIR = ROOT / "results" / "gate_analysis"

# Long residency events (≥10 ns) from original analysis
EVENTS = [
    ("R1",     362.0,  419.5, "R1 362–419.5 ns  (NEEDS RECHECK)"),
    ("R1",     629.9,  664.4, "R1 629.9–664.4 ns"),
    ("R1",     665.4,  677.9, "R1 665.4–677.9 ns"),
    ("R3",     120.6,  142.4, "R3 120.6–142.4 ns"),
    ("CENTER", 547.0,  557.5, "CENTER 547–557.5 ns"),
    ("R1",     773.0,  832.0, "R1 773–832 ns"),
]

# All replicas for aggregate Pearson r
all_sasa, all_angle = [], []

print("=" * 72)
print("  PER-EVENT SASA / ANGLE STATS (PBC-corrected)")
print("=" * 72)
print(f"{'Event':<30}  {'N':>5}  {'SASA_mean':>9}  {'SASA_max':>8}  "
      f"{'θ_mean':>7}  {'θ_min':>7}  {'SASA≥35':>7}  {'SASA≥32.1':>9}")
print("-" * 90)

for rep, t_lo, t_hi, label in EVENTS:
    z = np.load(GATE_DIR / f"{rep}_gate.npz")
    t, s, a = z["time"], z["sasa"], z["angle"]

    mask = (t >= t_lo) & (t <= t_hi)
    s_ev = s[mask]
    a_ev = a[mask]

    if len(s_ev) == 0:
        print(f"{label:<30}  {'—':>5}  (no frames in window)")
        continue

    pct_35  = 100 * (s_ev >= 35.0).mean()
    pct_321 = 100 * (s_ev >= 32.10).mean()

    print(f"{label:<30}  {len(s_ev):>5}  {s_ev.mean():>9.2f}  {s_ev.max():>8.2f}  "
          f"{a_ev.mean():>7.1f}  {a_ev.min():>7.1f}  {pct_35:>6.1f}%  {pct_321:>8.1f}%")

# Aggregate Pearson r
print()
print("=" * 72)
print("  AGGREGATE PEARSON r(SASA, angle)  — PBC-corrected")
print("=" * 72)

for rep in ("CENTER", "R1", "R2", "R3"):
    z = np.load(GATE_DIR / f"{rep}_gate.npz")
    all_sasa.append(z["sasa"])
    all_angle.append(z["angle"])

s_all = np.concatenate(all_sasa)
a_all = np.concatenate(all_angle)

r, p = pearsonr(s_all, a_all)
print(f"  N = {len(s_all)} frames")
print(f"  Pearson r = {r:.4f}  (p = {p:.4f})")
print(f"  SASA: mean={s_all.mean():.2f}  std={s_all.std():.2f}  "
      f"min={s_all.min():.1f}  max={s_all.max():.1f} nm²")
print(f"  Angle: mean={a_all.mean():.1f}  std={a_all.std():.1f}  "
      f"min={a_all.min():.0f}  max={a_all.max():.0f}°")

# Bootstrap CI on r (10000 resamples)
rng = np.random.default_rng(42)
n = len(s_all)
boot_r = np.empty(10000)
for i in range(10000):
    idx = rng.integers(0, n, size=n)
    boot_r[i] = pearsonr(s_all[idx], a_all[idx])[0]

ci_lo, ci_hi = np.percentile(boot_r, [2.5, 97.5])
print(f"  Bootstrap 95% CI: [{ci_lo:.4f}, {ci_hi:.4f}]")
