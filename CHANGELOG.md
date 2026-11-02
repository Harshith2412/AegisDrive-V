# v1.0.0 — Integrated Automotive Engineering Assurance Case Study

- Froze/reproduced v0.4.0; all 846 non-host-timing outcomes match and all 18 security collisions have individual timelines captured before control changes.
- Added scoped newest-authenticated route arbitration and current-pressure/clear-dwell diagnostic recovery without weakening MAC/replay gates.
- Compared perception/braking alternatives with retained genuine-obstacle failures; default union perception remains unchanged.
- Added independent C ABI/physics/stateful replay oracles; 100 tests and 53 linked requirements pass, with objective/lifecycle gaps reported separately.
- Executed actual archived/current final comparisons, locked regressions and controlled studies; no aggregate collision improvement claimed.
- Produced structured assurance case, lifecycle audit, model/quality evidence, reviewer workflow, technical slides, demo script and resume summary.
- Retained ASan runtime timeouts, shared physical/security failures, ghosts, stale-path loss and simulation limitations; no automotive approval/compliance claim.

# v0.4.0 — Automotive Cybersecurity and Safety-Security Co-Engineering

- Preserved/reproduced v0.3.0 (79 tests, 828 matched non-timing experiment outputs).
- Added public-test-key HMAC-SHA256 CAN FD envelopes, sender authorization, replay/age/epoch checks and bounded authenticated recovery.
- Protected command, status and sensor ingress while retaining native CRC/plausibility checks; ABI 4 security diagnostic does not initiate blind braking.
- Added local A01–A12 injection, eight safety-security cases and 846 matched A/B/C runs including locked old and separate new hold-outs.
- Recorded TARA, five security requirements, official SysML validation, trace chains, Python branch coverage and 20,000 finite mutation-fuzz inputs.
- Retained false braking, trusted compromise, rejection availability costs and missing native libFuzzer runtime as explicit limitations.

# v0.3.0 — ADAS SOTIF, Fault Tolerance & Model Assurance

- Archived and reproduced v0.2.0 without rewriting historical results.
- Audited seed diversity, friction, time causality, contact detection and requirement scope.
- Added camera confidence/latency/FOV/failure models and health-aware single-target fusion.
- Added independently E2E-validated backup command input to the same Brake ECU/actuator (ABI 3).
- Added timestamped achieved-deceleration supervision; fixed warning activation outside speed bounds.
- Corrected within-step contact and horizon integration; added Hypothesis properties and regression cases.
- Recorded 828 experiments with diverse held-out cases and retained negative/failed outcomes.
- Parsed and semantically validated architecture plus all requirement allocations/verification relationships using the official SysML pilot.
- Documented SOTIF insufficiencies, fault containment, qualitative FMEA/FTA, coverage gaps and open issues.

# v0.2.0 — Functional Safety, MBSE and ECU Integration Assurance

- Preserved hashed v0.1.0 source/evidence; reproduced 53 baseline tests on macOS.
- Added validated brake execution/accepted-command feedback and unavailable indication (ABI 2).
- Added conservative stopping-distance trigger and sustained release evidence, retaining original TTC.
- Added 9 regression tests; 62 total tests and 39 linked requirements pass.
- Recorded provisional scenario HARA, goals, FSC/FSRs, TSC/TSRs, FMEA/FTA and residual risks.
- Added five parser-validated UML models and an explicitly unvalidated SysML v2 structural model.
- Recorded paired original/boundary/adverse scenarios and partial LLVM MC/DC/branch evidence.
- FI01/FI02 and very-low-friction collisions remain open; no compliance/certification claim.

# Changelog

## 0.1.0 — Phase 0 baseline + first executable vertical slice
### Added
- Phase-0 documents 00–04, design doc 05, open-issues register, phase status, toolchain notes.
- C++17 ECU core: ADAS ECU (TTC, required decel, 7-state FSM with transition table, input supervision,
  DTCs), Brake ECU (E2E + payload validation, timeout, arbitration, first-order actuator), Body ECU (brake lamp,
  FCW / unavailable telltales, hazard policy, timeouts), CAN codecs, CRC-8 SAE J1850 + alive counter.
- Restricted C ABI with struct-size self-check; Python ctypes bindings (no duplicated algorithms).
- Deterministic SiL harness, virtual CAN bus with drop/tamper hooks, scenarios S01–S04, FI01–FI02.
- Requirement database (33 requirements), traceability checker (E1–E10), generated matrix and report.
### Defects found and fixed during this increment (preserved for the record)
1. **Test defect** (UT-BRK-002): the test sender consumed alive-counter values on frames rejected before the E2E
   check, so the Brake ECU (correctly) reported a sequence error instead of the range error under test.
   Fixed in the test; ECU behaviour unchanged and now documented in design doc §4.
2. **Experiment-setup defect**: the first sweep used a fixed 80 m / 20 s geometry; at 10 km/h the run ended
   before the threat developed (no brake request). Sweep now scales gap and duration with speed.
3. **Coverage finding**: gcov showed ego-speed invalid / future-timestamp / stale branches of the supervisor
   were never executed by any test, plus an unused `to_string()` and an untested BCM ADAS_STATUS rejection path.
   Added UT-ADAS-017 and extended UT-BCM-005; removed dead code. Line coverage 96.8 % → 100 %.
4. **Test defect** (UT-BCM-005 extension): assertion ignored that the BCM retains the last *valid* warning flag;
   fixed the test preconditions.
### Verified manually (not yet automated)
- Traceability checker mutation check: five seeded defects (E1, E3, E5, E6, E9) were all reported, exit code 1.
### Known gaps
- See `docs/open_issues.md` OI-001…OI-013.
