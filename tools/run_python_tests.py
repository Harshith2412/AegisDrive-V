#!/usr/bin/env python3
"""Fallback test runner for tests/python (used when pytest is unavailable).

The tests are plain pytest-style functions (no fixtures/marks), so `pytest tests/python`
is the preferred runner where pytest is installed. This runner discovers `test_*`
functions, executes them, and writes a JSON report consumed by tools/trace_check.py.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results" / "python_test_results.json"
    test_dir = ROOT / "tests" / "python"
    sys.path.insert(0, str(test_dir))
    results, failed = [], 0
    for path in sorted(test_dir.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for name in sorted(n for n in dir(mod) if n.startswith("test_") and callable(getattr(mod, n))):
            t0 = time.perf_counter()
            err = None
            try:
                getattr(mod, name)()
            except Exception:  # noqa: BLE001 - report every failure
                err = traceback.format_exc()
            dt = time.perf_counter() - t0
            ok = err is None
            failed += 0 if ok else 1
            print(f"[{'  OK  ' if ok else 'FAILED'}] {path.name}::{name} ({dt:.2f}s)")
            if err:
                print(err)
            results.append({"file": path.name, "name": name, "passed": ok, "time_s": round(dt, 4), "error": err})
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"framework": "aegis-fallback-runner", "tests": results}, indent=2))
    print(f"{len(results)} tests, {failed} failed -> {out_path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
