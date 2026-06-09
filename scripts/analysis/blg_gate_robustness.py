"""
gate_uncertainty_robustness.py
==============================
From saved gate NPZ files (no MDAnalysis needed), compute:
  1. Pearson r(SASA, theta) with autocorrelation-corrected SE
  2. Block-jackknife 95% CI on Obs/Indep per replica and aggregate
  3. Threshold robustness grid: Obs/Indep for SASA_thresh x angle_thresh combinations
  4. Activated-but-misaligned event termination classification

Outputs written to results/gate_robustness/ before any paper edits.

Usage:
    python scripts/gate_uncertainty_robustness.py
"""

from pathlib import Path
import json
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent.parent
GATE_DIR = ROOT / "results" / "gate_analysis"
OUT_DIR = ROOT / "results" / "gate_robustness"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SASA_THRESH_BASE = 35.0   # nm²
ANGLE_THRESH_BASE = 30.0  # degrees


# ── Load data ─────────────────────────────────────────────────────────────────

def load_replica(name):
    d = np.load(GATE_DIR / f"{name}_gate.npz")
    return {
        "name": name,
        "time":     d["time"],     # ns
        "sasa":     d["sasa"],     # nm²
        "angle":    d["angle"],    # degrees
        "min_dist": d["min_dist"], # nm
    }


# ── Integrated autocorrelation time ───────────────────────────────────────────

def autocorr(x):
    """Normalised autocorrelation via FFT."""
    x = x - x.mean()
    n = len(x)
    f = np.fft.fft(x, n=2 * n)
    acf = np.real(np.fft.ifft(f * np.conj(f)))[:n]
    acf /= acf[0]
    return acf


def iacf(x, max_lag=None):
    """Integrated autocorrelation time (frames) using Sokal's windowed estimator."""
    acf = autocorr(x)
    n = len(acf)
    if max_lag is None:
        max_lag = n // 4
    # Window: stop when acf[tau] < 2*tau/n (Sokal criterion)
    tau_int = 0.5
    for tau in range(1, max_lag):
        if acf[tau] <= 0:
            break
        tau_int += acf[tau]
        if tau >= 5 * tau_int:
            break
    return max(tau_int, 0.5)


def n_eff(x):
    """Effective sample size = N / (2 * tau_int)."""
    tau = iacf(x)
    return len(x) / (2.0 * tau)


# ── Pearson r with autocorrelation-corrected SE ───────────────────────────────

def pearson_r_corrected(sasa, angle):
    r, p_raw = stats.pearsonr(sasa, angle)
    neff_sasa  = n_eff(sasa)
    neff_angle = n_eff(angle)
    neff = min(neff_sasa, neff_angle)   # conservative
    # Fisher z-transform SE
    se_z = 1.0 / np.sqrt(max(neff - 3, 1))
    z = np.arctanh(r)
    ci_lo = np.tanh(z - 1.96 * se_z)
    ci_hi = np.tanh(z + 1.96 * se_z)
    return {"r": float(r), "p_raw": float(p_raw),
            "n_eff": float(neff), "ci95": [float(ci_lo), float(ci_hi)]}


# ── Obs/Indep for a single gate criterion ─────────────────────────────────────

def obs_over_indep(sasa, angle, sasa_thresh, angle_thresh):
    act  = sasa  >= sasa_thresh
    aln  = angle <= angle_thresh
    gate = act & aln
    p_act  = act.mean()
    p_aln  = aln.mean()
    p_gate = gate.mean()
    indep  = p_act * p_aln
    oi     = p_gate / indep if indep > 0 else np.nan
    return {
        "p_activated": float(p_act),
        "p_aligned":   float(p_aln),
        "p_gate_open": float(p_gate),
        "p_indep":     float(indep),
        "obs_over_indep": float(oi),
        "n_frames":    int(len(sasa)),
    }


# ── Block-jackknife CI on Obs/Indep ───────────────────────────────────────────

def block_jackknife_oi(sasa, angle, sasa_thresh, angle_thresh, block_size=80):
    """
    block_size: frames (at 0.5 ns stride, 80 frames = 40 ns, ~2x max tau)
    Returns jackknife estimate and 95% CI.
    """
    n = len(sasa)
    n_blocks = n // block_size
    if n_blocks < 4:
        return {"n_blocks": n_blocks, "note": "too few blocks for jackknife"}

    # Full estimate
    full = obs_over_indep(sasa, angle, sasa_thresh, angle_thresh)
    theta_all = full["obs_over_indep"]

    pseudo = []
    for k in range(n_blocks):
        idx = np.ones(n, dtype=bool)
        idx[k * block_size: (k + 1) * block_size] = False
        # include tail if n not divisible by block_size
        d = obs_over_indep(sasa[idx], angle[idx], sasa_thresh, angle_thresh)
        theta_k = d["obs_over_indep"]
        if np.isnan(theta_k):
            continue
        # pseudo-value
        pv = n_blocks * theta_all - (n_blocks - 1) * theta_k
        pseudo.append(pv)

    pseudo = np.array(pseudo)
    K = len(pseudo)
    se = np.sqrt(np.sum((pseudo - pseudo.mean())**2) / (K * (K - 1)))
    ci_lo = theta_all - 1.96 * se
    ci_hi = theta_all + 1.96 * se
    return {
        "obs_over_indep": float(theta_all),
        "jackknife_se":   float(se),
        "ci95":           [float(ci_lo), float(ci_hi)],
        "n_blocks":       int(K),
        "block_size_frames": block_size,
    }


# ── Threshold robustness grid ─────────────────────────────────────────────────

SASA_THRESHOLDS  = [30.0, 35.0, 40.0]   # nm²
ANGLE_THRESHOLDS = [15.0, 30.0, 45.0, 60.0, 90.0]  # degrees


def robustness_grid(all_sasa, all_angle):
    """Compute Obs/Indep on pooled data for each (sasa_thresh, angle_thresh)."""
    rows = []
    for st in SASA_THRESHOLDS:
        for at in ANGLE_THRESHOLDS:
            d = obs_over_indep(all_sasa, all_angle, st, at)
            rows.append({
                "sasa_thresh_nm2":  st,
                "angle_thresh_deg": at,
                **d,
            })
    return rows


# ── Event termination analysis ────────────────────────────────────────────────

# Activated-but-misaligned events from REVIEW_STATE.json
ABM_EVENTS = [
    {"replica": "R1", "start_ns":  362.0, "end_ns":  419.5, "dur_ns": 57.5},
    {"replica": "R1", "start_ns":  629.9, "end_ns":  664.4, "dur_ns": 34.5},
    {"replica": "R1", "start_ns":  665.4, "end_ns":  677.9, "dur_ns": 12.5},
    {"replica": "R3", "start_ns":  120.6, "end_ns":  142.4, "dur_ns": 21.8},
]


def classify_termination(time, sasa, angle, min_dist, end_ns,
                          sasa_thresh=35.0, angle_thresh=30.0, dist_thresh=0.30,
                          window_frames=10):
    """
    Look at window_frames after event end to classify termination mechanism.
    Returns dominant mechanism: SASA_DROP, SEPARATION, BOTH, END_OF_TRAJ.
    """
    dt = np.median(np.diff(time))
    end_idx = np.searchsorted(time, end_ns)
    if end_idx >= len(time) - window_frames:
        return "END_OF_TRAJ"

    post = slice(end_idx, min(end_idx + window_frames, len(time)))
    sasa_after  = sasa[post]
    dist_after  = min_dist[post]

    sasa_dropped    = np.any(sasa_after  < sasa_thresh)
    protein_left    = np.any(dist_after  > dist_thresh)

    if sasa_dropped and protein_left:
        return "BOTH"
    elif sasa_dropped:
        return "SASA_DROP"
    elif protein_left:
        return "SEPARATION"
    else:
        return "SUSTAINED"


def analyze_events(replicas):
    results = []
    for ev in ABM_EVENTS:
        rep = replicas[ev["replica"]]
        time = rep["time"]
        sasa = rep["sasa"]
        angle = rep["angle"]
        mdist = rep["min_dist"]

        s_idx = np.searchsorted(time, ev["start_ns"])
        e_idx = np.searchsorted(time, ev["end_ns"])
        ev_slice = slice(s_idx, e_idx + 1)

        sasa_ev  = sasa[ev_slice]
        angle_ev = angle[ev_slice]
        mdist_ev = mdist[ev_slice]

        # SASA criterion satisfied in what fraction of frames?
        sasa_frac  = float(np.mean(sasa_ev >= SASA_THRESH_BASE))
        angle_frac = float(np.mean(angle_ev <= ANGLE_THRESH_BASE))

        # Within-event statistics
        termination = classify_termination(
            time, sasa, angle, mdist, ev["end_ns"]
        )

        results.append({
            **ev,
            "n_frames_event":    int(e_idx - s_idx + 1),
            "sasa_frac_above35": sasa_frac,
            "angle_frac_below30": angle_frac,
            "sasa_mean":  float(sasa_ev.mean()),
            "sasa_max":   float(sasa_ev.max()),
            "angle_mean": float(angle_ev.mean()),
            "angle_min":  float(angle_ev.min()),
            "mdist_mean": float(mdist_ev.mean()),
            "termination": termination,
        })
    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Loading gate data...")
    replicas = {name: load_replica(name) for name in ["CENTER", "R1", "R2", "R3"]}

    results = {}

    # 1. Pearson r per replica + aggregate
    print("\n=== Pearson r(SASA, theta) ===")
    pearson = {}
    all_sasa, all_angle = [], []
    for name, rep in replicas.items():
        pr = pearson_r_corrected(rep["sasa"], rep["angle"])
        pearson[name] = pr
        all_sasa.append(rep["sasa"])
        all_angle.append(rep["angle"])
        print(f"  {name:8s}: r={pr['r']:+.3f}  95% CI=[{pr['ci95'][0]:+.3f}, {pr['ci95'][1]:+.3f}]  "
              f"n_eff={pr['n_eff']:.0f}  p_raw={pr['p_raw']:.2e}")
    all_sasa  = np.concatenate(all_sasa)
    all_angle = np.concatenate(all_angle)
    pr_agg = pearson_r_corrected(all_sasa, all_angle)
    pearson["aggregate"] = pr_agg
    print(f"  {'aggregate':8s}: r={pr_agg['r']:+.3f}  95% CI=[{pr_agg['ci95'][0]:+.3f}, {pr_agg['ci95'][1]:+.3f}]  "
          f"n_eff={pr_agg['n_eff']:.0f}  p_raw={pr_agg['p_raw']:.2e}")
    results["pearson_r"] = pearson

    # 2. Block-jackknife CI on Obs/Indep
    print("\n=== Block-jackknife 95% CI on Obs/Indep ===")
    jackknife = {}
    for name, rep in replicas.items():
        jk = block_jackknife_oi(rep["sasa"], rep["angle"],
                                SASA_THRESH_BASE, ANGLE_THRESH_BASE, block_size=80)
        jackknife[name] = jk
        oi = jk["obs_over_indep"]
        ci = jk.get("ci95", [None, None])
        print(f"  {name:8s}: Obs/Indep={oi:.3f}  95% CI=[{ci[0]:.3f}, {ci[1]:.3f}]  "
              f"n_blocks={jk['n_blocks']}")

    # Aggregate
    jk_agg = block_jackknife_oi(all_sasa, all_angle,
                                 SASA_THRESH_BASE, ANGLE_THRESH_BASE, block_size=80)
    jackknife["aggregate"] = jk_agg
    ci = jk_agg.get("ci95", [None, None])
    print(f"  {'aggregate':8s}: Obs/Indep={jk_agg['obs_over_indep']:.3f}  "
          f"95% CI=[{ci[0]:.3f}, {ci[1]:.3f}]  n_blocks={jk_agg['n_blocks']}")
    results["block_jackknife"] = jackknife

    # 3. Threshold robustness grid
    print("\n=== Threshold robustness grid (aggregate) ===")
    print(f"  {'SASA':>8}  {'angle':>8}  {'Obs/Indep':>10}  {'P_gate':>8}  {'P_act':>8}  {'P_aln':>8}")
    grid = robustness_grid(all_sasa, all_angle)
    for row in grid:
        print(f"  {row['sasa_thresh_nm2']:>8.0f}  {row['angle_thresh_deg']:>8.0f}  "
              f"{row['obs_over_indep']:>10.3f}  {row['p_gate_open']:>8.4f}  "
              f"{row['p_activated']:>8.4f}  {row['p_aligned']:>8.4f}")
    results["threshold_grid"] = grid

    # 4. Event termination analysis
    print("\n=== Activated-but-misaligned event termination ===")
    events = analyze_events(replicas)
    for ev in events:
        print(f"  {ev['replica']} {ev['start_ns']:.1f}-{ev['end_ns']:.1f} ns  "
              f"({ev['dur_ns']:.1f} ns): "
              f"SASA_above_35={ev['sasa_frac_above35']*100:.0f}%  "
              f"angle_below_30={ev['angle_frac_below30']*100:.0f}%  "
              f"angle_mean={ev['angle_mean']:.0f}°  "
              f"termination={ev['termination']}")
    results["event_termination"] = events

    # Decide language branch based on Pearson r
    r_agg = pr_agg["r"]
    ci_lo, ci_hi = pr_agg["ci95"]
    print("\n=== Language decision ===")
    if ci_hi < 0:
        decision = "ANTICORRELATED"
        note = f"r={r_agg:.3f}, CI entirely negative — 'anticorrelated' is justified"
    elif ci_lo > 0:
        decision = "CORRELATED"
        note = f"r={r_agg:.3f}, CI entirely positive — unexpected, check data"
    else:
        decision = "NEAR_ZERO_OR_CROSSING_ZERO"
        note = f"r={r_agg:.3f}, CI crosses zero — use suppression language, not anticorrelated"
    print(f"  Decision: {decision}")
    print(f"  Note:     {note}")
    results["language_decision"] = {"decision": decision, "note": note, "r": float(r_agg), "ci95": [float(ci_lo), float(ci_hi)]}

    # Save all results
    out_path = OUT_DIR / "robustness_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {out_path}")

    # Also save threshold grid as CSV for easy viewing
    import csv
    csv_path = OUT_DIR / "threshold_grid.csv"
    if grid:
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(grid[0].keys()))
            writer.writeheader()
            writer.writerows(grid)
    print(f"Threshold grid saved to {csv_path}")


if __name__ == "__main__":
    main()
