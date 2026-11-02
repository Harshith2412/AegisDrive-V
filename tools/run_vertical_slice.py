#!/usr/bin/env python3
"""Reproducible vertical-slice experiment runner.

Outputs (results/):
  traces/<ID>.csv, plots/<ID>.png      seed-0 trace + viewer per scenario
  scenario_summary.csv / .json         N seeds per scenario, collision counts + Wilson 95% CI
  sweep_stationary.csv, plots/sweep_stationary.png
                                       PRELIMINARY ego-speed x friction sweep (stationary target)
  vertical_slice_results.json          everything above in one machine-readable file
All seeds are listed in the outputs. Nothing is filtered or tuned after the fact.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim"))

from aegis_sim.plotting import plot_trace  # noqa: E402
from aegis_sim.runner import run_scenario  # noqa: E402
from aegis_sim.scenario import load_all, load_scenario  # noqa: E402
from aegis_sim.stats import wilson_interval  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=20)
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()
    out = Path(args.out)
    (out / "traces").mkdir(parents=True, exist_ok=True)
    (out / "plots").mkdir(parents=True, exist_ok=True)
    seeds = list(range(args.seeds))
    t_start = time.time()

    scenarios = load_all(ROOT / "scenarios")
    per_scenario, seed0 = [], {}
    for sc in scenarios:
        trace = out / "traces" / f"{sc.id}.csv"
        r0 = run_scenario(sc, seed=0, trace_path=trace)
        plot_trace(trace, out / "plots" / f"{sc.id}.png", f"{sc.id}: {sc.title}")
        seed0[sc.id] = r0.to_dict()
        runs = [r0] + [run_scenario(sc, seed=s) for s in seeds[1:]]
        n_coll = sum(r.collision for r in runs)
        lo, hi = wilson_interval(n_coll, len(runs))
        brk = [r.first_brake_request_s for r in runs if r.first_brake_request_s is not None]
        ttc = [r.ttc_at_brake_request_s for r in runs if r.ttc_at_brake_request_s is not None]
        per_scenario.append({
            "scenario": sc.id, "title": sc.title, "runs": len(runs), "collisions": n_coll,
            "collision_rate": n_coll / len(runs), "collision_rate_ci95": [round(lo, 4), round(hi, 4)],
            "brake_requested_runs": sum(r.first_brake_request_s is not None for r in runs),
            "warning_runs": sum(r.first_warning_s is not None for r in runs),
            "mean_first_brake_request_s": round(statistics.mean(brk), 4) if brk else None,
            "mean_ttc_at_brake_request_s": round(statistics.mean(ttc), 4) if ttc else None,
            "min_gap_m_min": round(min(r.min_gap_m for r in runs), 3),
            "min_gap_m_mean": round(statistics.mean(r.min_gap_m for r in runs), 3),
            "mean_impact_speed_kph_if_collision": round(statistics.mean(
                [r.impact_speed_mps * 3.6 for r in runs if r.collision]), 2) if n_coll else None,
            "degraded_runs": sum(r.first_degraded_s is not None for r in runs),
            "brake_timeout_runs": sum(r.brake_timeout_seen for r in runs),
            "illegal_transitions_total": sum(r.illegal_transitions for r in runs),
            "expected": sc.expected,
        })
        print(f"{sc.id}: collisions {n_coll}/{len(runs)}  (95% CI {lo:.3f}-{hi:.3f})")

    with open(out / "scenario_summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=[k for k in per_scenario[0] if k != "expected"])
        w.writeheader()
        for row in per_scenario:
            w.writerow({k: v for k, v in row.items() if k != "expected"})

    base = load_scenario(ROOT / "scenarios" / "S03_stationary_target.yaml")
    sweep = []
    for mu in (0.9, 0.5):
        for kph in range(10, 90, 10):
            v = kph / 3.6
            gap0 = max(40.0, 4.0 * v)  # start >= 4 s (and >= 40 m) away so every run reaches the threat
            sc = replace(base, ego_speed_kph=float(kph), mu=mu, gap0_m=gap0, duration_s=gap0 / v + 8.0)
            runs = [run_scenario(sc, seed=s) for s in seeds]
            n = sum(r.collision for r in runs)
            lo, hi = wilson_interval(n, len(runs))
            imp = [r.impact_speed_mps * 3.6 for r in runs if r.collision]
            sweep.append({"mu": mu, "ego_kph": kph, "runs": len(runs), "collisions": n,
                          "collision_rate": n / len(runs), "ci95_low": round(lo, 4), "ci95_high": round(hi, 4),
                          "mean_impact_kph": round(statistics.mean(imp), 2) if imp else 0.0,
                          "speed_reduction_pct": round(100 * (1 - statistics.mean(imp) / kph), 1) if imp else 100.0,
                          "mean_min_gap_m": round(statistics.mean(r.min_gap_m for r in runs), 3),
                          "brake_requested_runs": sum(r.first_brake_request_s is not None for r in runs),
                          "mean_ttc_at_brake_s": _mean_or_none(
                              [r.ttc_at_brake_request_s for r in runs if r.ttc_at_brake_request_s is not None])})
    with open(out / "sweep_stationary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sweep[0].keys()))
        w.writeheader()
        w.writerows(sweep)
    _plot_sweep(sweep, out / "plots" / "sweep_stationary.png")

    summary = {
        "generated_unix": int(time.time()), "runtime_s": round(time.time() - t_start, 2),
        "python": platform.python_version(), "platform": platform.platform(), "seeds": seeds,
        "scenarios": per_scenario, "seed0_details": seed0, "sweep_stationary": sweep,
        "note": "ADAS step timings are wall-clock per ctypes call (includes Python FFI overhead); "
                "they are NOT ECU execution-time / WCET measurements.",
    }
    (out / "vertical_slice_results.json").write_text(json.dumps(summary, indent=2))
    print(f"done in {summary['runtime_s']} s -> {out}")
    return 0


def _mean_or_none(xs):
    return round(statistics.mean(xs), 3) if xs else None


def _plot_sweep(sweep, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    for mu in sorted({s["mu"] for s in sweep}, reverse=True):
        pts = [s for s in sweep if s["mu"] == mu]
        x = [p["ego_kph"] for p in pts]
        y = [p["collision_rate"] for p in pts]
        err = [[p["collision_rate"] - p["ci95_low"] for p in pts], [p["ci95_high"] - p["collision_rate"] for p in pts]]
        ax[0].errorbar(x, y, yerr=err, marker="o", capsize=3, label=f"μ = {mu}")
        ax[1].plot(x, [p["mean_impact_kph"] for p in pts], marker="o", label=f"μ = {mu}")
    ax[0].set_xlabel("ego speed [km/h]"); ax[0].set_ylabel("collision rate (Wilson 95% CI)")
    ax[1].set_xlabel("ego speed [km/h]"); ax[1].set_ylabel("mean impact speed [km/h]")
    for a in ax:
        a.grid(alpha=0.3); a.legend()
    fig.suptitle("PRELIMINARY sweep — stationary target, radar-only, constant-velocity TTC (n=20 seeds/point)")
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    sys.exit(main())
