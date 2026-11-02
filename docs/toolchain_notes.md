> Historical v0.1.0 record retained for comparison. Current v0.2.0 analysis and issue dispositions: [safety](v0.2.0_safety.md), [audit](v0.2.0_audit.md), [release](v0.2.0_release.md).

# Toolchain Notes

## Target environment (as specified)
macOS on Apple Silicon, VS Code, Python 3, C++17, CMake + Clang, open-source only.

## Primary build path (intended for macOS)
`CMakeLists.txt` builds `libaegis_ecu` (shared) and `aegis_ecu_tests` with **real GoogleTest** fetched via
`FetchContent` (pinned tag). Python tests run with **pytest**. `requirements-dev.txt` lists pytest, numpy,
matplotlib, PyYAML and (optional) python-can.

## Development sandbox actually used for v0.1.0 (Linux container, no network)
| Tool | Available | Used instead |
|---|---|---|
| g++ 13.3 | yes | builds via `scripts/build_nocmake.sh` with `-Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror` |
| CMake | **no** | `scripts/build_nocmake.sh` (CMakeLists.txt therefore **unverified**, OI-011) |
| GoogleTest | **no** | `third_party/minitest` — a ~100-line source-compatible fallback for the macros used |
| pybind11 | **no** | not needed: C ABI + ctypes (design decision, see doc 05 §7) |
| pytest | **no** | `tools/run_python_tests.py` (tests are plain pytest-style functions) |
| python-can | **no** | deterministic `InProcessCanBus`; `PythonCanBus` adapter provided but **untested** |
| gcov | yes | statement/branch coverage via `scripts/coverage.sh` |

## Coverage
Statement and branch coverage are measured with gcov (GCC). **MC/DC is not measured**: neither GCC 13 gcov nor
the tools available report MC/DC. (Recent Clang releases added MC/DC instrumentation for source-based coverage;
this has not been evaluated in this project.) High branch coverage is not claimed as MC/DC.

## SysML v2
Not started (Phase 1). No SysML tool was installed; nothing in this repository claims a validated SysML model.
