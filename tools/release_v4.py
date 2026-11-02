#!/usr/bin/env python3
"""Educational evidence-integrity gate, not vehicle security/safety approval."""
import json,hashlib,platform,subprocess,sys,ssl,hmac,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/v0.4.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args):return subprocess.check_output(args,text=True).strip()
def main():
    subprocess.run([sys.executable,str(ROOT/'tools/check_v4.py')],check=True,cwd=ROOT)
    cpp=json.loads((OUT/'cpp_test_results.json').read_text());ct=[t for s in cpp['testsuites'] for t in s['testsuite']]
    py=list(ET.parse(OUT/'python_test_results.xml').getroot().iter('testcase'))
    assert len(ct)==46 and all(not t.get('failures') for t in ct)
    assert len(py)==46 and not any(list(t) for t in py)
    assert '100% tests passed' in (OUT/'ctest.log').read_text()
    log=(OUT/'coverage-build.log').read_text();assert not any(x in log for x in ['mismatched data','FAILED','error:'])
    assert 'error:' not in (OUT/'build.log').read_text().lower()
    fuzz=json.loads((OUT/'fuzz-python.json').read_text());assert fuzz['executions']==20000 and fuzz['unexpected_acceptances']==0
    coverage=json.loads((OUT/'python_coverage.json').read_text())['totals']
    summary=json.loads((OUT/'experiment_summary.json').read_text())
    for attack in ['A01','A03','A04']:
        assert summary[f'attack_matrix/{attack}/A']['unnecessary_braking_runs']==5
        for m in 'BC':assert summary[f'attack_matrix/{attack}/{m}']['unnecessary_braking_runs']==0
    for m in 'ABC':
        assert summary[f'attack_matrix/A12/{m}']['unnecessary_braking_runs']==5
        assert summary[f'locked_v3_holdout/locked_v3_holdout/{m}']['collisions']==29
    assert summary['attack_matrix/A06/B']['collisions']==5 and summary['attack_matrix/A06/C']['collisions']==0
    for m in 'BC':assert sum(s['counts'].get('legitimate_rejected',0) for k,s in summary.items() if k.startswith('attack_free/') and k.endswith('/'+m))==0
    env=dict(release='0.4.0',client_date='2026-11-01',client_timezone='America/New_York',platform=platform.platform(),
       python=sys.version,compiler=cmd(['clang++','--version']),cmake=cmd(['cmake','--version']),llvm_cov=cmd(['xcrun','llvm-cov','--version']),
       java=subprocess.run(['java','-version'],capture_output=True,text=True).stderr,
       cryptography=dict(api='Python standard hmac.digest/compare_digest with SHA256',hmac_module=hmac.__file__,openssl=ssl.OPENSSL_VERSION,
                         test_keys='public fixtures only; no production provisioning'),
       sysml='official pilot 0.63.1 / release 2026-09.1',plantuml='1.2026.2',
       native_fuzzer='UNAVAILABLE: missing installed AppleClang libclang_rt.fuzzer_osx.a; build log retained',
       coverage_scope='C++ six source files; Python security modules separately; no Python MC/DC')
    for key,path in [('sysml_distribution','/private/tmp/aegis-sysml.zip'),('sysml_jar','/private/tmp/aegis-sysml/sysml/jupyter-sysml-kernel-0.63.1-all.jar'),('plantuml','/private/tmp/aegis-plantuml.jar')]:
        if Path(path).exists():env[key+'_sha256']=sha(Path(path))
    (OUT/'environment.json').write_text(json.dumps(env,indent=2))
    files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'CHANGELOG.md',ROOT/'requirements-dev.txt']
    for d in ['ecu','sim','tests','tools','scripts','models','requirements','docs','scenarios']:
        files.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in str(p))
    (OUT/'source_manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))},indent=2))
    gate=dict(release='0.4.0',status='PASS: educational evidence integrity only',cpp_tests=46,python_tests=46,
        requirements_with_passing_linked_tests=49,threat_chains=13,safety_security_cases=8,experiments=846,
        baseline_runs_reproduced=828,baseline_non_timing_mismatches=0,locked_holdout_collisions=dict(A=29,B=29,C=29),
        new_security_holdout_collisions={m:summary[f'new_security_holdout/new_security_holdout/{m}']['collisions'] for m in 'ABC'},
        python_security_branches=dict(covered=coverage['covered_branches'],total=coverage['num_branches']),
        limitations='Public test keys; trusted-producer/common dependency compromise; rejection availability costs; physical/SOTIF failures remain. No certification, ISO/SAE 21434 or AUTOSAR conformance claim.')
    (OUT/'release_gate.json').write_text(json.dumps(gate,indent=2));print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
