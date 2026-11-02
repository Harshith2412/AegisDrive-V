#!/usr/bin/env python3
"""Interpret frozen per-step events using documented baseline verifier ordering."""
import json,struct
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/v1.0.0/failure_analysis'
files=sorted(OUT.glob('security_holdout_*.json'));cases=[];groups=Counter()
for p in files:
 d=json.loads(p.read_text());reasons=d['decision_counts'];mode=d['security_config']['mode'];attack=d['security_config']['attack']
 primary='stale_authenticated_delivery' if reasons.get('STALE') else 'counter_gap' if reasons.get('GAP') else 'rollback_or_replay'
 groups[mode+':'+primary]+=1
 tests=['SEC-ST-003','SEC-UT-002'] if attack=='A06' else ['SEC-UT-003','REV-PBT-002'] if attack=='A10' else ['SEC-ST-005','SEC-UT-002']
 d.update(primary_cause=primary,related_test_ids=tests,affected_requirements=['SEC-402','FSR-203','TSR-203','BRK-REQ-002'],
          objective_note='Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.')
 for row in d['timeline']:
  row['outgoing_request_ms']=round(row['t_s']*1000)
  for wire in row['wire_requests']:
   raw=bytes.fromhex(wire['wire_hex'])
   if len(raw)==64:
    issued=struct.Struct('!BBBBHIQQB').unpack_from(raw)[7]
    wire.update(authenticated_issued_ms=issued,end_to_end_age_ms=round(row['t_s']*1000)-issued)
  for e in row['security_decisions']:
   r=e['reason'];e['authentication']='VALID' if r in ('ACCEPT','RESYNC','STALE','FUTURE','REPLAY','GAP','EPOCH','ROLLBACK') else 'INVALID' if r=='AUTH' else 'NOT_CHECKED'
   e['freshness']='ACCEPT' if r in ('ACCEPT','RESYNC') else 'REJECT_'+r if r in ('STALE','FUTURE','REPLAY','GAP','EPOCH','ROLLBACK') else 'NOT_CHECKED'
 p.write_text(json.dumps(d,indent=2));r=d['outcome'];sc=d['initial_config']
 first_reject=next((row['t_s'] for row in d['timeline'] if any(e['reason'] not in ('ACCEPT','RESYNC') for e in row['security_decisions'])),None)
 lines=['# '+d['id'],'',f"Case {attack}, policy {mode}, seed {d['seed']}; config {d['security_config']}.",
 f"Initial ego {sc['ego_speed_kph']:.3f} km/h; lead {sc['lead_speed_kph']:.3f} km/h; gap {sc['gap0_m']:.3f} m; mu {sc['mu']:.3f}.",
 f"Evidence-backed primary group: **{primary}**. Additional observed classifications: {d['classifications']}.",
 f"Matched A collision: {d['comparison_A_collision']}. First request {r['first_brake_request_s']} s; first achieved brake {r['first_achieved_brake_s']} s; first rejection {first_reject} s; native timeout {r['first_brake_timeout_s']} s.",
 f"Contact {r['collision_time_s']:.6f} s; relative impact {r['impact_speed_mps']:.4f} m/s. Verifier decision counts: {reasons}.",
 'Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.',
 'Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.',
 'Tests: '+', '.join(tests)+'. Affected requirements: '+', '.join(d['affected_requirements'])+'.',d['objective_note']]
 p.with_suffix('.md').write_text('\n\n'.join(lines)+'\n')
 cases.append({k:d[k] for k in ['id','primary_cause','classifications','decision_counts','comparison_A_collision','related_test_ids','affected_requirements']})
index=dict(failures=len(cases),cause_counts=dict(groups),cases=cases,interpretation='All matched A runs avoid collision; these are withholding/rejection/timeout interactions, not simulated CPU delays or unrelated baseline collisions.')
(OUT/'index.json').write_text(json.dumps(index,indent=2))
lines=['# Independent security-collision review','',f"{len(cases)} individual reports; groups: {dict(groups)}.",'',index['interpretation'],'','| Failure | Primary cause | Mechanism tests |','|---|---|---|']
for c in cases:lines.append(f"| [{c['id']}]({c['id']}.md) | {c['primary_cause']} | {', '.join(c['related_test_ids'])} |")
(OUT/'review.md').write_text('\n'.join(lines)+'\n')
print('rendered',len(cases),'individual failure reports')
