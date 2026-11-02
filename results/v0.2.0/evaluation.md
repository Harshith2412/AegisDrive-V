# Before/after evaluation

Same scenario YAML, dt=10 ms, seeds 0–19 and common macOS dependency environment for both versions.
420 paired runs per version: 6 original scenarios and 15 boundary/adverse configurations.
The original 16-point stationary sweep is separately rerun for each version (320 runs each).
Original v0.1.0 Linux evidence remains archived as well as the local macOS reproduction.

| Input | Collisions old → new (/20) | Minimum separation old → new (m) | Retriggers old → new (total) |
|---|---|---|---|
| FI01 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |
| FI02 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |
| S01 | 0 → 0 | 40.0 → 40.0 | 0 → 0 |
| S02 | 0 → 0 | 0.575 → 7.771 | 0 → 0 |
| S03 | 0 → 0 | 2.401 → 4.888 | 0 → 0 |
| S04 | 0 → 0 | 1.018 → 20.263 | 20 → 0 |
| B_mu0.9_v10 | 0 → 0 | 2.816 → 2.816 | 0 → 0 |
| B_mu0.9_v50 | 0 → 0 | 2.411 → 4.786 | 0 → 0 |
| B_mu0.9_v60 | 0 → 0 | 2.283 → 5.571 | 0 → 0 |
| B_mu0.9_v80 | 0 → 0 | 2.184 → 8.165 | 0 → 0 |
| B_mu0.9_v81 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |
| B_mu0.5_v10 | 0 → 0 | 2.816 → 2.816 | 0 → 0 |
| B_mu0.5_v50 | 0 → 0 | 0.526 → 4.786 | 0 → 0 |
| B_mu0.5_v60 | 20 → 0 | 0.0 → 5.571 | 0 → 0 |
| B_mu0.5_v80 | 20 → 0 | 0.0 → 8.165 | 0 → 0 |
| B_mu0.5_v81 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |
| B_mu0.3_v10 | 0 → 0 | 2.629 → 2.629 | 0 → 0 |
| B_mu0.3_v50 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |
| B_mu0.3_v60 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |
| B_mu0.3_v80 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |
| B_mu0.3_v81 | 20 → 20 | 0.0 → 0.0 | 0 → 0 |

| Scenario | First warning old → new (s) | First command old → new (s) | Command-to-active old → new (ms) | Fault detection old → new (ms) |
|---|---|---|---|---|
| FI01 | None → None | None → None | None → None | 110.0 → 110.0 |
| FI02 | 3.19 → 3.19 | 4.183 → 3.55 | 10.0 → 20.0 | None → 120.0 |
| S01 | None → None | None → None | None → None | None → None |
| S02 | 3.085 → 2.127 | 3.455 → 2.127 | 20.0 → 20.0 | None → None |
| S03 | 3.19 → 3.19 | 4.183 → 3.55 | 10.0 → 20.0 | None → None |
| S04 | 6.26 → 4.665 | 6.947 → 4.665 | 20.0 → 20.0 | None → None |

Warning/command times are from simulation start. For S02/S04 the lead event begins at 2 s;
subtract 2 s to obtain event-to-indication/command latency. S03 target exists at t=0.
No independent ground-truth detection declaration exists: first warning is a decision timing proxy,
not measured perception detection latency. Radar sampling is 50 ms; availability is checked each 10 ms.
FI01 detection is 110 ms from freeze onset at 2 s, or 160 ms from last valid sample at 1.95 s.
FI02 feedback fault is 120 ms from drop onset at 4.2 s. None means no measurement/undefined, never zero.
Negative separation is not integrated after contact: min separation is clamped to 0 on collision.
At 81 km/h activation is outside the speed window; collision is an intentional residual limitation.
At mu=0.3 the planning assumption fails; these collisions remain in the report.
At mu=0.5 the expanded envelope avoids the tested high-speed impacts; it is not a wet-road guarantee.
Zero failures in 20 seeds gives a Wilson 95% upper collision-rate bound about 16.1%.
Seeds vary only nominal radar noise. They do not sample real traffic populations or confidence errors.
Wall-clock ctypes durations in raw JSON are host/FFI timings, not WCET.

Coverage: see coverage/summary.txt, coverage/mcdc-summary.txt and coverage/html/index.html.
LLVM source coverage is scoped to six ecu/src C++ files from C++ unit + Python integration tests;
scenario sweeps are not included. Baseline gcov is a different tool/denominator (unit tests only),
so its percentages are preserved but not compared numerically to LLVM.
Measured MC/DC condition coverage is partial, not a structural coverage adequacy claim.
Requirement verification: see traceability_matrix.md (39/39 linked tests pass); this does not
discharge the full safety goals or close the open issues in docs/v0.2.0_safety.md.
