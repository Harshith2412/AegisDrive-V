> Historical v0.1.0 record retained for comparison. Current v0.2.0 analysis and issue dispositions: [safety](v0.2.0_safety.md), [audit](v0.2.0_audit.md), [release](v0.2.0_release.md).

# Open Issues and Limitations Register

Status values: OPEN, ACCEPTED (limitation accepted for the slice), CLOSED.

| ID | Source | Description | Evidence | Status / plan |
|---|---|---|---|---|
| OI-001 | FI02 | The ADAS ECU does not consume BRAKE_STATUS. When BRAKE_REQ frames are lost, the Brake ECU correctly times out (TSR-003) but the ADAS ECU keeps "BRAKING", the driver is not informed, and the collision is unmitigated (20/20 runs). | `results/traces/FI02.csv`, ST-FI-002 | OPEN → Phase 3 TSR: ADAS shall monitor brake execution feedback and raise a driver alert. |
| OI-002 | S02 | Constant-velocity TTC (LIM-ALG-01) reacts late to a braking lead; S02 avoided but minimum gap only 0.58–0.81 m. | `results/scenario_summary.csv` | OPEN → evaluate acceleration-aware TTC in Phase 6/9. |
| OI-003 | S04 | Threat-clear logic uses instantaneous closing speed: AEB aborted mid-event when ego briefly became slower than the decelerating lead; the inattentive driver re-accelerated and a second intervention was needed (no collision). | `results/traces/S04.csv` (states MON→WRN→BRK→MON→STB→BRK→STB) | OPEN → review abort criterion (predicted, not instantaneous, closing). |
| OI-004 | sweep | No friction awareness: at mu = 0.5 collisions in 100 % of runs at 60/70/80 km/h (mean impact 20/34/46 km/h). | `results/sweep_stationary.csv` | ACCEPTED for slice (outside ODD) → SOTIF analysis Phase 6. |
| OI-005 | ST-INV-002 | CRC-8 + counter provide no authenticity: a manipulated BRAKE_REQ with recomputed CRC and in-range value is accepted and induces unnecessary braking. | ST-INV-002 (characterisation test, PASS = vulnerability present) | OPEN → Phase 7 message authentication + freshness. |
| OI-006 | FI01 | Radar is the single perception source; radar loss ⇒ AEB unavailable ⇒ collision at full speed (20/20) even though the fault is detected within 160 ms. | `results/traces/FI01.csv` | OPEN → camera model + fusion + degradation strategy (Phases 3/5). |
| OI-007 | BCM-REQ-004 | Brake-lamp behaviour on BRAKE_STATUS timeout ("retain last") is provisional. | UT-BCM-004 | OPEN → decide in FSC. |
| OI-008 | BCM-REQ-003 | Hazard policy is project-defined and not checked against any regulation. | — | ACCEPTED (documented). |
| OI-009 | BRK-REQ-001 | First frame after start-up is used for counter synchronisation without authentication. | UT-BRK-001 | OPEN → Phase 7. |
| OI-010 | LIM-TIME-01 | Reported ECU step times are host wall-clock times of ctypes calls, not ECU execution times. | `vertical_slice_results.json` | ACCEPTED; WCET out of scope. |
| OI-011 | toolchain | CMake + GoogleTest + pytest build path written but **not executed** in the development sandbox (tools unavailable). | `docs/toolchain_notes.md` | OPEN → run `scripts/build_and_test.sh` on macOS and record results. |
| OI-012 | process | HARA, FSC/TSC, FMEA/FTA, SysML model, SOTIF, TARA not started; FSR/TSR are provisional. | `docs/phase_status.md` | OPEN (planned phases). |
| OI-013 | statistics | 20 seeds/point and small sensor noise: zero observed failures only bound the rate below ≈16 % (95 %). | Wilson CIs in results | ACCEPTED; larger N and stochastic SOTIF factors in Phase 9. |
