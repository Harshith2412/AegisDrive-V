# 03 — Operational Design Domain (vertical-slice baseline)

| Dimension | ODD (slice) | Rationale / note |
|---|---|---|
| Road | straight, flat, single lane, no curvature | longitudinal-only model |
| Surface friction | mu in [0.8, 1.0] nominal; mu 0.5 evaluated **outside** ODD | dry asphalt; wet-road behaviour is a known limitation (OI-004) |
| Ego speed for activation | 10–80 km/h (2.78–22.22 m/s) | ADAS-REQ-004; braking continues below 10 km/h once started |
| Target type | one passenger car ahead, in path, stationary or moving in the same direction | no pedestrians, cyclists, cut-ins, oncoming traffic |
| Target dynamics | lead deceleration up to friction limit | S02 uses 6 m/s² |
| Perception | radar only, range <= 150 m, 20 Hz, sigma_r 0.10 m, sigma_rr 0.10 m/s | camera/fusion not implemented |
| Visibility / weather | not modelled in the slice | SOTIF sweeps (Phase 6) will add degradation models |
| Driver | inattentive, no braking or steering (DRV-A-01), takes over at standstill (DRV-A-02) | standard worst-case AEB test assumption |
| Network | classic CAN, 10 ms cycle, 1-cycle latency, no arbitration delays | CAN FD and bus load later |

## ODD exit / boundary behaviour
Outside the speed window the function stays in STANDBY (no new intervention). Friction below the ODD is **not
detected** by the function; the sweep in `results/` quantifies the consequence. Inputs outside plausibility ranges
cause DEGRADED (ADAS-REQ-009).
