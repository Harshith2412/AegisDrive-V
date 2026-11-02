#!/usr/bin/env python3
"""Integrity gate for documented educational evidence; not automotive approval."""
import hashlib,json,platform,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/v0.3.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def command(args):return subprocess.check_output(args,text=True).strip()
def main():
    subprocess.run([sys.executable,str(ROOT/'tools/check_v3.py')],check=True,cwd=ROOT)
    cpp=json.loads((OUT/'cpp_test_results.json').read_text())
    ct=[t for suite in cpp['testsuites'] for t in suite['testsuite']]
    py=list(ET.parse(OUT/'python_test_results.xml').getroot().iter('testcase'))
    assert len(ct)==45 and all(not t.get('failures') for t in ct)
    assert len(py)==34 and not any(list(t) for t in py)
    assert '100% tests passed' in (OUT/'ctest.log').read_text()
    coverage_log=(OUT/'coverage-build.log').read_text()
    assert 'mismatched data' not in coverage_log and 'error:' not in coverage_log and 'FAILED' not in coverage_log
    inventory=json.loads((OUT/'mcdc_conditions.json').read_text())
    assert sum(x['total'] for x in inventory)==195 and sum(x['covered'] for x in inventory)==127
    manifest=OUT/'case_manifest.json'
    assert sha(manifest)==(OUT/'case_manifest.sha256').read_text().strip()
    cases=json.loads(manifest.read_text());runs=json.loads((OUT/'experiment_runs.json').read_text())
    assert len(cases)==len(runs)==828
    for case,r in zip(cases,runs):
        assert case['seed']==r['seed'] and case['scenario']==r['config'] and case['split']==r['split']
        assert r['max_actual_decel_mps2']<=r['config']['mu']*9.81+1e-9
    summary=json.loads((OUT/'experiment_summary.json').read_text())
    for k in ['FI01_combined','FI02_combined_backup']:assert summary[k]['n']==20 and summary[k]['collisions']==0
    for k in ['FI01_radar','FI02_radar']:assert summary[k]['collisions']==20
    for k in ['actuator_failed','ecu_failed']:assert summary[k]['collisions']==10
    assert summary['radar_ghost']['false_interventions']==10
    assert summary['holdout']['n']==120
    assert 'SEMANTIC_ERRORS=0 WARNINGS=0' in (OUT/'sysml-validation.log').read_text()
    assert (ROOT/'models/v0.3.0/fault_containment.svg').exists()
    env=dict(release='0.3.0',client_date='2026-11-01',client_timezone='America/New_York',
      platform=platform.platform(),python=sys.version,compiler=command(['clang++','--version']),
      cmake=command(['cmake','--version']),llvm_cov=command(['xcrun','llvm-cov','--version']),
      java=subprocess.run(['java','-version'],capture_output=True,text=True).stderr,
      sysml_pilot=dict(version='0.63.1',release='2026-09.1',url='https://github.com/Systems-Modeling/SysML-v2-Pilot-Implementation/releases/download/2026-09.1/jupyter-sysml-kernel-0.63.1.zip'),
      test_frameworks='bundled minitest and pytest; Hypothesis property examples',
      untested='GoogleTest FetchContent, python-can, Linux v0.3.0',
      cpu_scope='process CPU around ctypes, not target ECU WCET')
    tools={'sysml_distribution':'/private/tmp/aegis-sysml.zip','sysml_jar':'/private/tmp/aegis-sysml/sysml/jupyter-sysml-kernel-0.63.1-all.jar','plantuml_jar':'/private/tmp/aegis-plantuml.jar'}
    for key,p in tools.items():
        if Path(p).exists():env[key+'_sha256']=sha(Path(p))
    (OUT/'environment.json').write_text(json.dumps(env,indent=2))
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'CHANGELOG.md',ROOT/'requirements-dev.txt']
    for d in ['ecu','sim','tests','tools','scripts','models','requirements','docs','scenarios']:
        files.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in str(p))
    (OUT/'source_manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))},indent=2))
    gate=dict(release='0.3.0',status='PASS: educational evidence integrity gate only',cpp_tests=45,python_tests=34,
      requirements_linked_to_passing_tests=44,sysml_files_semantically_validated=2,negative_control_rejected=True,
      candidate_runs=828,holdout_collisions=summary['holdout']['collisions'],holdout_runs=120,
      fi01=dict(radar_collisions=20,healthy_camera_collisions=0,runs=20),
      fi02=dict(primary_only_collisions=20,healthy_backup_collisions=0,runs=20),
      limitations='Shared ECU/actuator failures and false-positive ghosts remain hazardous. Sensor independence unproven. No compliance or certification claim.')
    (OUT/'release_gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
