#!/usr/bin/env python3
"""Validate trace artifacts and cross-check legal state edges; not a SysML parser."""
import json
import re
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/v0.2.0'

def main():
    db=yaml.safe_load((ROOT/'requirements/requirements.yaml').read_text())['requirements']
    matrix=json.loads((OUT/'traceability_matrix.json').read_text())
    byid={r['id']:r for r in matrix['matrix']}
    source=(ROOT/'ecu/src/adas_ecu.cpp').read_text()
    table=source.split('constexpr bool kAllowed',1)[1].split('};',1)[0]
    rows=re.findall(r'/\*\s*(\w+)\s*\*/\s*\{([^}]+)\}',table)
    names=[n for n,_ in rows]
    expected={(names[i],names[j]) for i,(_,row) in enumerate(rows)
              for j,b in enumerate(re.findall(r'\b(true|false)\b',row)) if b=='true'}
    actual=set(re.findall(r'^(\w+) --> (\w+) :', (ROOT/'models/adas_states.puml').read_text(),re.M))
    assert len(expected)==26 and actual==expected, 'state model differs from compiled table'
    safety=(ROOT/"docs/v0.2.0_safety.md").read_text()
    chains=[]
    for r in db:
        rid=r['id']
        if rid in ('FSR-203','TSR-203','TSR-003','BRK-REQ-002'):
            hazards,goals=['HE-04'],['SG-04']
        elif rid in ('FSR-202','TSR-202','ADAS-REQ-006'):
            hazards,goals=['HE-05'],['SG-05']
        elif rid.startswith('BCM-'):
            hazards,goals=['HE-06'],['SG-06']
        elif rid in ('FSR-001','TSR-001','ADAS-REQ-009','ADAS-REQ-010','ADAS-REQ-011'):
            hazards,goals=['HE-03'],['SG-03','SG-02']
        elif rid in ('TSR-002','BRK-REQ-001','SYS-REQ-002'):
            hazards,goals=['HE-02'],['SG-02']
        else:
            hazards,goals=['HE-01','HE-07'],['SG-01']
        assert all(x in safety for x in hazards+goals),rid
        models=['models/context.puml','models/interfaces.puml','models/sequence.puml']
        if 'ADAS ECU' in r['allocated_to']:models+=['models/adas_states.puml']
        for f in models+r['implementation']:
            assert (ROOT/f.split('#')[0]).exists(),f
        assert byid[rid]['verification_status']=='VERIFIED',rid
        chains.append(dict(hazardous_events=hazards,safety_goals=goals,requirement=rid,
                           allocated_to=r['allocated_to'],models=models,implementation=r['implementation'],
                           tests=byid[rid]['tests'],evidence='results/v0.2.0/traceability_matrix.json',
                           role='supporting assurance' if rid.startswith(('SIM-','SWR-')) else 'functional allocation'))
    result=dict(state_edges_checked=len(actual),requirements_linked=len(chains),chains=chains,
                sysml_validation='NOT VALIDATED: no SysML v2 parser installed',
                note='Link integrity and executed test status only; no proof of hazard mitigation or UML semantics.')
    (OUT/'safety_trace.json').write_text(json.dumps(result,indent=2))
    lines=['# Hazard to evidence links','', '| Event | Goal | Requirement | Component | Models | Tests |', '|---|---|---|---|---|---|']
    for c in chains:
        lines.append('| '+' | '.join([', '.join(c['hazardous_events']),', '.join(c['safety_goals']),c['requirement'],', '.join(c['allocated_to']),', '.join(c['models']),', '.join(t['id']+' '+t['result'] for t in c['tests'])])+' |')
    (OUT/'safety_trace.md').write_text('\n'.join(lines)+'\n')
    print(f'{len(chains)} linked requirements; {len(actual)} model/code state edges match. SysML unvalidated.')
if __name__=='__main__':main()
