#!/usr/bin/env bash
# Fallback build without CMake/GoogleTest (used in the v0.1.0 development sandbox).
# Usage: scripts/build_nocmake.sh [--coverage]
set -euo pipefail
cd "$(dirname "$0")/.."
CXX="${CXX:-c++}"
WARN="-Wall -Wextra -Wpedantic -Wconversion -Wshadow -Werror"
mkdir -p build
case "$(uname -s)" in Darwin) LIB=build/libaegis_ecu.dylib; SHARED="-dynamiclib";; *) LIB=build/libaegis_ecu.so; SHARED="-shared";; esac
"$CXX" -std=c++17 -O2 $WARN -fPIC -fvisibility=hidden -Iecu/include $SHARED ecu/src/*.cpp -o "$LIB"
COV=""; OPT="-O0 -g"
if [[ "${1:-}" == "--coverage" ]]; then COV="--coverage"; fi
"$CXX" -std=c++17 $OPT $COV -Wall -Wextra -Wpedantic -Werror -Iecu/include -Ithird_party/minitest \
  ecu/src/*.cpp ecu/tests/*.cpp third_party/minitest/minitest_main.cpp -o build/aegis_ecu_tests
echo "built $LIB and build/aegis_ecu_tests (minitest fallback)"
