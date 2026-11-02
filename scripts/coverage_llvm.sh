#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-.venv/bin/python}"
OUT="${1:-results/v1.0.0/coverage}"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"
cmake -S . -B build/llvm -DAEGIS_USE_MINITEST=ON -DAEGIS_LLVM_COVERAGE=ON -DAEGIS_MCDC="${AEGIS_MCDC:-OFF}" -DCMAKE_BUILD_TYPE=Debug
cmake --build build/llvm -j4
# Explicit cleanup prevents stale profiles contaminating a subsequent run.
find "$OUT" -name '*.profraw' -delete
LLVM_PROFILE_FILE="$OUT/unit-%p.profraw" ./build/llvm/aegis_ecu_tests
AEGIS_ECU_LIB="$PWD/build/llvm/libaegis_ecu.dylib" LLVM_PROFILE_FILE="$OUT/python-%p.profraw" "$PYTHON" -m pytest -o cache_dir="$PWD/.pytest_cache" tests/python -q
xcrun llvm-profdata merge -sparse "$OUT"/*.profraw -o "$OUT/merged.profdata"
xcrun llvm-cov report build/llvm/aegis_ecu_tests -object build/llvm/libaegis_ecu.dylib -instr-profile="$OUT/merged.profdata" "$PWD"/ecu/src/*.cpp > "$OUT/summary.txt"
xcrun llvm-cov export build/llvm/aegis_ecu_tests -object build/llvm/libaegis_ecu.dylib -instr-profile="$OUT/merged.profdata" "$PWD"/ecu/src/*.cpp > "$OUT/coverage.json"
xcrun llvm-cov show build/llvm/aegis_ecu_tests -object build/llvm/libaegis_ecu.dylib -instr-profile="$OUT/merged.profdata" -format=html -output-dir="$OUT/html" -show-branches=count "$PWD"/ecu/src/*.cpp
if [[ "${AEGIS_MCDC:-OFF}" == "ON" ]]; then
  xcrun llvm-cov report build/llvm/aegis_ecu_tests -object build/llvm/libaegis_ecu.dylib -instr-profile="$OUT/merged.profdata" -show-mcdc-summary "$PWD"/ecu/src/*.cpp > "$OUT/mcdc-summary.txt"
fi
cat "$OUT/summary.txt"
