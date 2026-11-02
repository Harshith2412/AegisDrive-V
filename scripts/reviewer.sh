#!/usr/bin/env bash
# Free local reviewer workflow; no historical result generators are invoked.
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
OUT=results/v1.0.0
mkdir -p "$OUT"
case "${1:-reference}" in
  build)
    cmake -S . -B build -DAEGIS_USE_MINITEST=ON -DCMAKE_BUILD_TYPE=Debug > "$OUT/build.log" 2>&1
    cmake --build build -j4 >> "$OUT/build.log" 2>&1 ;;
  test)
    ./build/aegis_ecu_tests --gtest_output=json:"$OUT/cpp_test_results.json" > "$OUT/cpp-tests.log"
    ctest --test-dir build --output-on-failure > "$OUT/ctest.log"
    "$PYTHON" -m pytest -o cache_dir="$PWD/.pytest_cache" tests/python -q --junitxml="$OUT/python_test_results.xml" > "$OUT/python-tests.log"
    "$PYTHON" tools/trace_check.py --cpp-results "$OUT/cpp_test_results.json" --py-results "$OUT/python_test_results.xml" --out "$OUT" ;;
  models)
    scripts/validate_sysml_v1.sh > "$OUT/sysml-validation.log" 2>&1
    : "${PLANTUML_JAR:?Set free PlantUML jar path}"
    shasum -a 256 models/v1.0.0/*.puml > "$OUT/uml-validation.log"
    java -jar "$PLANTUML_JAR" -checkonly models/v1.0.0/*.puml >> "$OUT/uml-validation.log" 2>&1
    java -jar "$PLANTUML_JAR" -tsvg models/v1.0.0/*.puml >> "$OUT/uml-validation.log" 2>&1
    echo UML_VALIDATION_PASS >> "$OUT/uml-validation.log" ;;
  reference) "$PYTHON" tools/review/reference.py ;;
  evaluate)
    "$PYTHON" tools/review/design.py
    for version in v0.3.0 v0.4.0; do
      "$PYTHON" tools/review/freeze_extract.py "$version"
      cmake -S "build/frozen/$version" -B "build/frozen/$version/build" -DAEGIS_USE_MINITEST=ON -DCMAKE_BUILD_TYPE=Debug > "$OUT/baseline/frozen-$version.log" 2>&1
      cmake --build "build/frozen/$version/build" -j4 >> "$OUT/baseline/frozen-$version.log" 2>&1
      "$PYTHON" tools/review/worker.py "$version"
    done
    "$PYTHON" tools/review/worker.py candidate
    "$PYTHON" tools/review/studies.py
    "$PYTHON" tools/review/report.py ;;
  audit)
    "$PYTHON" tools/review/lifecycle.py
    "$PYTHON" tools/review/assurance_case.py
    "$PYTHON" tools/review/check.py
    "$PYTHON" tools/review/release.py ;;
  *) echo 'usage: scripts/reviewer.sh build|test|models|reference|evaluate|audit' >&2;exit 2 ;;
esac
