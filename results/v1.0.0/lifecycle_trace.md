# Lifecycle traceability audit

53 requirements with computed linked-test status; vehicle objectives separately classified.

## Explicit lifecycle gaps

- L01: Legacy YAML parents reference charter/provisional hazards, not a complete explicit HARA->SG->FSR derivation graph. OPEN: documentary allocations are reviewed supporting links, not retroactive normative derivation
- L02: SysML behavior is abstract and some units are encoded in names; no full controller/model behavioral equivalence or executed verification cases. OPEN
- L03: Text symbol/link existence and PASS tags do not independently prove acceptance scope or every natural-language obligation. OPEN: objective flags below
- L04: HARA S/E/C/ASIL proposals lack external exposure/controllability validation. OPEN: no substantiated ASIL or compliance finding
- L05: No target ECU timing, physical hardware, following-vehicle model or real image-domain validation. OPEN

| Requirement | Linked tests | Objective review | Scope / counterexample |
|---|---|---|---|
| SYS-REQ-001 | VERIFIED | SCOPE_AMBIGUOUS | Gap/response-distance conditions must constrain broad avoidance wording; final short-gap/ODD/low-grip counterexamples remain, while specified nominal acceptance tests pass. |
| SYS-REQ-002 | VERIFIED | INTENDED_OBJECTIVE_OPEN | Persistent ghosts and trusted malicious commands cause unnecessary braking despite nominal following tests passing. |
| SYS-REQ-003 | VERIFIED | TESTED_SCENARIOS_ONLY | S02/S04 acceptance samples pass, not a general lead-braking guarantee. |
| ADAS-REQ-001 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-002 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-003 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-004 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-005 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-006 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-007 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-008 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-009 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-010 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-011 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| ADAS-REQ-012 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| FSR-001 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| TSR-001 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| TSR-002 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| TSR-003 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BRK-REQ-001 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BRK-REQ-002 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BRK-REQ-003 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BRK-REQ-004 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BRK-REQ-005 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BCM-REQ-001 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BCM-REQ-002 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BCM-REQ-003 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| BCM-REQ-004 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SWR-001 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SWR-002 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SIM-REQ-001 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SIM-REQ-002 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SIM-REQ-003 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| FSR-201 | VERIFIED | ASSUMPTION_LIMITED | Stopping-distance planning assumes achievable deceleration; no measured friction estimator. |
| TSR-201 | VERIFIED | ASSUMPTION_LIMITED | Low adhesion/short-distance collisions remain; passing selected wet cases is not all-weather avoidance. |
| FSR-202 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| TSR-202 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| FSR-203 | VERIFIED | DETECTION_NOT_AVAILABILITY | Status/achieved diagnostics can pass while both-path/shared-actuator loss still collides. |
| TSR-203 | VERIFIED | DETECTION_NOT_AVAILABILITY | Diagnostic budgets are not demonstrated vehicle FTTIs or rescue guarantees. |
| SIM-301 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| PER-301 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| PER-302 | VERIFIED | FALSE_POSITIVE_OBJECTIVE_OPEN | Union policy retains isolated/persistent common ghosts; corroboration/temporal alternatives introduce true-obstacle collisions. |
| BRK-301 | VERIFIED | COMMON_DEPENDENCY_OPEN | Backup command transport shares ECU/actuator/security dependencies. |
| DIA-301 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SEC-401 | VERIFIED | AUTHENTICITY_SCOPE_ONLY | Valid-key compromise and plausible malicious intent are not prevented. |
| SEC-402 | VERIFIED | AVAILABILITY_TRADEOFF | Strict freshness and stale replacement can suppress legitimate braking; total retained-state loss is replay-vulnerable. |
| SEC-403 | VERIFIED | SEMANTIC_TRUST_OPEN | Authenticated implausible data is rejected, but plausible false data/dangerous authorized commands can pass. |
| SEC-404 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SEC-405 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| REC-501 | VERIFIED | ALGORITHM_TESTED_BENEFIT_LIMITED | Newer verified backup selected; no aggregate collision reduction demonstrated in final set. |
| REC-502 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
| SOT-501 | VERIFIED | EVALUATION_COMPLETE_OBJECTIVE_OPEN | Tradeoff study is evidence of limitations, not a false-braking solution. |
| QLT-501 | VERIFIED | SCOPED_EVIDENCE_ONLY | No general safety-goal closure is inferred from linked tests. |
