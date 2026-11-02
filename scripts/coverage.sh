#!/usr/bin/env bash
# Statement + branch coverage of the C++ ECU core from the C++ unit tests (GCC gcov).
# MC/DC is NOT measured (see docs/toolchain_notes.md).
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf build/cov && mkdir -p build/cov results
CXX="${CXX:-g++}"
( cd build/cov && "$CXX" -std=c++17 -O0 -g --coverage -I../../ecu/include -I../../third_party/minitest \
    ../../ecu/src/*.cpp ../../ecu/tests/*.cpp ../../third_party/minitest/minitest_main.cpp -o tests_cov \
  && ./tests_cov > /dev/null )
( cd build/cov && gcov -b -c $(ls *.gcda | grep -E '^tests_cov-(adas_ecu|brake_ecu|body_ecu|codec|e2e)\.gcda$') ) \
  | tee build/cov/gcov_summary.txt > /dev/null
python3 - <<'PY'
import re, json
txt = open("build/cov/gcov_summary.txt").read()
out = {}
for block in txt.split("File '")[1:]:
    name = block.split("'")[0]
    if "/ecu/src/" not in name: continue
    g = lambda k: re.search(k + r":\s*([\d.]+)% of (\d+)", block)
    lines, br, taken = g("Lines executed"), g("Branches executed"), g("Taken at least once")
    out[name.split("/ecu/src/")[1]] = {"line_pct": float(lines.group(1)), "lines": int(lines.group(2)),
        "branch_taken_pct": float(taken.group(1)) if taken else None, "branches": int(taken.group(2)) if taken else 0}
tl = sum(v["lines"] for v in out.values()); tb = sum(v["branches"] for v in out.values())
out["TOTAL"] = {"line_pct": round(sum(v["line_pct"]*v["lines"] for v in out.values())/tl, 2), "lines": tl,
                "branch_taken_pct": round(sum((v["branch_taken_pct"] or 0)*v["branches"] for k,v in out.items() if k!="TOTAL")/tb, 2), "branches": tb}
out["_note"] = "GCC gcov on C++ unit tests only. Branch % = branches taken at least once. Includes compiler-generated branches. MC/DC not measured."
json.dump(out, open("results/cpp_coverage.json", "w"), indent=2)
for k, v in out.items():
    if k != "_note": print(f"{k:16s} lines {v['line_pct']:6.2f}% of {v['lines']:4d}   branches {v['branch_taken_pct']}% of {v['branches']}")
PY
