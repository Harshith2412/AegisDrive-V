#!/usr/bin/env python3
"""Independent review evidence integrity, not automotive risk acceptance."""
import hashlib,json,tarfile,re
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/v1.0.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 for version in ('v0.1.0','v0.2.0','v0.3.0','v0.4.0'):
  archive=ROOT/'baseline'/version/'source-and-evidence.tar.gz'
  assert sha(archive)==(archive.parent/'SHA256SUMS').read_text().split()[0]
 checked=0;native=0
 with tarfile.open(ROOT/'baseline/v0.4.0/source-and-evidence.tar.gz') as tf:
  for m in tf.getmembers():
   if not m.isfile() or Path(m.name).name.startswith('._'):continue
   if m.name.startswith(('results/v0.4.0/','results/v0.3.0/','results/v0.2.0/','scenarios/','ecu/src/','ecu/include/')):
    assert tf.extractfile(m).read()==(ROOT/m.name).read_bytes(),m.name
    checked+=1;native+=int(m.name.startswith(('ecu/src/','ecu/include/')))
 assert not json.loads((OUT/'baseline/source_integrity.json').read_text())['unexpected_changes']
 reproduction=json.loads((OUT/'baseline/reproduction.json').read_text());assert reproduction['runs']==846 and not reproduction['mismatches']
 failures=json.loads((OUT/'failure_analysis/index.json').read_text());assert failures['failures']==18
 assert failures['cause_counts']=={'B:counter_gap':4,'B:stale_authenticated_delivery':6,'C:stale_authenticated_delivery':6,'B:rollback_or_replay':2}
 for c in failures['cases']:
  d=json.loads((OUT/'failure_analysis'/f"{c['id']}.json").read_text())
  assert d['outcome']['collision'] and not d['comparison_A_collision'] and d['timeline']
  assert all('security_decisions' in row and 'brake_aeb_target' in row and 'sensor_measurements' in row for row in d['timeline'])
  assert (OUT/'failure_analysis'/f"{c['id']}.md").exists()
 trace=json.loads((OUT/'traceability_matrix.json').read_text());assert trace['requirements']==53 and trace['status_counts']['VERIFIED']==53 and not trace['errors']
 life=json.loads((OUT/'lifecycle_trace.json').read_text());assert life['requirements']==53 and len(life['lifecycle_gaps'])==5
 assert any(r['objective_status']=='INTENDED_OBJECTIVE_OPEN' for r in life['links'])
 paths=['models/v0.3.0/aegis.sysml','models/v0.3.0/requirements.sysml','models/v0.4.0/security.sysml','models/v1.0.0/review.sysml']
 log=(OUT/'sysml-validation.log').read_text();assert 'SEMANTIC_ERRORS=0 WARNINGS=0' in log and 'negative control correctly rejected' in log
 for p in paths:assert sha(ROOT/p)+'  '+p in log,p
 text='\n'.join((ROOT/p).read_text() for p in paths)
 db=yaml.safe_load((ROOT/'requirements/requirements.yaml').read_text())
 for r in db['requirements']:assert "requirement '"+r['id']+"'" in text,r['id']
 uml=(OUT/'uml-validation.log').read_text();assert 'UML_VALIDATION_PASS' in uml
 for p in (ROOT/'models/v1.0.0').glob('*.puml'):
  assert sha(p)+'  '+str(p.relative_to(ROOT)) in uml
  assert p.with_suffix('.svg').exists()
 # Native legal-state graph has not changed and still matches the model.
 source=(ROOT/'ecu/src/adas_ecu.cpp').read_text().split('constexpr bool kAllowed')[1].split('};')[0]
 rows=re.findall(r'/\*\s*(\w+)\s*\*/\s*\{([^}]+)\}',source);names=[r[0] for r in rows]
 edges={(names[i],names[j]) for i,(_,row) in enumerate(rows) for j,v in enumerate(re.findall(r'\b(true|false)\b',row)) if v=='true'}
 assert len(edges)==26 and edges==set(re.findall(r'^(\w+) --> (\w+) :',(ROOT/'models/adas_states.puml').read_text(),re.M))
 manifest=OUT/'final_case_manifest.json';assert sha(manifest)==(OUT/'final_case_manifest.sha256').read_text().strip()
 cases=json.loads(manifest.read_text())['cases'];assert len(cases)==108 and len({c['category'] for c in cases})==12
 for profile,expected in [('v0.3.0',81),('v0.4.0',108),('candidate',108)]:
  rs=json.loads((OUT/f'final_{profile}.json').read_text());assert len(rs)==108 and sum(r['supported'] for r in rs)==expected
  for case,r in zip(cases,rs):
   assert r['config']==case
   if r['supported']:assert r['max_actual_decel_mps2']<=case['scenario']['mu']*9.81+1e-9
 assert len(json.loads((OUT/'perception_study.json').read_text()))==200
 locked=json.loads((OUT/'locked_candidate.json').read_text());assert len(locked)==216
 for split,mode,n in [('locked_v3_holdout','C',120),('new_security_holdout','B',48),('new_security_holdout','C',48)]:
  assert len([r for r in locked if r['split']==split and r['security_config']['mode']==mode])==n
 # Original locked set parameters/seeds are rechecked, never relabeled unseen.
 old={r['scenario']['id']:r for r in json.loads((ROOT/'results/v0.4.0/case_manifest.json').read_text()) if r['split']=='locked_v3_holdout'}
 for r in locked:
  if r['split']=='locked_v3_holdout':assert r['original_config']==old[r['scenario_id']]['scenario'] and r['seed']==old[r['scenario_id']]['seed']
 for c in json.loads((OUT/'assurance_case.json').read_text())['claims']:
  assert c['counterexamples'] and c['evidence']
  for ref in c['evidence']:assert (ROOT/ref).exists(),ref
 result=dict(historical_files_checked=checked,native_source_files_unchanged=native,baseline_reproduced=846,individual_failures=18,
  linked_requirements=53,lifecycle_gaps=5,model_files_validated=4,legal_state_edges=26,executed_final_version_runs=297,
  unsupported_v03_security_records=27,note='Integrity/link/semantic review checks only; unsafe outcomes remain explicit.')
 (OUT/'review_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
