# Final engineering robustness evaluation

108 predefined cases: twelve strata ×9 parameter samples (manifest seed1100907). This is a declared stratified case study, not a random traffic population.
Actual archived v0.3.0 and v0.4.0 source/library builds are used. v0.3.0 has no security attack API: 27 cases are explicitly unsupported, never assigned invented outcomes.
Common comparison denominator is 81 cases. Candidate is C + newest-authenticated-route selection, legacy union perception; study filters are not the default.

| Stratum | v0.3 collisions/n | v0.4 collisions/n | Candidate collisions/n | Candidate unnecessary brake | Candidate max impact (m/s) |
|---|---|---|---|---|---|
| actuator | 9/9 | 9/9 | 9/9 | 0 | 12.137818282797657 |
| authentication_recovery | UNSUPPORTED | 0/9 | 0/9 | 0 | None |
| boundary | 4/9 | 4/9 | 4/9 | 0 | 22.5 |
| combined | UNSUPPORTED | 6/9 | 6/9 | 0 | 9.4287960690487 |
| communication_failure | 6/9 | 6/9 | 6/9 | 0 | 14.438848077192345 |
| ghost | 0/9 | 0/9 | 0/9 | 9 | None |
| hard_braking | 1/9 | 1/9 | 1/9 | 0 | 4.163628291703836 |
| low_friction | 5/9 | 5/9 | 5/9 | 0 | 13.271952310841366 |
| normal | 0/9 | 0/9 | 0/9 | 0 | None |
| security_attack | UNSUPPORTED | 4/9 | 4/9 | 0 | 13.65573689186231 |
| sensor_failure | 3/9 | 3/9 | 3/9 | 0 | 17.282974792340408 |
| shared_ecu | 9/9 | 9/9 | 9/9 | 0 | 16.00810961797778 |

Overall supported denominators: {'v0.3.0': (37, 81), 'v0.4.0': (47, 108), 'candidate': (47, 108)}
Strictly common 81-case comparison: {'v0.3.0': (37, 81), 'v0.4.0': (37, 81), 'candidate': (37, 81)}
All raw minimum gaps, impact speeds, missed interventions, timeout/achieved-response indicators, authentication decisions, legitimate rejection counts and host CPU times are retained in comparison.json and final_*.json.
Unnecessary-braking counts require target_present=false and achieved braking; a zero count with a real target does not establish justified timing/intensity. There is no following-vehicle model.
The candidate route preference is exercised but does not reduce the overall collision count in this final set. No aggregate safety improvement is claimed.

| Existing locked set | n | Candidate collisions | Wilson 95% interval (conditional illustrative noise/sample model) |
|---|---|---|---|
| locked_v3_holdout / C | 120 | 29 | [0.174, 0.326] |
| new_security_holdout / B | 48 | 12 | [0.149, 0.388] |
| new_security_holdout / C | 48 | 6 | [0.059, 0.247] |

These previously exposed sets are not unseen validation. Intervals describe conditional artificial sampling only; message counts are correlated and do not justify binomial attack-probability claims.
No binomial interval is assigned to the intentionally stratified 108-case aggregate. Exact counts per stratum/denominator are the defensible result. Physical impact uses relative speed only, not injury severity or crash energy without mass.

## Controlled perception/braking study

| Case | Profile | Collisions/n | Unnecessary braking/n | Max achieved decel | No request collisions |
|---|---|---|---|---|---|
| persistent_radar_ghost | union | 0/5 | 5/5 | 8.829 | 0 |
| persistent_radar_ghost | corroborated | 0/5 | 0/5 | 0.000 | 0 |
| persistent_radar_ghost | temporal | 0/5 | 5/5 | 8.829 | 0 |
| persistent_radar_ghost | low_confidence | 0/5 | 0/5 | 0.000 | 0 |
| persistent_radar_ghost | bounded_3mps2 | 0/5 | 5/5 | 3.000 | 0 |
| persistent_common_ghost | union | 0/5 | 5/5 | 8.829 | 0 |
| persistent_common_ghost | corroborated | 0/5 | 5/5 | 8.829 | 0 |
| persistent_common_ghost | temporal | 0/5 | 5/5 | 8.829 | 0 |
| persistent_common_ghost | low_confidence | 0/5 | 5/5 | 8.829 | 0 |
| persistent_common_ghost | bounded_3mps2 | 0/5 | 5/5 | 3.000 | 0 |
| brief_ghost | union | 0/5 | 5/5 | 3.916 | 0 |
| brief_ghost | corroborated | 0/5 | 0/5 | 0.000 | 0 |
| brief_ghost | temporal | 0/5 | 0/5 | 0.000 | 0 |
| brief_ghost | low_confidence | 0/5 | 0/5 | 0.000 | 0 |
| brief_ghost | bounded_3mps2 | 0/5 | 5/5 | 2.912 | 0 |
| genuine_close_camera_failed | union | 0/5 | 0/5 | 7.024 | 0 |
| genuine_close_camera_failed | corroborated | 5/5 | 0/5 | 0.000 | 5 |
| genuine_close_camera_failed | temporal | 0/5 | 0/5 | 7.919 | 0 |
| genuine_close_camera_failed | low_confidence | 5/5 | 0/5 | 0.000 | 5 |
| genuine_close_camera_failed | bounded_3mps2 | 5/5 | 0/5 | 3.000 | 0 |
| genuine_occluded | union | 0/5 | 0/5 | 4.217 | 0 |
| genuine_occluded | corroborated | 5/5 | 0/5 | 0.000 | 5 |
| genuine_occluded | temporal | 0/5 | 0/5 | 4.217 | 0 |
| genuine_occluded | low_confidence | 5/5 | 0/5 | 0.000 | 5 |
| genuine_occluded | bounded_3mps2 | 0/5 | 0/5 | 3.000 | 0 |
| genuine_low_confidence | union | 0/5 | 0/5 | 4.217 | 0 |
| genuine_low_confidence | corroborated | 5/5 | 0/5 | 0.000 | 5 |
| genuine_low_confidence | temporal | 0/5 | 0/5 | 4.217 | 0 |
| genuine_low_confidence | low_confidence | 5/5 | 0/5 | 0.000 | 5 |
| genuine_low_confidence | bounded_3mps2 | 0/5 | 0/5 | 3.000 | 0 |
| genuine_nominal | union | 0/5 | 0/5 | 4.253 | 0 |
| genuine_nominal | corroborated | 1/5 | 0/5 | 8.246 | 0 |
| genuine_nominal | temporal | 1/5 | 0/5 | 8.286 | 0 |
| genuine_nominal | low_confidence | 1/5 | 0/5 | 8.246 | 0 |
| genuine_nominal | bounded_3mps2 | 0/5 | 0/5 | 3.000 | 0 |
| genuine_fog | union | 0/5 | 0/5 | 4.217 | 0 |
| genuine_fog | corroborated | 5/5 | 0/5 | 0.000 | 5 |
| genuine_fog | temporal | 0/5 | 0/5 | 4.217 | 0 |
| genuine_fog | low_confidence | 5/5 | 0/5 | 0.000 | 5 |
| genuine_fog | bounded_3mps2 | 0/5 | 0/5 | 3.000 | 0 |

200 study runs, 216 locked-set candidate runs, and 297 actually supported final-version runs are distinct executed batches (713 runs), in addition to 846 baseline reproductions.
A prior study attempt is retained: confidence was initially lowered after the fusion gate without being consumed by native ADAS; the corrected study explicitly re-gates availability. No final-hold-out threshold tuning occurred.
Temporal/corroboration profiles can suppress brief/isolated ghosts while introducing genuine-obstacle misses/collisions. Persistent common ghosts remain. The 3 m/s² cap changes planning and emergency threshold as documented; no independent follower model exists.
Logical cryptographic computation delay remains zero. Host CPU timing includes interpreter/FFI/OS effects and is not ECU target WCET.
Recovery selection/time: verified requests are compared in the same 10 ms control step; per-path freshness policy remains B/C. Diagnostic pressure recovery requires 100 ms clear dwell; event traces/tests define transition timing, not a guaranteed collision rescue deadline.
