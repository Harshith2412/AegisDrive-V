# AegisDrive-V

**Model-Based Automotive ECU Safety, Security and V-Model Validation Platform** — an open-source,
software-in-the-loop engineering project around an Automatic Emergency Braking (AEB) function, a simulated
Brake ECU and a Body Control Module.

> ⚠️ **Educational simulation only.** Not production software, not certified, no ISO 26262 / ISO 21448 /
> ISO/SAE 21434 compliance is claimed. Standards are used as *inspiration*; see `docs/`.

## Status — v1.0.0: Integrated Automotive Engineering Assurance Case Study

A reproducible C++/Python AEB research artifact integrating functional-safety, SOTIF,
cybersecurity, MBSE and V-model evidence. **Not a safe-vehicle approval, production ECU,
certification, homologation or standards-conformance claim.** Public test keys, trusted
local FFI/clock/state and point-mass simulation remain explicit limits.

[Executive summary](docs/v1.0.0_executive_summary.md) · [Release report](docs/v1.0.0_release.md) ·
[Reviewer workflow](docs/portfolio/reviewer_guide.md) · [Assurance case](docs/v1.0.0_assurance_case.md) ·
[Evaluation](results/v1.0.0/evaluation.md) · [Lifecycle audit](results/v1.0.0/lifecycle_trace.md) ·
[Presentation PDF](docs/portfolio/technical_presentation.pdf) · [Demo script](docs/portfolio/demo_script.md)

- Frozen v0.4.0: 92 tests and all 846 non-host-timing experiment outputs reproduced.
- Current: **100 tests pass; 53 requirements link to passing tests**. Five lifecycle gaps
  and unclosed vehicle objectives are reported separately from test status.
- All **18 strict/recovery security collisions** have individual sensor-to-impact timelines.
- Candidate adds newest-authenticated route selection and current-pressure diagnostic recovery;
  temporal/confidence/capped-braking profiles are studies, not a silently optimized default.
- Final stratified set: v0.4/candidate both **47/108 collisions**. Actual v0.3 supports only
  81 common cases; 27 security cases are explicitly unsupported. No aggregate safety gain claimed.
- Existing **29/120** and security **12/48 strict, 6/48 recovery** collisions remain visible.
- Official SysML semantic validation, static/UBSan checks and partial structural evidence
  are retained. ASan runtime is unvalidated after smoke/native timeouts.

Start with the release report and open issues before interpreting a passing test or coverage
percentage. This is the same automation in review roles, not an accredited external assessment.
Historical releases/results and hashed v0.1–v0.4 archives remain unchanged.

## Vertical slice in one picture
```
radar model ─► ADAS ECU (TTC, FSM, supervisor) ─CAN 0x120─► Brake ECU (validate, timeout, actuator) ─► ego vehicle
                    └────────────CAN 0x130──────► Body ECU ◄──CAN 0x220──┘   (brake lamps, FCW, hazard)
```
ADAS states: DISABLED · STANDBY · MONITORING · WARNING · BRAKING · DEGRADED · FAULT (26 legal transitions, all others rejected and logged).

## Historical v0.1.0 results (preserved; current comparison linked above)
| Scenario | Outcome (20 seeds) |
|---|---|
| S01 normal following | 0 warnings, 0 brake requests |
| S02 lead brakes 6 m/s² @ 50 km/h, 20 m gap | 0/20 collisions, but min gap only **0.58 m** (constant-velocity TTC limitation, OI-002) |
| S03 stationary target @ 50 km/h | 0/20 collisions, stops 2.4–2.6 m short; brake lamp 10 ms after brake active |
| S04 lead decelerates 1.5 m/s² | 0/20 collisions, but AEB **aborted and re-triggered** (OI-003) |
| FI01 radar freezes | detected within 160 ms → DEGRADED → FAULT; **collision 20/20** (single sensor, OI-006) |
| FI02 brake command loss | Brake ECU times out correctly; ADAS doesn't notice → **collision 20/20** (OI-001) |
| Sweep, stationary target | μ 0.9: 0 collisions 10–80 km/h · μ 0.5: collisions 100 % at ≥ 60 km/h (no friction awareness, OI-004) |
| Characterisation | forged frame with recomputed CRC **is accepted** → CRC ≠ security (OI-005, Phase 7) |

With 20 runs per point, "0 collisions" bounds the true rate only below ≈16 % (Wilson 95 %).

## Quick reviewer workflow (executed on macOS)

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip==26.2.2
.venv/bin/python -m pip install -r results/v1.0.0/dependencies.txt
scripts/reviewer.sh build
scripts/reviewer.sh test
scripts/reviewer.sh reference
# With pinned free tool downloads (see reviewer guide):
SYSML_PILOT_HOME=/path/to/sysml-0.63.1 PLANTUML_JAR=/path/to/plantuml.jar scripts/reviewer.sh models
scripts/reviewer.sh evaluate
scripts/reviewer.sh audit
```

No hosted URL/tag is claimed; the reviewer guide uses an explicit publication placeholder.
Default native build uses bundled minitest with no GoogleTest download. Archived-version
comparisons use isolated source/library builds; do not run historical release generators on
the current database. No commercial modeling tools, real CAN devices or external attack
networks are needed. ABI remains 4; rebuild native library/bindings together.

## Repository layout
```
docs/            00–04 Phase-0 baseline, 05 design, open issues, phase status, toolchain notes
ecu/include      C ABI types (aegis_types.h, aegis_c_api.h) + C++ headers
ecu/src          ADAS, Brake, Body ECUs, CAN codecs, E2E (CRC-8 + alive counter)
ecu/tests        GoogleTest-style unit tests (tagged TEST-ID / VERIFIES)
sim/aegis_sim    ctypes bindings, virtual CAN, vehicle & radar models, runner, plotting
scenarios        YAML scenarios S01–S04, FI01–FI02
requirements     requirements.yaml (machine-readable DB)
tests/python     integration / system / fault-injection tests
tools            experiment runner, traceability checker, report generator, fallback test runner
results          generated evidence (re-created by scripts/run_all.sh)
```

## Important honesty notes
* v0.1.0 evidence was produced in a Linux sandbox **without CMake, GoogleTest, pytest, pybind11 or python-can**
  (no network). The CMake path is written but was **not executed** there (OI-011). See `docs/toolchain_notes.md`.
* Timing numbers are host FFI wall-clock times, not ECU execution times.
* v0.1.0 MC/DC was not measured. v0.2.0 has partial LLVM MC/DC evidence; see the release record.

## License
MIT — see `LICENSE`.
