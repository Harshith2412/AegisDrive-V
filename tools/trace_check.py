#!/usr/bin/env python3
"""Automated traceability checker for AegisDrive-V.

Inputs
  requirements/requirements.yaml            requirement database
  ecu/tests/*.cpp, tests/python/test_*.py   tests tagged "TEST-ID: X | VERIFIES: A, B" (or "| CHARACTERIZES: OI-n")
  C++ results  (GoogleTest --gtest_output=json, or the minitest fallback subset)
  Python results (fallback runner JSON, or pytest --junitxml)
  docs/open_issues.md                       issue IDs referenced by CHARACTERIZES tags

Checks (each failure is an ERROR, exit code 1)
  E1 missing/empty mandatory requirement fields         E6 test verifies unknown requirement
  E2 duplicate requirement or test IDs                  E7 requirement<->test link not bidirectional
  E3 orphan requirement (no or unknown parent)          E8 test has no executed result
  E4 requirement without tests                          E9 implementation reference missing (file or symbol)
  E5 requirement lists unknown test ID                  E10 CHARACTERIZES references unknown issue
Verification status is computed per requirement: VERIFIED / FAILED / NOT_RUN / NO_TESTS.
Outputs results/traceability_matrix.{md,json}.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANDATORY = ["id", "title", "description", "rationale", "parent", "acceptance_criteria", "allocated_to",
             "verification_method", "implementation", "tests", "verification_status"]
TAG = re.compile(r"TEST-ID:\s*([A-Z0-9-]+)\s*\|\s*(VERIFIES|CHARACTERIZES):\s*(.+)$")
CPP_TEST = re.compile(r"^\s*TEST\(\s*(\w+)\s*,\s*(\w+)\s*\)")
PY_TEST = re.compile(r"^\s*def\s+(test_\w+)\s*\(")


def parse_tests():
    tests = {}
    sources = [(p, CPP_TEST, "cpp") for p in sorted((ROOT / "ecu" / "tests").glob("*.cpp"))]
    sources += [(p, PY_TEST, "py") for p in sorted((ROOT / "tests" / "python").glob("test_*.py"))]
    dups = []
    for path, pattern, kind in sources:
        lines = path.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines):
            m = TAG.search(line)
            if not m:
                continue
            tid, rel, targets = m.group(1), m.group(2), [t.strip() for t in m.group(3).split(",") if t.strip()]
            exe = None
            for nxt in lines[i + 1:i + 4]:
                mm = pattern.match(nxt)
                if mm:
                    exe = f"{mm.group(1)}.{mm.group(2)}" if kind == "cpp" else f"{path.name}::{mm.group(1)}"
                    break
            if tid in tests:
                dups.append(tid)
            tests[tid] = {"id": tid, "kind": kind, "file": str(path.relative_to(ROOT)), "line": i + 1,
                          "executable": exe, "verifies": targets if rel == "VERIFIES" else [],
                          "characterizes": targets if rel == "CHARACTERIZES" else []}
    return tests, dups


def load_results(cpp_json: Path | None, py_results: Path | None):
    res = {}
    if cpp_json and cpp_json.exists():
        data = json.loads(cpp_json.read_text())
        for suite in data.get("testsuites", []):
            for t in suite.get("testsuite", []):
                res[f"{suite['name']}.{t['name']}"] = not t.get("failures")
    if py_results and py_results.exists():
        if py_results.suffix == ".xml":
            for tc in ET.parse(py_results).getroot().iter("testcase"):
                fname = Path(tc.get("file") or tc.get("classname", "").replace(".", "/") + ".py").name
                ok = not any(c.tag in ("failure", "error", "skipped") for c in tc)
                res[f"{fname}::{tc.get('name')}"] = ok
        else:
            for t in json.loads(py_results.read_text())["tests"]:
                res[f"{t['file']}::{t['name']}"] = bool(t["passed"])
    return res


def check_impl(ref: str) -> str | None:
    path, _, symbol = ref.partition("#")
    p = ROOT / path
    if not p.exists():
        return f"file not found: {path}"
    if symbol and symbol not in p.read_text(encoding="utf-8"):
        return f"symbol '{symbol}' not found in {path}"
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpp-results", type=Path, default=ROOT / "results" / "v1.0.0" / "cpp_test_results.json")
    ap.add_argument("--py-results", type=Path, default=ROOT / "results" / "v1.0.0" / "python_test_results.xml")
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "v1.0.0")
    args = ap.parse_args()

    db = yaml.safe_load((ROOT / "requirements" / "requirements.yaml").read_text(encoding="utf-8"))
    reqs, externals = db["requirements"], db.get("external_sources", {})
    issues = set(re.findall(r"\bOI-\d{3}\b", (ROOT / "docs" / "open_issues.md").read_text(encoding="utf-8")))
    tests, dup_tests = parse_tests()
    results = load_results(args.cpp_results, args.py_results)
    errors, ids = [], [r.get("id") for r in reqs]
    known = set(ids)

    for d in {i for i in ids if ids.count(i) > 1}:
        errors.append(("E2", d, "duplicate requirement id"))
    for d in dup_tests:
        errors.append(("E2", d, "duplicate test id"))
    for r in reqs:
        rid = r.get("id", "?")
        for f in MANDATORY:
            v = r.get(f)
            if v is None or (isinstance(v, (str, list)) and len(v) == 0):
                errors.append(("E1", rid, f"missing field '{f}'"))
        parents = r.get("parent") or []
        if not parents:
            errors.append(("E3", rid, "orphan: no parent"))
        for p in parents:
            if p not in known and p not in externals:
                errors.append(("E3", rid, f"unknown parent '{p}'"))
        if not r.get("tests"):
            errors.append(("E4", rid, "no tests"))
        for tid in r.get("tests") or []:
            if tid not in tests:
                errors.append(("E5", rid, f"unknown test '{tid}'"))
            elif rid not in tests[tid]["verifies"]:
                errors.append(("E7", rid, f"lists {tid}, but {tid} does not declare VERIFIES {rid}"))
        for ref in r.get("implementation") or []:
            if (msg := check_impl(ref)):
                errors.append(("E9", rid, msg))
    req_by_id = {r["id"]: r for r in reqs}
    for tid, t in tests.items():
        for rid in t["verifies"]:
            if rid not in known:
                errors.append(("E6", tid, f"verifies unknown requirement '{rid}'"))
            elif tid not in (req_by_id[rid].get("tests") or []):
                errors.append(("E7", tid, f"declares VERIFIES {rid}, but {rid} does not list it"))
        for oi in t["characterizes"]:
            if oi not in issues:
                errors.append(("E10", tid, f"unknown issue '{oi}'"))
        if t["executable"] is None or t["executable"] not in results:
            errors.append(("E8", tid, f"no executed result for {t['executable']}"))
        t["result"] = {True: "PASS", False: "FAIL"}.get(results.get(t["executable"]), "NOT_RUN")

    matrix = []
    for r in reqs:
        tr = [tests[t]["result"] for t in r.get("tests") or [] if t in tests]
        status = ("NO_TESTS" if not tr else "FAILED" if "FAIL" in tr else "NOT_RUN" if "NOT_RUN" in tr else "VERIFIED")
        matrix.append({"id": r["id"], "title": r["title"], "parent": r.get("parent"), "allocated_to": r.get("allocated_to"),
                       "implementation": r.get("implementation"), "tests": [
                           {"id": t, "result": tests[t]["result"] if t in tests else "MISSING",
                            "evidence": tests[t]["file"] + f":{tests[t]['line']}" if t in tests else None}
                           for t in r.get("tests") or []], "verification_status": status})

    args.out.mkdir(parents=True, exist_ok=True)
    counts = {s: sum(m["verification_status"] == s for m in matrix) for s in ("VERIFIED", "FAILED", "NOT_RUN", "NO_TESTS")}
    report = {"requirements": len(matrix), "tests_tagged": len(tests), "status_counts": counts,
              "errors": [{"code": c, "item": i, "message": m} for c, i, m in errors],
              "matrix": matrix, "characterization_tests": {k: v for k, v in tests.items() if v["characterizes"]}}
    (args.out / "traceability_matrix.json").write_text(json.dumps(report, indent=2))
    lines = ["# Traceability matrix (generated by tools/trace_check.py — do not edit)", "",
             f"Requirements: **{len(matrix)}** | tagged tests: **{len(tests)}** | "
             + " | ".join(f"{k}: **{v}**" for k, v in counts.items()), "",
             f"Checker errors: **{len(errors)}**", ""]
    for c, i, m in errors:
        lines.append(f"- `{c}` {i}: {m}")
    lines += ["", "| Requirement | Parent | Allocated to | Tests (result) | Status |", "|---|---|---|---|---|"]
    for m in matrix:
        tl = ", ".join(f"{t['id']} ({t['result']})" for t in m["tests"])
        lines.append(f"| {m['id']} — {m['title']} | {', '.join(m['parent'] or [])} | "
                     f"{', '.join(m['allocated_to'] or [])} | {tl} | **{m['verification_status']}** |")
    lines += ["", "## Characterisation tests (document known limitations; a PASS means the limitation is still present)", ""]
    for k, v in report["characterization_tests"].items():
        lines.append(f"- {k} -> {', '.join(v['characterizes'])} ({v['result']}) — {v['file']}:{v['line']}")
    (args.out / "traceability_matrix.md").write_text("\n".join(lines) + "\n")
    print(f"{len(matrix)} requirements, {len(tests)} tagged tests, status {counts}, {len(errors)} errors")
    for c, i, m in errors:
        print(f"  {c} {i}: {m}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
