#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
OUT=results/v0.4.0
mkdir -p "$OUT"
cmake -S . -B build -DAEGIS_USE_MINITEST=ON -DCMAKE_BUILD_TYPE=Debug > "$OUT/build.log" 2>&1
cmake --build build -j4 >> "$OUT/build.log" 2>&1
./build/aegis_ecu_tests --gtest_output=json:"$OUT/cpp_test_results.json" > "$OUT/cpp-tests.log"
ctest --test-dir build --output-on-failure > "$OUT/ctest.log"
COVERAGE_FILE="$OUT/python.coverage" "$PYTHON" -m coverage run --branch --source=aegis_sim.security,aegis_sim.security_gateway -m pytest -o cache_dir="$PWD/.pytest_cache" tests/python -q --junitxml="$OUT/python_test_results.xml" > "$OUT/python-tests.log"
"$PYTHON" -m coverage json --data-file="$OUT/python.coverage" -o "$OUT/python_coverage.json"
"$PYTHON" -m coverage report --data-file="$OUT/python.coverage" > "$OUT/python_coverage.txt"
"$PYTHON" tools/experiment_v4.py
"$PYTHON" tools/report_v4.py
"$PYTHON" tools/trace_check.py --cpp-results "$OUT/cpp_test_results.json" --py-results "$OUT/python_test_results.xml" --out "$OUT"
"$PYTHON" tools/fuzz_security.py
AEGIS_MCDC=ON PYTHON="$PYTHON" scripts/coverage_llvm.sh "$OUT/coverage" > "$OUT/coverage-build.log" 2>&1
"$PYTHON" tools/coverage_inventory.py "$OUT"
if [[ -n "${SYSML_PILOT_HOME:-}" ]]; then scripts/validate_sysml_v4.sh > "$OUT/sysml-validation.log" 2>&1; fi
if [[ -n "${PLANTUML_JAR:-}" ]]; then
  shasum -a 256 models/v0.4.0/trust_boundaries.puml > "$OUT/uml-validation.log"
  java -jar "$PLANTUML_JAR" -checkonly models/v0.4.0/*.puml >> "$OUT/uml-validation.log" 2>&1
  java -jar "$PLANTUML_JAR" -tsvg models/v0.4.0/*.puml >> "$OUT/uml-validation.log" 2>&1
  echo UML_VALIDATION_PASS >> "$OUT/uml-validation.log"
fi
"$PYTHON" tools/check_v4.py
"$PYTHON" tools/release_v4.py
