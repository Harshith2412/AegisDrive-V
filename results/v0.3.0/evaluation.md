# v0.3.0 quantitative evaluation

828 candidate runs; frozen case manifest and all raw outcomes retained.
Six original scenarios × four configurations × 20 seeds (480); 18 fault/SOTIF cases × 10 seeds (180);
48 development and 120 hold-out parameter samples. Baseline reproduction includes 6×20 scenarios plus the original 16×20 sweep.

| Original | v0.2 collisions /20 | v0.3 radar /20 | camera /20 | combined /20 | combined+backup /20 |
|---|---|---|---|---|---|
| FI01 | 20 | 20 | 0 | 0 | 0 |
| FI02 | 20 | 20 | 20 | 20 | 0 |
| S01 | 0 | 0 | 0 | 0 | 0 |
| S02 | 0 | 0 | 0 | 0 | 0 |
| S03 | 0 | 0 | 0 | 0 | 0 |
| S04 | 0 | 0 | 0 | 0 | 0 |

| Original | Baseline minimum gap (m) | Combined+backup minimum gap (m) | Baseline mean first command (s) | New mean first command (s) |
|---|---|---|---|---|
| FI01 | 0.0 | 5.345 | None | 3.5295 |
| FI02 | 0.0 | 5.246 | 3.55 | 3.529 |
| S01 | 40.0 | 40.000 | None | None |
| S02 | 7.771 | 7.354 | 2.1275 | 2.163 |
| S03 | 4.888 | 5.237 | 3.55 | 3.529 |
| S04 | 20.263 | 20.263 | 4.665 | 4.6445 |

| Case/configuration | n | Collisions | 95% Wilson interval | Minimum gap (m) | False interventions | Missed-detection cycles | Retriggers |
|---|---|---|---|---|---|---|---|
| FI01_radar | 20 | 20 | [0.839, 1.000] | 0.000 | 0 | 7320 | 0 |
| FI01_camera | 20 | 0 | [0.000, 0.161] | 5.345 | 0 | 720 | 0 |
| FI01_combined | 20 | 0 | [0.000, 0.161] | 5.345 | 0 | 487 | 0 |
| FI01_combined_backup | 20 | 0 | [0.000, 0.161] | 5.345 | 0 | 487 | 0 |
| FI02_radar | 20 | 20 | [0.839, 1.000] | 0.000 | 0 | 0 | 0 |
| FI02_camera | 20 | 20 | [0.839, 1.000] | 0.000 | 0 | 365 | 0 |
| FI02_combined | 20 | 20 | [0.839, 1.000] | 0.000 | 0 | 0 | 0 |
| FI02_combined_backup | 20 | 0 | [0.000, 0.161] | 5.246 | 0 | 0 | 0 |
| S01_radar | 20 | 0 | [0.000, 0.161] | 40.000 | 0 | 0 | 0 |
| S01_camera | 20 | 0 | [0.000, 0.161] | 40.000 | 0 | 910 | 0 |
| S01_combined | 20 | 0 | [0.000, 0.161] | 40.000 | 0 | 0 | 0 |
| S01_combined_backup | 20 | 0 | [0.000, 0.161] | 40.000 | 0 | 0 | 0 |
| S02_radar | 20 | 0 | [0.000, 0.161] | 7.771 | 0 | 0 | 0 |
| S02_camera | 20 | 0 | [0.000, 0.161] | 6.659 | 0 | 720 | 0 |
| S02_combined | 20 | 0 | [0.000, 0.161] | 7.354 | 0 | 0 | 0 |
| S02_combined_backup | 20 | 0 | [0.000, 0.161] | 7.354 | 0 | 0 | 0 |
| S03_radar | 20 | 0 | [0.000, 0.161] | 4.888 | 0 | 0 | 0 |
| S03_camera | 20 | 0 | [0.000, 0.161] | 5.345 | 0 | 720 | 0 |
| S03_combined | 20 | 0 | [0.000, 0.161] | 5.237 | 0 | 0 | 0 |
| S03_combined_backup | 20 | 0 | [0.000, 0.161] | 5.237 | 0 | 0 | 0 |
| S04_radar | 20 | 0 | [0.000, 0.161] | 20.263 | 0 | 0 | 0 |
| S04_camera | 20 | 0 | [0.000, 0.161] | 19.708 | 0 | 910 | 0 |
| S04_combined | 20 | 0 | [0.000, 0.161] | 20.263 | 0 | 0 | 0 |
| S04_combined_backup | 20 | 0 | [0.000, 0.161] | 20.263 | 0 | 0 | 0 |
| camera_unavailable | 10 | 0 | [0.000, 0.278] | 5.098 | 0 | 0 | 0 |
| both_unavailable | 10 | 10 | [0.722, 1.000] | 0.000 | 0 | 3770 | 0 |
| both_frozen | 10 | 10 | [0.722, 1.000] | 0.000 | 0 | 3660 | 0 |
| radar_ambiguity | 10 | 10 | [0.722, 1.000] | 0.000 | 0 | 5610 | 0 |
| common_bias | 10 | 10 | [0.722, 1.000] | 0.000 | 0 | 0 | 0 |
| fog | 10 | 0 | [0.000, 0.278] | 5.098 | 0 | 0 | 0 |
| occlusion | 10 | 0 | [0.000, 0.278] | 5.098 | 0 | 0 | 0 |
| camera_false_negative | 10 | 0 | [0.000, 0.278] | 5.098 | 0 | 0 | 0 |
| feedback_lost | 10 | 0 | [0.000, 0.278] | 5.237 | 0 | 0 | 0 |
| ecu_failed | 10 | 10 | [0.722, 1.000] | 0.000 | 0 | 0 | 0 |
| actuator_failed | 10 | 10 | [0.722, 1.000] | 0.000 | 0 | 0 | 0 |
| both_channels_lost | 10 | 10 | [0.722, 1.000] | 0.000 | 0 | 0 | 0 |
| intermittent | 10 | 0 | [0.000, 0.278] | 5.235 | 0 | 0 | 0 |
| delayed | 10 | 0 | [0.000, 0.278] | 4.323 | 0 | 0 | 0 |
| duplicate | 10 | 0 | [0.000, 0.278] | 5.237 | 0 | 0 | 0 |
| no_target | 10 | 0 | [0.000, 0.278] | 291.667 | 0 | 0 | 0 |
| radar_ghost | 10 | 0 | [0.000, 0.278] | 487.012 | 10 | 0 | 0 |
| common_ghost | 10 | 0 | [0.000, 0.278] | 487.012 | 10 | 0 | 0 |
| development | 48 | 10 | [0.117, 0.343] | 0.000 | 0 | 138 | 0 |
| holdout | 120 | 29 | [0.174, 0.326] | 0.000 | 0 | 357 | 0 |

| Case | First sensor loss / fault indication (s) | First brake command (s) | Command→active (ms) | Mean unavailable (s) | Degraded runs / successful without collision | CPU mean/max call (µs) |
|---|---|---|---|---|---|---|
| FI01_radar | 2.11 / feedback None / achieved None | None | None | 3.65 | 0 / 0 | 3.384 / 58.0 |
| FI01_camera | None / feedback None / achieved None | 3.5295 | 20.000000000000018 | 0.17 | 0 / 0 | 3.5195 / 50.0 |
| FI01_combined | 2.11 / feedback None / achieved None | 3.5295 | 20.000000000000018 | 0.0 | 20 / 20 | 3.5119 / 39.0 |
| FI01_combined_backup | 2.11 / feedback None / achieved None | 3.5295 | 20.000000000000018 | 0.0 | 20 / 20 | 3.6282 / 73.0 |
| FI02_radar | None / feedback 4.32 / achieved 4.6235 | 3.55 | 20.000000000000018 | 1.8709 | 0 / 0 | 3.5838 / 45.0 |
| FI02_camera | None / feedback 4.32 / achieved 4.6305 | 3.5295 | 20.000000000000018 | 2.0741 | 0 / 0 | 3.5689 / 58.0 |
| FI02_combined | None / feedback 4.32 / achieved 4.6285 | 3.529 | 20.000000000000018 | 1.8954 | 0 / 0 | 3.5451 / 39.0 |
| FI02_combined_backup | None / feedback None / achieved None | 3.529 | 20.000000000000018 | 0.0 | 0 / 0 | 3.5236 / 56.0 |
| S01_radar | None / feedback None / achieved None | None | None | 0.0 | 0 / 0 | 3.4809 / 71.0 |
| S01_camera | None / feedback None / achieved None | None | None | 0.17 | 0 / 0 | 3.4866 / 56.0 |
| S01_combined | None / feedback None / achieved None | None | None | 0.0 | 0 / 0 | 3.4811 / 63.0 |
| S01_combined_backup | None / feedback None / achieved None | None | None | 0.0 | 0 / 0 | 3.581 / 66.0 |
| S02_radar | None / feedback None / achieved None | 2.1275 | 20.000000000000018 | 0.0 | 0 / 0 | 3.4974 / 50.0 |
| S02_camera | None / feedback None / achieved None | 2.1225 | 20.000000000000018 | 0.17 | 0 / 0 | 3.6408 / 64.0 |
| S02_combined | None / feedback None / achieved None | 2.163 | 20.000000000000018 | 0.0 | 0 / 0 | 3.622 / 69.0 |
| S02_combined_backup | None / feedback None / achieved None | 2.163 | 20.000000000000018 | 0.0 | 0 / 0 | 3.5822 / 72.0 |
| S03_radar | None / feedback None / achieved None | 3.55 | 20.000000000000018 | 0.0 | 0 / 0 | 3.5656 / 39.0 |
| S03_camera | None / feedback None / achieved None | 3.5295 | 20.000000000000018 | 0.17 | 0 / 0 | 3.6224 / 56.0 |
| S03_combined | None / feedback None / achieved None | 3.529 | 20.000000000000018 | 0.0 | 0 / 0 | 3.5373 / 55.0 |
| S03_combined_backup | None / feedback None / achieved None | 3.529 | 20.000000000000018 | 0.0 | 0 / 0 | 3.5939 / 62.0 |
| S04_radar | None / feedback None / achieved None | 4.665 | 19.999999999999662 | 0.0 | 0 / 0 | 3.515 / 61.0 |
| S04_camera | None / feedback None / achieved None | 4.647 | 20.000000000000064 | 0.17 | 0 / 0 | 3.6678 / 82.0 |
| S04_combined | None / feedback None / achieved None | 4.6445 | 20.000000000000107 | 0.0 | 0 / 0 | 3.685 / 64.0 |
| S04_combined_backup | None / feedback None / achieved None | 4.6445 | 20.000000000000107 | 0.0 | 0 / 0 | 3.6212 / 40.0 |
| camera_unavailable | 2.0 / feedback None / achieved None | 3.534 | 20.000000000000018 | 0.0 | 10 / 10 | 3.5765 / 62.0 |
| both_unavailable | 2.0 / feedback None / achieved None | None | None | 3.76 | 0 / 0 | 3.47 / 56.0 |
| both_frozen | 2.11 / feedback None / achieved None | None | None | 3.65 | 0 / 0 | 3.4676 / 44.0 |
| radar_ambiguity | None / feedback None / achieved None | None | None | 5.68 | 0 / 0 | 3.4565 / 13.0 |
| common_bias | None / feedback None / achieved None | 5.692 | 20.000000000000018 | 0.0 | 0 / 0 | 3.5666 / 44.0 |
| fog | 0.16 / feedback None / achieved None | 3.534 | 20.000000000000018 | 0.0 | 10 / 10 | 3.6069 / 68.0 |
| occlusion | 0.16 / feedback None / achieved None | 3.534 | 20.000000000000018 | 0.0 | 10 / 10 | 3.5578 / 22.0 |
| camera_false_negative | None / feedback None / achieved None | 3.534 | 20.000000000000018 | 0.0 | 0 / 0 | 3.5687 / 42.0 |
| feedback_lost | None / feedback 2.11 / achieved None | 3.527 | 20.000000000000018 | 12.89 | 0 / 0 | 3.4408 / 53.0 |
| ecu_failed | None / feedback 3.11 / achieved 4.047 | 3.527 | None | 2.65 | 0 / 0 | 3.4489 / 31.0 |
| actuator_failed | None / feedback None / achieved 4.047 | 3.527 | None | 1.713 | 0 / 0 | 3.6463 / 35.0 |
| both_channels_lost | None / feedback 4.32 / achieved 4.639 | 3.527 | 20.000000000000018 | 1.9032 | 0 / 0 | 3.6516 / 53.0 |
| intermittent | None / feedback None / achieved None | 3.527 | 20.000000000000018 | 0.0 | 0 / 0 | 3.6091 / 51.0 |
| delayed | None / feedback 0.11 / achieved None | 3.527 | 190.00000000000026 | 14.89 | 0 / 0 | 3.6456 / 44.0 |
| duplicate | None / feedback None / achieved None | 3.527 | 20.000000000000018 | 0.0 | 0 / 0 | 3.8564 / 52.0 |
| no_target | None / feedback None / achieved None | None | None | 0.0 | 0 / 0 | 3.4725 / 40.0 |
| radar_ghost | None / feedback None / achieved None | 0.0 | 20.0 | 0.0 | 0 / 0 | 3.7445 / 61.0 |
| common_ghost | None / feedback None / achieved None | 0.0 | 20.0 | 0.0 | 0 / 0 | 3.5843 / 45.0 |
| development | 0.16 / feedback None / achieved None | 4.0089 | 44.090909090909065 | 0.0944 | 46 / 36 | 3.6669 / 72.0 |
| holdout | 0.16 / feedback None / achieved 0.85 | 3.3046 | 41.607142857142904 | 0.1178 | 119 / 90 | 3.6974 / 84.0 |

All timing columns use simulation-start reference; fault onset is stored in each case config.
FI01 freeze onset 2 s; last radar sample 1.95 s. Per-source loss detected at 2.11 s (110 ms from freeze, 160 ms from sample).
Software/actuator failure onset 3 s; sensor/common loss 2 s; both-channel loss 4.2 s.
Startup camera latency can cause early camera-only unavailability; distinguish it from a later injected failure.
Missed detection is counted per control cycle while a real target is within 120 m and no usable target exists.
Cached frames make these cycles correlated, not independent Bernoulli detections.
False intervention requires explicitly target_present=false; this does not classify all unnecessary braking in real traffic.
Intervals for repeated scenario seeds apply only to toy sensor randomness. Hold-out/development intervals are conditional
on the declared independent artificial uniform parameter samples, not a traffic population. No aggregate real-world rate is inferred.
Mean/max process CPU duration includes Python FFI and timing overhead and scheduler effects; not ECU-only execution or target WCET.
Baseline CPU/false-detection/unavailability metrics were not implemented; absent baseline values are not assumed zero.
Baseline v0.2.0 physical contact timing used endpoint checks; v0.3.0 resolves first within-step contact and stops at horizon.
Original inputs are identical; this numerical correction is disclosed rather than rewriting old results.
The held-out manifest was fixed before outcomes; failures are retained, and no post-outcome threshold tuning was performed.
