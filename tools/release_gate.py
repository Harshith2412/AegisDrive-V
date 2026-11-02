#!/usr/bin/env python3
"""Evidence integrity gate for an educational release, not a safety approval."""
import hashlib
import json
import platform
import subprocess
import sys
import tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/v0.2.0'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args):return subprocess.check_output(args,text=True).strip()
def main():
    archive=ROOT/'baseline/v0.1.0/source-and-evidence.tar.gz'
    expected=(ROOT/'baseline/v0.1.0/SHA256SUMS').read_text().split()[0]
    assert sha(archive)==expected,'baseline archive changed'
    with tarfile.open(archive) as tf:
        for p in (ROOT/'scenarios').glob('*.yaml'):
            assert tf.extractfile(str(p.relative_to(ROOT))).read()==p.read_bytes(),'baseline scenario changed'
    cpp=json.loads((OUT/'cpp_test_results.json').read_text())
    tests=[t for suite in cpp['testsuites'] for t in suite['testsuite']]
    assert len(tests)==39 and all(not t.get('failures') for t in tests)
    import xml.etree.ElementTree as ET
    py=list(ET.parse(OUT/'python_test_results.xml').getroot().iter('testcase'))
    assert len(py)==23 and not any(list(t) for t in py)
    trace=json.loads((OUT/'traceability_matrix.json').read_text())
    assert trace['requirements']==39 and trace['status_counts']['VERIFIED']==39 and not trace['errors']
    models=json.loads((OUT/'models.json').read_text())
    assert len(models['uml'])==5
    for m in models['uml']:assert sha(ROOT/m['path'])==m['sha256']
    for loc in [ROOT/'baseline/v0.1.0/macos-rerun/vertical_slice_results.json',OUT/'scenarios/vertical_slice_results.json']:
        scenarios=json.loads(loc.read_text())
        assert len(scenarios['scenarios'])==6 and len(scenarios['sweep_stationary'])==16
        assert all(x['runs']==20 for x in scenarios['scenarios']+scenarios['sweep_stationary'])
    assert 'mismatched data' not in (OUT/'coverage-build.log').read_text()
    paired=json.loads((OUT/'comparison.json').read_text()); assert len(paired)==21
    assert all(r[v]['runs']==20 for r in paired for v in ['baseline','modified'])
    for p in ['coverage/summary.txt','coverage/mcdc-summary.txt','evaluation.md','safety_trace.json','build.log','ctest.txt']:
        assert (OUT/p).stat().st_size>0,p
    assert '100% tests passed' in (OUT/'ctest.txt').read_text()
    assert 'error:' not in (OUT/'build.log').read_text().lower()
    env=dict(release='0.2.0',client_date='2026-11-01',client_timezone='America/New_York',platform=platform.platform(),
             machine=platform.machine(),python=sys.version,compiler=cmd(['clang++','--version']),
             cmake=cmd(['cmake','--version']),llvm_cov=cmd(['xcrun','llvm-cov','--version']),
             build='CMake Debug, bundled minitest, strict warnings',pytest='executed',python_can='not installed/tested',
             baseline_sha256=expected,plantuml_version='1.2026.2',
             timing='deterministic 10 ms steps, 50 ms radar; shared monotonic simulation clock; host FFI durations not WCET')
    jar=Path('/private/tmp/aegis-plantuml.jar')
    if jar.exists():env['plantuml_jar_sha256']=sha(jar)
    (OUT/'environment.json').write_text(json.dumps(env,indent=2))
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'requirements-dev.txt']
    for d in ['ecu','sim','tests','tools','scripts','models','requirements','docs','scenarios']:
        files.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in str(p))
    manifest={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))}
    (OUT/'source_manifest.json').write_text(json.dumps(manifest,indent=2))
    gate=dict(release='0.2.0',status='PASS: educational evidence gate only',cpp_tests=39,python_tests=23,
              verified_requirements=39,uml_validated=5,sysml='UNVALIDATED',paired_runs_each_version=420,
              original_sweep_runs_each_version=320,baseline_archive_intact=True,original_scenario_inputs_identical=True,
              limitations='FI01/FI02 collisions, adhesion limits, confidence/redundancy/fallback issues remain open; no compliance claim')
    (OUT/'release_gate.json').write_text(json.dumps(gate,indent=2))
    print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
