#!/usr/bin/env python3
import json,sys,hashlib,platform,subprocess,ssl
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/v1.0.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(args):return subprocess.check_output(args,text=True).strip()
def main():
 subprocess.run([sys.executable,str(ROOT/'tools/review/check.py')],cwd=ROOT,check=True)
 ct=json.loads((OUT/'cpp_test_results.json').read_text());cpp=[t for s in ct['testsuites'] for t in s['testsuite']]
 py=list(ET.parse(OUT/'python_test_results.xml').getroot().iter('testcase'))
 assert len(cpp)==46 and all(not t.get('failures') for t in cpp)
 assert len(py)==54 and not any(list(t) for t in py)
 assert '100% tests passed' in (OUT/'ctest.log').read_text()
 assert not any(x in (OUT/'coverage-build.log').read_text() for x in ('mismatched data','FAILED','error:'))
 assert 'error:' not in (OUT/'build.log').read_text().lower()
 analysis=json.loads((OUT/'quality/clang-analysis.json').read_text());assert len(analysis)==6 and all(x['returncode']==0 and not x['stderr'] for x in analysis)
 ub=json.loads((OUT/'quality/ubsan-result.json').read_text());assert ub['returncode']==0 and not ub['stderr']
 asan=json.loads((OUT/'quality/asan-investigation.json').read_text());assert 'smoke' in asan and 'ecu' in asan
 fuzz=json.loads((OUT/'quality/fuzz.json').read_text());assert fuzz['executions']==100000 and fuzz['unexpected_acceptance']==0
 audit=json.loads((OUT/'quality/dependency-audit-remediated.json').read_text());assert not any(x.get('vulns') for x in audit['dependencies'])
 comparison=json.loads((OUT/'comparison.json').read_text());candidate=comparison['profiles']['candidate']
 inventory=json.loads((OUT/'mcdc_conditions.json').read_text());covered=sum(x['covered'] for x in inventory);total=sum(x['total'] for x in inventory)
 assert covered<=total and total>0
 assert (ROOT/'docs/portfolio/technical_presentation.pdf').read_bytes().startswith(b'%PDF')
 env=dict(release='1.0.0',client_date='2026-11-01',client_timezone='America/New_York',platform=platform.platform(),python=sys.version,
   compiler=cmd(['clang++','--version']),cmake=cmd(['cmake','--version']),llvm=cmd(['xcrun','llvm-cov','--version']),openssl=ssl.OPENSSL_VERSION,
   sysml='Official pilot0.63.1 release2026-09.1',plantuml='1.2026.2',
   independence='Same automation in separate review roles, no accredited external assessor/blind third-party validation',
   sanitizer='UBSan executed; ASan build succeeded but smoke/native runtime timed out, no pass claimed',
   dependency_query='Public advisory service results retained before and after venv pip remediation; no vulnerability-free guarantee')
 for key,path in [('sysml_distribution','/private/tmp/aegis-sysml.zip'),('sysml_jar','/private/tmp/aegis-sysml/sysml/jupyter-sysml-kernel-0.63.1-all.jar'),('plantuml_jar','/private/tmp/aegis-plantuml.jar')]:
  if Path(path).exists():env[key+'_sha256']=sha(Path(path))
 (OUT/'environment.json').write_text(json.dumps(env,indent=2))
 files=[ROOT/'CMakeLists.txt',ROOT/'README.md',ROOT/'CHANGELOG.md',ROOT/'requirements-dev.txt']
 for d in ('ecu','sim','tests','tools','scripts','models','requirements','docs','scenarios'):
  files.extend(p for p in (ROOT/d).rglob('*') if p.is_file() and '__pycache__' not in str(p))
 (OUT/'source_manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in sorted(set(files))},indent=2))
 gate=dict(release='1.0.0',status='PASS: transparent educational research evidence gate; no automotive safety approval',
  cpp_tests=46,python_tests=54,requirements_with_passing_linked_tests=53,lifecycle_gaps=5,baseline_runs_reproduced=846,
  individual_security_failure_reports=18,final_case_manifest_count=108,final_candidate_collisions=candidate['collisions'],
  executed_final_version_runs=297,unsupported_v03_security_cases=27,perception_study_runs=200,locked_candidate_runs=216,
  native_mcdc_conditions=dict(covered=covered,total=total),asan='UNVALIDATED: runtime timeout',
  limitations='Shared physical/security dependencies, ghosts, trusted compromise, stale/both-path loss, grip/ODD/short gaps, model/lifecycle gaps and simulation-only evidence remain open; no certification, homologation or standards compliance.')
 (OUT/'release_gate.json').write_text(json.dumps(gate,indent=2))
 artifacts={str(p.relative_to(ROOT)):sha(p) for p in OUT.rglob('*') if p.is_file() and p.name!='artifact_manifest.json'}
 (OUT/'artifact_manifest.json').write_text(json.dumps(artifacts,indent=2));print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
