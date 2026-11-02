> Historical v0.1.0 record retained for comparison. Current v0.2.0 analysis and issue dispositions: [safety](v0.2.0_safety.md), [audit](v0.2.0_audit.md), [release](v0.2.0_release.md).

# 05 — Vertical Slice: Detailed Design

## 1. Execution model
All ECUs are deterministic step functions called every 10 ms with an explicit `now_ms`. No ECU reads a clock,
allocates memory in `step()`, throws exceptions, or keeps global state. Handles are allocated once through the C ABI.

Simulation step order (`sim/aegis_sim/runner.py`): bus advance → radar → ADAS → Brake → BCM → vehicle integration.
Consequence: ADAS decision at *t* reaches the Brake ECU at *t*+10 ms; Brake status reaches the BCM at *t*+10 ms.

## 2. Algorithms (ADAS ECU)
- closing speed `c = -range_rate`
- `TTC = range / c` if `c > 0.5 m/s`, else `+inf`  (ADAS-REQ-001)
- required decel `a_req = c² / (2·max(range − 2.0 m, 0.1 m))`  (ADAS-REQ-003)
- brake demand `clamp(1.2·a_req, 4.0, 9.0) m/s²`; emergency flag if demand ≥ 6.0 m/s²
- freshness: sample stale if `now − ts > 150 ms`; future timestamps implausible (TSR-001, ADAS-REQ-009)

## 3. ADAS state machine
| From \ To | DIS | STB | MON | WRN | BRK | DEG | FLT |
|---|---|---|---|---|---|---|---|
| DISABLED   | – | ✔ |   |   |   |   |   |
| STANDBY    | ✔ | – | ✔ |   |   | ✔ | ✔ |
| MONITORING | ✔ | ✔ | – | ✔ | ✔ | ✔ | ✔ |
| WARNING    | ✔ | ✔ | ✔ | – | ✔ | ✔ | ✔ |
| BRAKING    | ✔ | ✔ | ✔ |   | – | ✔ | ✔ |
| DEGRADED   | ✔ | ✔ |   |   |   | – | ✔ |
| FAULT      | ✔ |   |   |   |   |   | – |

26 allowed transitions. Notable *illegal* transitions: STANDBY→BRAKING/WARNING (must pass MONITORING),
DEGRADED→MONITORING/BRAKING (recovery only via STANDBY), FAULT→anything except DISABLED, BRAKING→WARNING.

Guards:
| Transition | Condition |
|---|---|
| any → DISABLED | function_enabled = 0 |
| DISABLED → STANDBY | function_enabled = 1 |
| STANDBY → MONITORING | ego speed in [10, 80] km/h |
| MONITORING/WARNING → STANDBY | ego speed outside window |
| MONITORING → WARNING | TTC ≤ 2.6 s |
| MONITORING/WARNING → BRAKING | TTC ≤ 1.6 s |
| WARNING → MONITORING | TTC > 2.9 s |
| BRAKING → STANDBY | standstill (≤ 0.1 m/s) held ≥ 2000 ms |
| BRAKING → MONITORING | not closing and not at standstill for ≥ 500 ms |
| STB/MON/WRN/BRK → DEGRADED | any input check fails |
| DEGRADED → STANDBY | 10 consecutive valid cycles |
| DEGRADED → FAULT | DEGRADED for ≥ 1000 ms |
| (construction) → FAULT | invalid calibration (permanent) |

Output policy: brake request only in BRAKING; warning in WARNING/BRAKING; "unavailable" in DEGRADED/FAULT;
**on invalid inputs the brake request is released** (provisional — see FSR-001 rationale).

## 4. CAN frames (classic CAN, DLC 8, little-endian signals)
Common: byte0 = CRC-8 SAE J1850 (poly 0x1D, init 0xFF, xorout 0xFF) over [DataID lo, DataID hi, byte1..7];
byte1[3:0] alive counter; byte1[7:4] reserved = 0. DataID = CAN ID.

| ID | Name | byte2 | byte3–4 | other |
|---|---|---|---|---|
| 0x120 | BRAKE_REQ | b0 active, b1 emergency, b2–7 = 0 | decel, uint16, 0.01 m/s²/bit | bytes 5–7 = 0 |
| 0x130 | ADAS_STATUS | state (0–6) | byte3: b0 warning, b1 unavailable, b2 emergency, b3 standstill | bytes 4–7 = 0 |
| 0x220 | BRAKE_STATUS | b0 active, b1 timeout, b2 rejecting | actual decel, uint16, 0.01 m/s²/bit | bytes 5–7 = 0 |

Receiver rules: CRC error → reject; counter delta 0 → reject (repeated); delta > 2 → reject and re-sync;
first frame after start → sync only (not acted upon). Brake ECU additionally checks ID, DLC, reserved bits,
range (≤ 10 m/s²) and consistency (active ⇔ decel > 0).

## 5. Brake ECU
`target = max(driver, AEB)`; AEB demand = last valid command unless > 100 ms old (then 0, status TIMEOUT).
Actuator: `x += (target − x)(1 − e^(−dt/τ))`, τ = 0.15 s; invalid dt freezes the actuator. brake_active ⇔ x ≥ 0.3 m/s².

## 6. Body Control Module
Brake lamp = last valid brake_active (retained on timeout, fault flagged). FCW telltale = ADAS warning flag (off on
timeout). AEB-unavailable telltale = unavailable flag OR ADAS_STATUS timeout. Hazard lamps while (BRAKING ∧ emergency)
and 3000 ms afterwards (project policy).

## 7. Design decisions and trade-offs
1. **C ABI + ctypes instead of pybind11** — no build-time dependency, and the C ABI doubles as the seed of an
   embedded-style interface (Phase 12 item 8). Struct sizes are cross-checked at load (SWR-001).
2. **Release on invalid data** rather than hold or maximum braking — avoids H2 from frozen data at the cost of H1
   availability. FI01 shows the cost: with radar-only perception, a frozen radar ⇒ unmitigated collision.
3. **E2E ≠ security** — demonstrated by characterisation test ST-INV-002.
