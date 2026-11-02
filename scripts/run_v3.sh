#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
OUT=results/v0.3.0
mkdir -p "$OUT"
cmake -S . -B build -DAEGIS_USE_MINITEST=ON -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j4
./build/aegis_ecu_tests --gtest_output=json:"$OUT/cpp_test_results.json"
ctest --test-dir build --output-on-failure
"$PYTHON" -m pytest -o cache_dir="$PWD/.pytest_cache" tests/python -q --junitxml="$OUT/python_test_results.xml"
"$PYTHON" tools/experiment_v3.py
"$PYTHON" tools/report_v3.py
"$PYTHON" tools/trace_check.py --cpp-results "$OUT/cpp_test_results.json" --py-results "$OUT/python_test_results.xml" --out "$OUT"
AEGIS_MCDC=ON PYTHON="$PYTHON" scripts/coverage_llvm.sh "$OUT/coverage"
"$PYTHON" tools/coverage_inventory.py
if [[ -n "${SYSML_PILOT_HOME:-}" ]]; then
  scripts/validate_sysml.sh > "$OUT/sysml-validation.log" 2>&1
fi
if [[ -n "${PLANTUML_JAR:-}" ]]; then
  scripts/validate_uml_v3.sh > "$OUT/uml-validation.log" 2>&1
fi
"$PYTHON" tools/check_v3.py
"$PYTHON" tools/release_v3.py
