# 00 — Project Charter: AegisDrive-V

**Full title:** Model-Based Automotive ECU Safety, Security and V-Model Validation Platform
**Document status:** Baseline v0.1.0 (Phase 0) — living document
**Nature of the project:** Open-source *educational/portfolio* engineering project. It is **not** production
automotive software, is **not** certified to any standard, and must never be used in a vehicle.

## 1. Purpose
Demonstrate, with executable and reproducible evidence, how an Automatic Emergency Braking (AEB) function and
its supporting ECUs (ADAS ECU, Brake ECU, Body Control Module) are specified, implemented, analysed and verified
along an automotive V-model, including functional safety (ISO 26262-inspired), SOTIF (ISO 21448-inspired) and
cybersecurity (ISO/SAE 21434-inspired) workstreams.

## 2. Goals (referenced as parents in `requirements/requirements.yaml`)
| ID | Goal |
|----|------|
| CHARTER-G1 | The AEB function avoids, or mitigates, rear-end collisions with an in-path vehicle within the defined ODD. |
| CHARTER-G2 | The AEB function does not warn or brake when no collision threat exists. |
| CHARTER-G3 | The vehicle braking state is signalled to following traffic (brake lamps, hazard policy). |
| CHARTER-G4 | Every reported result is reproducible from the repository with documented seeds and versions. |

## 3. Success criteria for the whole project
1. Each requirement is traceable to implementation and to an executed test, by an automated checker.
2. Safety, SOTIF and security analyses are kept separate and cross-referenced, never conflated.
3. Baseline vs. defended configurations are compared on matched scenarios, including negative results.
4. No claim of compliance, certification, ASIL achievement or production readiness is made anywhere.

## 4. Scope
**In scope:** single ego vehicle, single lead vehicle, straight road, longitudinal dynamics only; radar (and later
camera) object-level sensor models; ADAS/Brake/Body ECU logic in C++; virtual CAN/CAN FD; SiL test and evidence
generation; analyses (HARA, FMEA, FTA, SOTIF, TARA) at the depth a single engineer can defend.

**Out of scope:** lateral control, multi-lane traffic (until optional SUMO extension), pedestrians/cyclists,
real ECU hardware, AUTOSAR stacks, HIL, real-time OS behaviour, tool qualification, production calibration.

## 5. Approach
Incremental, phase-by-phase (Phases 0–12), starting with a **working vertical slice**
(one lead + one ego vehicle → C++ AEB → one CAN command → Brake ECU reaction → Body ECU reaction → one passing
end-to-end test), then deepening safety, security and validation. Each phase records objective, deliverables,
executed commands, results, defects, limitations and traceability updates (`docs/phase_status.md`, `CHANGELOG.md`).

## 6. Engineering rules (binding)
No fabricated results; no invented ISO clauses or ASIL tables; standards are approximated and the approximation is
stated; failed experiments are preserved; planned work is never described as completed.

## 7. Risks to the project itself
| Risk | Mitigation |
|---|---|
| SysML v2 tooling not installable locally | Record as toolchain limitation; never claim the model validated. |
| Normative standard texts unavailable | Use only publicly documented concepts; mark mappings as approximate. |
| Evidence drifts from code | Traceability checker + generated reports are re-run by one command. |
| Scope creep | Optional extensions (Phase 12) only after core completion. |
