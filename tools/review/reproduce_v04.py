#!/usr/bin/env python3
"""Replay frozen v0.4 source via AEGIS_SOURCE_ROOT / AEGIS_ECU_LIB; no ECU source patching.
Run from the current repository; output only results/v1.0.0/baseline and failure_analysis.
The reviewer must build the archived baseline separately before using this reproduction tool.
"""
import sys,json,inspect,csv,os
from pathlib import Path
from dataclasses import asdict
sys.path.insert(0,str(Path(os.environ.get('AEGIS_SOURCE_ROOT','.'))/'sim'))
from aegis_sim.scenario import Scenario,LeadEvent
from aegis_sim.runner import run_scenario
from aegis_sim.security import HEADER
OUT=Path('results/v1.0.0');original=json.load(open('results/v0.4.0/experiment_runs.json'))
source,base=inspect.getsourcelines(run_scenario)
capture_line=next(base+i for i,x in enumerate(source) if 'res.min_gap_m = min(res.min_gap_m, gap)' in x)
allruns=[];mismatches=[];failures=[]
for i,old in enumerate(original):
 cfg=dict(old['config']);cfg['lead_events']=[LeadEvent(**x) for x in cfg['lead_events']];sc=Scenario(**cfg)
 failing=old['split']=='new_security_holdout' and old['security_config']['mode'] in ('B','C') and old['collision']
 timeline=[]
 def tracer(frame,event,arg):
  if frame.f_code is not run_scenario.__code__:return None
  if event=='line' and frame.f_lineno==capture_line:
   v=frame.f_locals;t=v['t_ms'];ctx=v['security_context'];row=dict(v['rows'][-1])
   row.update(sensor_measurements={name:None if v[name] is None else vars(v[name]) for name in ['rm','cm']},
      sensor_timestamp_ms=int(v['ai'].meas_ts_ms),outgoing_request=bytes(v['ao'].brake_req_frame).hex(),
      request_active=bool(v['ao'].brake_request_active),request_delivered=v['rf'] is not None,
      received_request=None if v['rf'] is None else dict(payload=v['rf'].data.hex(),sent_ms=v['rf'].timestamp_ms),
      backup_request_present=bool(v['bi'].backup_present),brake_frame_accepted=bool(v['bo'].frame_accepted),
      brake_aeb_target=float(v['bo'].aeb_target_decel_mps2),
      security_decisions=[dict(receiver=who,channel=channel,**e) for (who,channel),rx in ctx.verifiers.items() for e in rx.events if e['now_ms']==t],
      wire_requests=[dict(sent_ms=f.timestamp_ms,actual_delay_ms=t-f.timestamp_ms,wire_hex=f.data.hex()) for f in v['bus'].bus._deliverable if f.arbitration_id==0x120])
   timeline.append(row)
  return tracer
 if failing:sys.settrace(tracer)
 try:new=run_scenario(sc,old['seed'],security=old['security_config']).to_dict()
 finally:sys.settrace(None)
 # Security CPU timings are host measurements; all other original outputs must match.
 def stable(x):
  if isinstance(x,dict):return {k:stable(v) for k,v in x.items() if not k.startswith(('adas_cpu','adas_step')) and k not in ('verification_cpu_mean_us','verification_cpu_max_us','tx_cpu_mean_us')}
  if isinstance(x,list):return [stable(v) for v in x]
  return x
 for key,value in new.items():
  if stable({key:value})!=stable({key:old[key]}):mismatches.append(dict(index=i,field=key))
 allruns.append(new)
 if failing:
  ident=sc.id+'_'+old['security_config']['mode'];events=[e for row in timeline for e in row['security_decisions']]
  reasons={reason:sum(e['reason']==reason for e in events) for reason in set(e['reason'] for e in events)}
  labels=[]
  if reasons.get('AUTH'):labels.append('legitimate_or_modified_message_authentication_rejected')
  if reasons.get('GAP'):labels.append('freshness_counter_desynchronization')
  if reasons.get('STALE'):labels.append('authenticated_delivery_deadline_exceeded')
  if reasons.get('REPLAY') or reasons.get('EPOCH'):labels.append('restart_or_replay_freshness_rejected')
  if new['brake_timeout_seen']:labels.append('native_command_timeout')
  if old['security_config'].get('attack')=='A11':labels.append('authenticated_perception_insufficiency')
  if new['disagreement_cycles']:labels.append('sensor_disagreement')
  a=next(r for r in original if r['scenario_id']==sc.id and r['security_config']['mode']=='A')
  result=dict(id=ident,initial_config=old['config'],security_config=old['security_config'],seed=old['seed'],
    outcome=new,comparison_A_collision=a['collision'],classifications=labels,decision_counts=reasons,
    processing_delay='Zero logical crypto processing delay in model; CPU duration is not a causal simulated delay',
    timeline=timeline,collision_event=dict(time_s=new['collision_time_s'],impact_mps=new['impact_speed_mps']))
  (OUT/'failure_analysis'/f'{ident}.json').write_text(json.dumps(result,indent=2))
  first_reject=next((row['t_s'] for row in timeline if any(e['reason'] not in ('ACCEPT','RESYNC') for e in row['security_decisions'])),None)
  report=['# '+ident,'',f"Attack/fault: {old['security_config']}; seed {old['seed']}.",f"Initial speed {sc.ego_speed_kph:.3f} km/h; gap {sc.gap0_m:.3f} m; friction {sc.mu:.3f}.",f"Same-input A collision: {a['collision']}. Current collision {new['collision_time_s']:.6f} s, impact {new['impact_speed_mps']:.4f} m/s.",f"First request {new['first_brake_request_s']}; achieved brake {new['first_achieved_brake_s']}; first rejection {first_reject}; timeout {new['first_brake_timeout_s']}.",f"Observed contributing classifications: {labels}. Decisions: {reasons}.",'No security processing delay is modeled; do not attribute this collision to CPU overhead.', 'Full per-step sensor, request, wire delay, verifier and native brake/plant timeline is in the adjacent JSON.', 'Related tests: SEC-ST-003/004/005/006 as applicable; passing mechanism tests do not assert safe vehicle outcomes.']
  (OUT/'failure_analysis'/f'{ident}.md').write_text('\n'.join(report)+'\n');failures.append({k:result[k] for k in ['id','classifications','decision_counts','comparison_A_collision']})
 if (i+1)%100==0:print(i+1,flush=True)
(OUT/'baseline/runs.json').write_text(json.dumps(allruns,indent=2));(OUT/'baseline/reproduction.json').write_text(json.dumps(dict(runs=len(allruns),mismatches=mismatches),indent=2));(OUT/'failure_analysis/index.json').write_text(json.dumps(dict(failures=len(failures),cases=failures),indent=2))
assert not mismatches,mismatches[:5]
assert len(failures)==18

import subprocess
subprocess.run([sys.executable,str(Path(__file__).with_name("failure_reports.py"))],check=True)
