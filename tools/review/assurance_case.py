#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/v1.0.0'
claims=[
 ('C1','Nominal configured decision thresholds are exercised; universal timely avoidance is not claimed.','LIMITED',['ecu/tests/test_adas.cpp','results/v1.0.0/final_candidate.json'],['29/120 prior hold-outs collide','47/108 stratified final candidate cases collide']),
 ('C2','Configured MAC/authorization/freshness rejection is supported under public-fixture-key assumptions.','SCOPED_SUPPORTED',['tests/python/test_v4_security.py','results/v1.0.0/locked_candidate.json'],['Trusted-key compromise passes dangerous intent','Retained-state total loss permits replay']),
 ('C3','Specified detectable sensor/communication/achieved-braking faults are indicated in tested budgets.','SCOPED_SUPPORTED',['tests/python/test_v3_faults.py','results/v1.0.0/failure_analysis/review.md'],['Detection cannot restore missing bandwidth/physical braking']),
 ('C4','Newest-authenticated route selection and bounded diagnostic recovery follow tested contracts.','SCOPED_SUPPORTED',['tests/python/test_v1_assurance.py','docs/v1.0.0_recovery_decision.md'],['No aggregate collision reduction in final set','All usable paths stale/lost remain open']),
 ('C5','Specified detectable invalid-input modes have defined native degradation behavior.','LIMITED',['ecu/src/adas_ecu.cpp','results/v1.0.0/python_test_results.xml'],['Plausible errors and compromised intent can escape validity checks','Degraded/unavailable can still collide']),
 ('C6','Perception/braking limitations are compared with preserved negative results.','EVALUATION_SUPPORTED',['results/v1.0.0/perception_study.json','results/v1.0.0/evaluation.md'],['Temporal/corroboration can cause genuine-obstacle collisions','Common ghosts remain']),
 ('C7','Evidence integrity, requirement/test linkage and known lifecycle/model gaps are reviewable.','SCOPED_SUPPORTED',['results/v1.0.0/lifecycle_trace.json','results/v1.0.0/sysml-validation.log'],['PASS is not objective closure','Language validity is not engineering equivalence'])]
case=dict(top_claim=dict(id='C0',text='This educational case study transparently characterizes its specified simulated mechanisms, evidence and unresolved hazards.',
 status='REVIEWABLE_RESEARCH_ARTIFACT_NOT_SAFE_VEHICLE_CLAIM'),
 argument='Combine reproducibility, mechanism verification, adverse evaluation and explicit defeaters; do not infer acceptable real-world risk.',
 context=['Single-target longitudinal point-mass SiL','No real vehicles/hardware or physical independent actuation','Same automation in reviewer roles, no accredited independent assessment'],
 assumptions=['Trusted local FFI and shared simulation clock','Public test keys only','Declared artificial scenario distributions','No follower or injury model'],
 claims=[dict(id=i,claim=t,status=s,evidence=e,counterexamples=d) for i,t,s,e,d in claims],
 open_limitations=['Physical/SOTIF/availability hazards unresolved','Partial structural coverage and ASan unvalidated','No ISO/AUTOSAR conformance, homologation or production-readiness claim'])
(OUT/'assurance_case.json').write_text(json.dumps(case,indent=2))
lines=['# Structured engineering assurance case','',case['top_claim']['text'],'', '**This is not a claim that the vehicle function is safe.** GSN-like notation: C=claim, S=strategy, E=evidence, A=assumption, D=defeater/counterexample. Links are documented arguments, not a formal proof.','',case['argument'],'']
for c in case['claims']:
 lines += [f"## {c['id']} — {c['status']}", '',c['claim'],'','Evidence: '+', '.join(c['evidence']),'','Defeaters: '+ '; '.join(c['counterexamples']),'']
lines += ['## Assumptions and residuals','']+['- '+s for s in case['assumptions']+case['open_limitations']]
(ROOT/'docs/v1.0.0_assurance_case.md').write_text('\n'.join(lines)+'\n')
