#!/usr/bin/env python3
"""v0.3 evidence/model link checks, separate from historic release tooling."""
import hashlib,json,re,tarfile
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/v0.3.0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    db=yaml.safe_load((ROOT/'requirements/requirements.yaml').read_text())['requirements']
    matrix=json.loads((OUT/'traceability_matrix.json').read_text());assert not matrix['errors']
    assert matrix['requirements']==44 and matrix['status_counts']['VERIFIED']==44
    sysml=(ROOT/'models/v0.3.0/requirements.sysml').read_text()
    for r in db:
        assert "requirement '"+r['id']+"'" in sysml
        assert "verify '"+r['id']+"'" in sysml
        assert "allocate '"+r['id']+"'" in sysml
    log=(OUT/'sysml-validation.log').read_text()
    for model in ['models/v0.3.0/aegis.sysml','models/v0.3.0/requirements.sysml']:
        assert sha(ROOT/model)+'  '+model in log,'Semantic validation hash mismatch'
    assert 'SEMANTIC_ERRORS=0 WARNINGS=0' in log and 'negative control correctly rejected' in log
    assert "Couldn't resolve" in (OUT/'sysml-negative.log').read_text()
    uml_log=(OUT/'uml-validation.log').read_text()
    assert 'UML_VALIDATION_PASS' in uml_log
    assert sha(ROOT/'models/v0.3.0/fault_containment.puml')+'  models/v0.3.0/fault_containment.puml' in uml_log
    archive=ROOT/'baseline/v0.2.0/source-and-evidence.tar.gz'
    assert sha(archive)==(ROOT/'baseline/v0.2.0/SHA256SUMS').read_text().split()[0]
    count=0
    with tarfile.open(archive) as tf:
        for m in tf.getmembers():
            if m.isfile() and not Path(m.name).name.startswith('._') and (m.name.startswith('results/v0.2.0/') or m.name.startswith('scenarios/')):
                assert tf.extractfile(m).read()==(ROOT/m.name).read_bytes(),m.name
                count+=1
    rows=re.findall(r'/\*\s*(\w+)\s*\*/\s*\{([^}]+)\}',(ROOT/'ecu/src/adas_ecu.cpp').read_text().split('constexpr bool kAllowed')[1].split('};')[0])
    names=[x[0] for x in rows]
    edges={(names[i],names[j]) for i,(_,row) in enumerate(rows) for j,v in enumerate(re.findall(r'\b(true|false)\b',row)) if v=='true'}
    modeled=set(re.findall(r'^(\w+) --> (\w+) :',(ROOT/'models/adas_states.puml').read_text(),re.M))
    assert edges==modeled and len(edges)==26
    chains=[]
    previous={r['requirement']:r for r in json.loads((ROOT/'results/v0.2.0/safety_trace.json').read_text())['chains']}
    for r in matrix['matrix']:
        c=previous.get(r['id'],dict(hazardous_events=['HE-01','HE-02','HE-03','HE-04'],safety_goals=['SG-01','SG-02','SG-03','SG-04']))
        c=dict(c);c.update(requirement=r['id'],allocated_to=r['allocated_to'],tests=r['tests'],
            implementation=r['implementation'],models=['models/v0.3.0/aegis.sysml','models/v0.3.0/requirements.sysml'],
            evidence='results/v0.3.0/traceability_matrix.json',verification_scope='Linked executed tests; not full safety-goal satisfaction')
        chains.append(c)
    (OUT/'safety_trace.json').write_text(json.dumps(dict(requirements=44,chains=chains),indent=2))
    models=[ROOT/'models/v0.3.0/aegis.sysml',ROOT/'models/v0.3.0/requirements.sysml',ROOT/'models/v0.3.0/fault_containment.puml']
    (OUT/'models.json').write_text(json.dumps(dict(sysml_tool='Official SysML v2 pilot 0.63.1, release 2026-09.1',
        semantic_errors=0,semantic_warnings=0,negative_control='Unresolved type rejected',
        files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in models],
        note='Parser/semantic validity and link integrity do not establish engineering correctness, behavior equivalence or executed SysML verification verdicts.'),indent=2))
    print('44 requirement/model/test chains checked; 26 state edges match; SysML semantics checked; historical evidence unchanged:',count,'files')
if __name__=='__main__':main()
