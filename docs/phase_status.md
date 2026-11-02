> Historical v0.1.0 record retained for comparison. Current v0.2.0 analysis and issue dispositions: [safety](v0.2.0_safety.md), [audit](v0.2.0_audit.md), [release](v0.2.0_release.md).

# Phase Status (v0.1.0)

Legend: ✅ completed with evidence · 🟡 partially completed · ⬜ not started

| Phase | Status | What exists | What does NOT exist yet |
|---|---|---|---|
| 0 Baseline & scope | ✅ | Charter, item definition, system boundary, ODD, assumptions/limitations (docs 00–04) | — |
| 1 MBSE / SysML | ⬜ | ASCII context diagram, state table, interface tables (informal) | SysML v2 model, PlantUML sources, SVGs, validation |
| 2 Requirements | 🟡 | 33 requirements (YAML, all mandatory fields), automated traceability checker, computed status | SEC-REQ, SOTIF-REQ; full FSR/TSR set; reviews |
| 3 Functional safety | 🟡 (mechanisms only) | Freshness, plausibility, timeout, E2E, illegal-transition detection, config check, DEGRADED/FAULT, DTCs — implemented and tested | HARA, ASILs, FSC/TSC documents, FMEA, FTA, safety argument |
| 4 C++ ECU software | 🟡 | ADAS, Brake, Body ECUs, codecs, E2E, C ABI; 34 unit tests (100 % line, 78.7 % branch-taken coverage) | camera/fusion interface, watchdog simulation, DTC memory/logging |
| 5 Vehicle & sensor sim | 🟡 | Longitudinal model, radar model, S01–S04, FI01–FI02, static viewer (PNG) | camera model, S05–S10 as dedicated scenarios |
| 6 SOTIF | ⬜ | (friction sweep is a preliminary input only) | everything |
| 7 Cybersecurity | ⬜ | characterisation of the CRC gap (ST-INV-002) | TARA, authentication, A01–A07 |
| 8 V-model V&V | 🟡 | unit / integration / system / fault-injection tests, coverage script, traceability | mutation & property-based testing, MC/DC investigation on Clang, formal V&V plan |
| 9 Quantitative evaluation | ⬜ (preliminary sweep only) | 20-seed scenario summary + speed×friction sweep with Wilson CIs | RQ1–RQ5 experiment design |
| 10 Traceability & safety case | 🟡 | requirement → implementation → test → result matrix | hazard/SOTIF/threat chains, assurance argument |
| 11 Presentation | 🟡 | README, report, plots | dashboard, demo script, résumé summary |
| 12 Extensions | ⬜ | — | — |
