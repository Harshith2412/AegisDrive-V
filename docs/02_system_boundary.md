# 02 — System Boundary

```
 ┌──────────────────────────── SIMULATED ENVIRONMENT (Python) ────────────────────────────┐
 │  Lead vehicle model     Ego vehicle model (+ inattentive driver)     Road (mu)          │
 │        │  true gap / relative speed            ▲ decel (friction-limited)               │
 │        ▼                                       │                                        │
 │  Radar sensor model (noise, period, latency, faults)                                    │
 └────────┬───────────────────────────────────────┼────────────────────────────────────────┘
          │ object + timestamp                    │ actuator decel
 ┌────────▼───────────────── ITEM UNDER DEVELOPMENT (C++ via C ABI) ──┼───────────────────┐
 │  ADAS ECU (TTC, FSM, safety supervisor) ── CAN 0x120 ──► Brake ECU (validate, timeout, │
 │        │                                                   arbitrate, actuator model)  │
 │        └──────────── CAN 0x130 ──► Body Control Module ◄── CAN 0x220 ──┘               │
 └──────────────────────────────────────────────────────────────────────────────────────────┘
          Virtual CAN bus (Python, deterministic, 1-cycle latency, logged, fault hooks)
```

## Inside the simulation (and inside the item)
ADAS ECU logic, Brake ECU logic and actuator model, BCM logic, CAN payload encoding/decoding and E2E checks —
all **compiled C++**, the only implementation of these algorithms.

## Inside the simulation (environment, outside the item)
Vehicle dynamics, driver model, radar model, virtual CAN transport, fault-injection hooks, test orchestration,
evidence collection. These are **test infrastructure**; their fidelity limits the meaning of all results.

## Outside the simulation
Real sensors and their signal processing; camera (planned); sensor fusion (planned); real CAN controllers,
bit timing, arbitration and error frames; gateways and security modules (planned as models in Phase 7);
OS scheduling, interrupts, memory protection, power supply, EMC; HMI design; legal/regulatory requirements.

## Simulated vs. production software (explicit distinction)
| Aspect | This project | Production ECU software |
|---|---|---|
| Execution | step function called from Python, host CPU | RTOS tasks, timing-protected, target MCU |
| Timing | logical time, perfect periodicity | jitter, WCET analysis required |
| Data | doubles, host endianness | fixed-point/float per MCU, defined byte order |
| Process | single developer, informal reviews | ISO 26262 process, independent assessment |
| Tooling | GCC/Clang, unqualified | qualified/confidence-assessed tools |
