# Hazard to evidence links

| Event | Goal | Requirement | Component | Models | Tests |
|---|---|---|---|---|---|
| HE-01, HE-07 | SG-01 | SYS-REQ-001 | ADAS ECU, Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | ST-SLICE-001 PASS, ST-SLICE-002 PASS |
| HE-02 | SG-02 | SYS-REQ-002 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | ST-SLICE-003 PASS |
| HE-01, HE-07 | SG-01 | SYS-REQ-003 | ADAS ECU, Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | ST-SLICE-004 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-001 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-001 PASS, IT-ABI-003 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-002 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-004 PASS, ST-SLICE-001 PASS, ST-SLICE-003 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-003 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-002 PASS, UT-ADAS-005 PASS, ST-SLICE-001 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-004 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-003 PASS, UT-ADAS-006 PASS, UT-ADAS-007 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-005 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-007 PASS, ST-SLICE-001 PASS |
| HE-05 | SG-05 | ADAS-REQ-006 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-008 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-007 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-003 PASS, UT-ADAS-014 PASS, IT-ABI-004 PASS, ST-SLICE-006 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-008 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-016 PASS, UT-E2E-004 PASS |
| HE-03 | SG-03, SG-02 | ADAS-REQ-009 | ADAS ECU (Safety Supervisor function) | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-ADAS-011 PASS, UT-ADAS-017 PASS |
| HE-03 | SG-03, SG-02 | ADAS-REQ-010 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-012 PASS |
| HE-03 | SG-03, SG-02 | ADAS-REQ-011 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-013 PASS |
| HE-01, HE-07 | SG-01 | ADAS-REQ-012 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-015 PASS |
| HE-03 | SG-03, SG-02 | FSR-001 | ADAS ECU, Body Control Module | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-009 PASS, UT-ADAS-010 PASS, UT-SIM-004 PASS, ST-FI-001 PASS |
| HE-03 | SG-03, SG-02 | TSR-001 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-ADAS-009 PASS, UT-ADAS-010 PASS, UT-ADAS-017 PASS, ST-FI-001 PASS |
| HE-02 | SG-02 | TSR-002 | ADAS ECU, Brake ECU, Body Control Module | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-E2E-002 PASS, UT-E2E-003 PASS, ST-INV-001 PASS |
| HE-04 | SG-04 | TSR-003 | Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BRK-003 PASS, ST-FI-002 PASS |
| HE-02 | SG-02 | BRK-REQ-001 | Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BRK-001 PASS, UT-BRK-002 PASS, UT-BRK-007 PASS, UT-E2E-004 PASS, UT-E2E-005 PASS, ST-INV-001 PASS |
| HE-04 | SG-04 | BRK-REQ-002 | Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BRK-003 PASS, ST-FI-002 PASS |
| HE-01, HE-07 | SG-01 | BRK-REQ-003 | Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BRK-004 PASS |
| HE-01, HE-07 | SG-01 | BRK-REQ-004 | Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BRK-005 PASS |
| HE-01, HE-07 | SG-01 | BRK-REQ-005 | Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BRK-006 PASS, ST-SLICE-001 PASS |
| HE-06 | SG-06 | BCM-REQ-001 | Body Control Module | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BCM-001 PASS, ST-SLICE-001 PASS |
| HE-06 | SG-06 | BCM-REQ-002 | Body Control Module | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BCM-002 PASS |
| HE-06 | SG-06 | BCM-REQ-003 | Body Control Module | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BCM-003 PASS, ST-SLICE-001 PASS |
| HE-06 | SG-06 | BCM-REQ-004 | Body Control Module | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-BCM-004 PASS, UT-BCM-005 PASS, ST-FI-001 PASS |
| HE-01, HE-07 | SG-01 | SWR-001 | Simulation harness | models/context.puml, models/interfaces.puml, models/sequence.puml | IT-ABI-001 PASS, IT-ABI-002 PASS |
| HE-01, HE-07 | SG-01 | SWR-002 | ADAS ECU, Brake ECU, Body Control Module | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-E2E-001 PASS, IT-ABI-003 PASS |
| HE-01, HE-07 | SG-01 | SIM-REQ-001 | Simulation harness | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-SIM-001 PASS, UT-SIM-002 PASS |
| HE-01, HE-07 | SG-01 | SIM-REQ-002 | Simulation harness | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-SIM-003 PASS, UT-SIM-004 PASS, ST-SLICE-005 PASS |
| HE-01, HE-07 | SG-01 | SIM-REQ-003 | Virtual CAN bus | models/context.puml, models/interfaces.puml, models/sequence.puml | UT-SIM-005 PASS |
| HE-01, HE-07 | SG-01 | FSR-201 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-V2-001 PASS, ST-V2-001 PASS, ST-V2-002 PASS |
| HE-01, HE-07 | SG-01 | TSR-201 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-V2-001 PASS, ST-V2-001 PASS, ST-V2-002 PASS |
| HE-05 | SG-05 | FSR-202 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-V2-002 PASS, ST-V2-001 PASS |
| HE-05 | SG-05 | TSR-202 | ADAS ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-V2-002 PASS, ST-V2-001 PASS |
| HE-04 | SG-04 | FSR-203 | ADAS ECU, Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-V2-003 PASS, UT-V2-004 PASS, UT-V2-005 PASS, ST-V2-003 PASS, ST-V2-004 PASS |
| HE-04 | SG-04 | TSR-203 | ADAS ECU, Brake ECU | models/context.puml, models/interfaces.puml, models/sequence.puml, models/adas_states.puml | UT-V2-003 PASS, UT-V2-004 PASS, UT-V2-005 PASS, ST-V2-003 PASS, ST-V2-004 PASS |
