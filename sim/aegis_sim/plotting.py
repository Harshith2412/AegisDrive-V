"""Static results viewer: multi-panel PNG per scenario trace (no GPU / 3D needed)."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STATES = ["DISABLED", "STANDBY", "MONITORING", "WARNING", "BRAKING", "DEGRADED", "FAULT"]


def _f(v):
    return float(v) if v not in ("", None) else float("nan")


def plot_trace(csv_path: str | Path, png_path: str | Path, title: str) -> None:
    with open(csv_path, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    t = [_f(r["t_s"]) for r in rows]
    fig, ax = plt.subplots(6, 1, figsize=(10, 13), sharex=True)
    ax[0].plot(t, [_f(r["ego_x_m"]) for r in rows], label="ego front bumper")
    ax[0].plot(t, [_f(r["lead_x_m"]) for r in rows], label="lead rear bumper")
    ax[0].set_ylabel("position [m]")
    ax[1].plot(t, [_f(r["ego_v_mps"]) * 3.6 for r in rows], label="ego")
    ax[1].plot(t, [_f(r["lead_v_mps"]) * 3.6 for r in rows], label="lead")
    ax[1].set_ylabel("speed [km/h]")
    ax[2].plot(t, [_f(r["gap_m"]) for r in rows], label="true gap")
    ax[2].plot(t, [_f(r["meas_range_m"]) for r in rows], ".", ms=1.5, label="radar range (ZOH)")
    ax[2].set_ylabel("gap [m]")
    ax[3].plot(t, [_f(r["ttc_s"]) for r in rows], label="TTC (ADAS)")
    ax[3].axhline(2.6, ls="--", c="orange", lw=0.8, label="warn 2.6 s")
    ax[3].axhline(1.6, ls="--", c="red", lw=0.8, label="brake 1.6 s")
    ax[3].set_ylim(0, 6)
    ax[3].set_ylabel("TTC [s]")
    ax[4].plot(t, [_f(r["decel_request_mps2"]) for r in rows], label="ADAS request")
    ax[4].plot(t, [_f(r["brake_actual_mps2"]) for r in rows], label="Brake ECU actuator")
    ax[4].plot(t, [-_f(r["ego_accel_mps2"]) for r in rows], ":", label="vehicle decel (friction-limited)")
    ax[4].set_ylabel("decel [m/s²]")
    ax[5].step(t, [STATES.index(r["adas_state"]) for r in rows], where="post", label="ADAS state")
    ax[5].step(t, [int(r["brake_lamp"]) - 1.2 for r in rows], where="post", label="brake lamp")
    ax[5].step(t, [int(r["hazard"]) - 2.6 for r in rows], where="post", label="hazard")
    ax[5].step(t, [int(r["unavailable"]) - 4.0 for r in rows], where="post", label="AEB unavailable")
    ax[5].set_yticks(list(range(7)))
    ax[5].set_yticklabels(STATES, fontsize=7)
    ax[5].set_xlabel("time [s]")
    for a in ax:
        a.grid(alpha=0.3)
        a.legend(fontsize=7, loc="upper right")
    fig.suptitle(title)
    fig.tight_layout()
    Path(png_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png_path, dpi=110)
    plt.close(fig)
