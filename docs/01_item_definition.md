> Historical v0.1.0 record retained for comparison. Current v0.2.0 analysis and issue dispositions: [safety](v0.2.0_safety.md), [audit](v0.2.0_audit.md), [release](v0.2.0_release.md).

# 01 — Item Definition (ISO 26262-inspired)

> Inspired by the *item definition* activity of the ISO 26262 concept phase. Content and structure are the
> project's own; no normative text is reproduced, and no conformance is claimed.

## 1. Item
**AEB item** = the function "Automatic Emergency Braking for rear-end collisions with an in-path vehicle",
realised by: perception (radar; camera planned), ADAS ECU (incl. safety supervisor function), Brake ECU,
Body Control Module (BCM), and the in-vehicle network connecting them.

## 2. Functional description
| Function | Description | Realised by |
|---|---|---|
| F1 Threat assessment | Compute time-to-collision (TTC) and the deceleration required to stop before the object. | ADAS ECU |
| F2 Forward collision warning | Warn the driver when TTC falls below a warning threshold. | ADAS ECU → BCM telltale |
| F3 Autonomous emergency braking | Request a bounded deceleration when TTC falls below a braking threshold; hold at standstill, then release. | ADAS ECU → Brake ECU |
| F4 Brake execution | Validate requests, arbitrate with driver demand, actuate, report status. | Brake ECU |
| F5 Braking signalling | Brake lamps from brake status; hazard lamps per project policy after emergency braking. | BCM |
| F6 Supervision | Detect stale/implausible inputs, communication loss and illegal states; degrade and inform the driver. | ADAS ECU, Brake ECU, BCM |

## 3. Operating modes (ADAS ECU)
DISABLED, STANDBY, MONITORING, WARNING, BRAKING, DEGRADED, FAULT — see `05_vertical_slice_design.md`.

## 4. Interfaces of the item
| Interface | Direction | Content (slice) |
|---|---|---|
| Radar object list | sensor → ADAS | range [m], range rate [m/s], object present, sensor ok, sampling timestamp [ms] |
| Ego speed | vehicle → ADAS | speed [m/s], valid flag, timestamp [ms] (direct in slice, not via CAN) |
| HMI enable switch | driver → ADAS | function_enabled |
| BRAKE_REQ 0x120 | ADAS → Brake | active, emergency, decel request [0.01 m/s²], CRC-8, alive counter |
| ADAS_STATUS 0x130 | ADAS → BCM | state, warning, unavailable, emergency, standstill, CRC-8, counter |
| BRAKE_STATUS 0x220 | Brake → BCM | brake active, timeout, rejecting, actual decel, CRC-8, counter |
| Driver brake pedal | driver → Brake | deceleration demand [m/s²] (always 0 in the slice) |
| Actuator | Brake ECU → plant | deceleration [m/s²] |
| Lamps / telltales | BCM → vehicle | brake lamps, hazard lamps, FCW telltale, AEB-unavailable telltale |

## 5. Known functional dependencies and assumptions
Driver remains responsible (assistance function); perception supplies the in-path object (no path prediction in
the slice); common time base across ECUs (LIM-TIME-01); the brake system can deliver up to the friction limit.

## 6. Potential hazards (to be analysed in the HARA — Phase 3, NOT YET PERFORMED)
H1 missed braking in a critical scenario · H2 unnecessary emergency braking · H3 Brake ECU accepts an invalid command ·
H4 brake lamps not activated · H5 ADAS continues on frozen sensor data · H6 safety-critical communication unavailable.
These are *candidate* hazards only; no severity/exposure/controllability or ASIL has been assigned.
