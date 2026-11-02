#!/usr/bin/env python3
"""Join threat, safety/security requirement, mechanism, test and measured evidence."""
import hashlib,json,tarfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/v0.4.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    trace=json.loads((OUT/'traceability_matrix.json').read_text())
    assert trace['requirements']==49 and trace['status_counts']['VERIFIED']==49 and not trace['errors']
    req={r['id']:r for r in trace['matrix']};tara=json.loads((ROOT/'requirements/threats_v0.4.0.json').read_text())
    runs=json.loads((OUT/'experiment_runs.json').read_text());assert len(runs)==846
    experiments={r['scenario_id'] for r in runs};chains=[]
    for t in tara['threats']:
        assert t['asset'] in tara['assets'] and t['goal'] in tara['goals']
        r=req[t['requirement']];tests={x['id']:x['result'] for x in r['tests']}
        assert all(tid in tests and tests[tid]=='PASS' for tid in t['verification_tests']),t['id']
        assert t['experiment'] in experiments,t['id']
        for ref in t['implementation']:assert (ROOT/ref).exists()
        chains.append(dict(threat=t['id'],asset=t['asset'],goal=t['goal'],requirement=r['id'],
          mechanism=r['implementation'],tests=r['tests'],experiment=t['experiment'],evidence='results/v0.4.0/experiment_runs.json'))
    modelpaths=['models/v0.3.0/aegis.sysml','models/v0.3.0/requirements.sysml','models/v0.4.0/security.sysml']
    log=(OUT/'sysml-validation.log').read_text()
    assert 'SEMANTIC_ERRORS=0 WARNINGS=0' in log and 'negative control correctly rejected' in log
    for p in modelpaths:assert sha(ROOT/p)+'  '+p in log,p
    assert "Couldn't resolve" in (OUT/'sysml-negative.log').read_text()
    uml=(OUT/'uml-validation.log').read_text()
    assert 'UML_VALIDATION_PASS' in uml
    assert sha(ROOT/'models/v0.4.0/trust_boundaries.puml')+'  models/v0.4.0/trust_boundaries.puml' in uml
    protected=json.loads((OUT/'case_manifest.json').read_text())
    assert sha(OUT/'case_manifest.json')==(OUT/'case_manifest.sha256').read_text().strip()
    old=json.loads((ROOT/'results/v0.3.0/case_manifest.json').read_text())
    locked={x['scenario']['id']:x for x in old if x['split']=='holdout'}
    assert len(locked)==120
    for p,r in zip(protected,runs):
        assert p['scenario']==r['config'] and p['security']==r['security_config'] and p['seed']==r['seed']
        if p['split']=='locked_v3_holdout':
            original=locked[p['scenario']['id']]
            assert p['scenario']==original['scenario'] and p['seed']==original['seed']
    for version in ['v0.1.0','v0.2.0','v0.3.0']:
        archive=ROOT/'baseline'/version/'source-and-evidence.tar.gz'
        assert sha(archive)==(archive.parent/'SHA256SUMS').read_text().split()[0]
    old_archive=ROOT/'baseline/v0.3.0/source-and-evidence.tar.gz'
    assert sha(old_archive)==(ROOT/'baseline/v0.3.0/SHA256SUMS').read_text().split()[0]
    checked=0
    with tarfile.open(old_archive) as tf:
        for m in tf.getmembers():
            if m.isfile() and not Path(m.name).name.startswith('._') and m.name.startswith(('results/v0.3.0/','results/v0.2.0/','scenarios/')):
                assert tf.extractfile(m).read()==(ROOT/m.name).read_bytes(),m.name
                checked+=1
    baseline=json.loads((OUT/'baseline/comparison.json').read_text());assert baseline['runs']==828 and not baseline['mismatches']
    interactions={
      'C01_forged_rejected':(['SYS-REQ-002','BRK-REQ-001'],'HE-02'),
      'C02_legitimate_bad_auth':(['FSR-203','TSR-203','BRK-REQ-002'],'HE-04'),
      'C03_desync':(['FSR-203','BRK-301'],'HE-04'),
      'C04_flood':(['TSR-203','DIA-301'],'HE-04'),
      'C05_gateway_down':(['FSR-203','BRK-301'],'HE-04'),
      'C06_primary_bad_backup_healthy':(['BRK-301','TSR-203'],'HE-04'),
      'C07_shared_compromise':(['SYS-REQ-002','BRK-301'],'HE-02'),
      'C08_trusted_ecu':(['SYS-REQ-002','PER-302'],'HE-02')}
    safety=[]
    for case,(ids,hazard) in interactions.items():
        assert case in experiments and all(i in req for i in ids)
        safety.append(dict(security_control_failure_or_scenario=case,affected_safety_requirements=ids,hazardous_event=hazard,
                           experiment=case,evidence='results/v0.4.0/experiment_summary.json'))
    (OUT/'security_trace.json').write_text(json.dumps(dict(threat_chains=chains,safety_security_chains=safety,
      note='Link and executed evidence integrity, not prevention of all damage scenarios'),indent=2))
    (OUT/'models.json').write_text(json.dumps(dict(tool='Official SysML pilot 0.63.1',semantic_errors=0,semantic_warnings=0,
      negative_control_rejected=True,models=[dict(path=p,sha256=sha(ROOT/p)) for p in modelpaths],
      new_security_model='models/v0.4.0/security.sysml',uml='models/v0.4.0/trust_boundaries.svg',
      limitation='Language/link validation, not engineering completeness or executed SysML verification cases'),indent=2))
    print('49 linked requirements, 13 threat chains, 8 safety-security chains; historical files unchanged:',checked)
if __name__=='__main__':main()
