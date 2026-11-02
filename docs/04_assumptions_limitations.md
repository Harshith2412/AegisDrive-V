# 04 — Assumptions and Limitations

## Assumptions
| ID | Assumption |
|---|---|
| DRV-A-01 | The driver neither brakes nor steers in reaction to the threat or the warning. |
| DRV-A-02 | After AEB brings the vehicle to standstill, the driver keeps it stationary (driver target speed := 0). |
| A-TIME-01 | All ECUs and sensors share one time base (no clock drift/offset). |
| A-BUS-01 | Every frame is delivered exactly one 10 ms cycle after sending unless a fault hook drops/alters it. |
| A-SENS-01 | Radar reports the single in-path object; association and path prediction are perfect. |
| A-ACT-01 | Brake actuation is a first-order lag (tau 0.15 s); deliverable decel is capped at mu·g. |

## Limitations (all results must be read with these in mind)
| ID | Limitation | Consequence |
|---|---|---|
| LIM-ALG-01 | TTC assumes constant relative velocity. | Late reaction when the lead brakes (S02 margin only ~0.6 m). |
| LIM-ALG-02 | No friction estimation; demand clamp is friction-agnostic. | Collisions at mu 0.5 from 60 km/h (sweep). |
| LIM-VEH-01 | Point mass; no drag, grade, load transfer, tyre or ABS dynamics. | Stopping distances optimistic vs. reality. |
| LIM-SENS-01 | Gaussian noise only; no clutter, ghost targets, occlusion, misclassification. | SOTIF effects not yet represented. |
| LIM-BUS-01 | No CAN arbitration, error frames, bus-off, or bus load. | Timing results are logical, not physical. |
| LIM-TIME-01 | Logical time; ECU execution time not modelled. | Measured µs values are host FFI timings, not WCET. |
| LIM-SEC-01 | CRC/counter are safety mechanisms only; no authentication yet. | Forged frames with valid CRC are accepted (OI-005). |
| LIM-STAT-01 | 20 seeds per point; noise is small so outcomes are nearly deterministic. | 0/20 failures ⇒ 95 % upper bound ≈ 16 %; no low-rate claims possible. |
| LIM-TOOL-01 | Development sandbox lacked CMake, GoogleTest, pybind11, pytest, python-can. | Fallbacks used; see `toolchain_notes.md`. |
