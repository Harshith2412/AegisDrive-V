#!/usr/bin/env python3
"""Explicit trace provenance and objective limitations; no inferred certification hierarchy."""
import json,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/v1.0.0'
def main():
 db=yaml.safe_load((ROOT/'requirements/requirements.yaml').read_text());trace=json.loads((OUT/'traceability_matrix.json').read_text());byid={x['id']:x for x in trace['matrix']}
 old=json.loads((ROOT/'results/v0.3.0/safety_trace.json').read_text());alloc={r['requirement']:r for r in old['chains']}
 warnings=[dict(id='L01',finding='Legacy YAML parents reference charter/provisional hazards, not a complete explicit HARA->SG->FSR derivation graph.',status='OPEN: documentary allocations are reviewed supporting links, not retroactive normative derivation'),
 dict(id='L02',finding='SysML behavior is abstract and some units are encoded in names; no full controller/model behavioral equivalence or executed verification cases.',status='OPEN'),
 dict(id='L03',finding='Text symbol/link existence and PASS tags do not independently prove acceptance scope or every natural-language obligation.',status='OPEN: objective flags below'),
 dict(id='L04',finding='HARA S/E/C/ASIL proposals lack external exposure/controllability validation.',status='OPEN: no substantiated ASIL or compliance finding'),
 dict(id='L05',finding='No target ECU timing, physical hardware, following-vehicle model or real image-domain validation.',status='OPEN')]
 objective={
 'SYS-REQ-001':('SCOPE_AMBIGUOUS','Gap/response-distance conditions must constrain broad avoidance wording; final short-gap/ODD/low-grip counterexamples remain, while specified nominal acceptance tests pass.'),
 'SYS-REQ-002':('INTENDED_OBJECTIVE_OPEN','Persistent ghosts and trusted malicious commands cause unnecessary braking despite nominal following tests passing.'),
 'SYS-REQ-003':('TESTED_SCENARIOS_ONLY','S02/S04 acceptance samples pass, not a general lead-braking guarantee.'),
 'FSR-201':('ASSUMPTION_LIMITED','Stopping-distance planning assumes achievable deceleration; no measured friction estimator.'),
 'TSR-201':('ASSUMPTION_LIMITED','Low adhesion/short-distance collisions remain; passing selected wet cases is not all-weather avoidance.'),
 'FSR-203':('DETECTION_NOT_AVAILABILITY','Status/achieved diagnostics can pass while both-path/shared-actuator loss still collides.'),
 'TSR-203':('DETECTION_NOT_AVAILABILITY','Diagnostic budgets are not demonstrated vehicle FTTIs or rescue guarantees.'),
 'BRK-301':('COMMON_DEPENDENCY_OPEN','Backup command transport shares ECU/actuator/security dependencies.'),
 'PER-302':('FALSE_POSITIVE_OBJECTIVE_OPEN','Union policy retains isolated/persistent common ghosts; corroboration/temporal alternatives introduce true-obstacle collisions.'),
 'SEC-401':('AUTHENTICITY_SCOPE_ONLY','Valid-key compromise and plausible malicious intent are not prevented.'),
 'SEC-402':('AVAILABILITY_TRADEOFF','Strict freshness and stale replacement can suppress legitimate braking; total retained-state loss is replay-vulnerable.'),
 'SEC-403':('SEMANTIC_TRUST_OPEN','Authenticated implausible data is rejected, but plausible false data/dangerous authorized commands can pass.'),
 'REC-501':('ALGORITHM_TESTED_BENEFIT_LIMITED','Newer verified backup selected; no aggregate collision reduction demonstrated in final set.'),
 'SOT-501':('EVALUATION_COMPLETE_OBJECTIVE_OPEN','Tradeoff study is evidence of limitations, not a false-braking solution.')}
 links=[]
 for r in db['requirements']:
  reviewed={'REC-501':dict(hazardous_events=['HE-04'],safety_goals=['SG-04']), 'REC-502':dict(hazardous_events=['HE-04'],safety_goals=['SG-04']), 'SOT-501':dict(hazardous_events=['HE-01','HE-02'],safety_goals=['SG-01','SG-02'])}
  oldlink=alloc.get(r['id'],reviewed.get(r['id'],{}));support=r['id'].startswith(('SIM-','SWR-','QLT-'))
  links.append(dict(requirement=r['id'],actual_yaml_parents=r['parent'],item='docs/01_item_definition.md',
   hara='docs/v0.2.0_safety.md#scenario-hara' if not support else None,
   hazardous_events=oldlink.get('hazardous_events',[]),safety_goals=oldlink.get('safety_goals',[]),
   concept_sources=['docs/v0.2.0_safety.md','docs/v0.3.0_fault_containment.md','docs/v1.0.0_recovery_decision.md'],
   software_allocation=r['allocated_to'],architecture=['models/v0.3.0/aegis.sysml','models/v0.4.0/security.sysml','models/v1.0.0/review.sysml'],
   implementation=r['implementation'],tests=byid[r['id']]['tests'],linked_test_status=byid[r['id']]['verification_status'],
   objective_status=objective.get(r['id'],('SCOPED_EVIDENCE_ONLY','No general safety-goal closure is inferred from linked tests.'))[0],
   objective_note=objective.get(r['id'],('','No general safety-goal closure is inferred from linked tests.'))[1],
   provenance='Legacy reviewed allocation from prior safety_trace' if oldlink else 'Supporting review/security allocation; missing hazard/goal derivation explicitly retained',
   supporting_assurance=support))
 sotif=[dict(limitation=x,trigger=trigger,mitigation=mitigation,evidence='results/v1.0.0/perception_study.json',status='OPEN') for x,trigger,mitigation in [
 ('isolated ghost','single-source false target','compare union/corroboration/temporal/confidence'),
 ('common ghost','consistent positive false target from both sensors','none demonstrated'),
 ('occlusion/fog/low confidence','camera fails to corroborate real obstacle','single-source recall vs confirmation tradeoff'),
 ('insufficient physical distance','short gap/low adhesion','no physically unjustified rescue claim')]]
 data=dict(requirements=len(links),links=links,sotif=sotif,lifecycle_gaps=warnings,security_chain_source='results/v0.4.0/security_trace.json',
  current_security_tests='results/v1.0.0/traceability_matrix.json',note='Review allocations and gaps are explicit; no complete normative derivation or objective closure claimed.')
 (OUT/'lifecycle_trace.json').write_text(json.dumps(data,indent=2))
 lines=['# Lifecycle traceability audit','',f"{len(links)} requirements with computed linked-test status; vehicle objectives separately classified.",'','## Explicit lifecycle gaps','']
 for w in warnings:lines.append(f"- {w['id']}: {w['finding']} {w['status']}")
 lines+=['','| Requirement | Linked tests | Objective review | Scope / counterexample |','|---|---|---|---|']
 for r in links:lines.append(f"| {r['requirement']} | {r['linked_test_status']} | {r['objective_status']} | {r['objective_note']} |")
 (OUT/'lifecycle_trace.md').write_text('\n'.join(lines)+'\n');print('audited',len(links),'requirements; retained',len(warnings),'lifecycle gaps')
if __name__=='__main__':main()
