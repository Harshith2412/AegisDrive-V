#!/usr/bin/env python3
import sys,json
from pathlib import Path
from dataclasses import replace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.scenario import load_scenario
from aegis_sim.runner import run_scenario
OUT=ROOT/'results/v1.0.0';base=load_scenario(ROOT/'scenarios/S03_stationary_target.yaml')
cases={
'persistent_radar_ghost':replace(base,id='persistent_radar_ghost',target_present=False,gap0_m=500,perception='combined',radar_false_positive=True),
'persistent_common_ghost':replace(base,id='persistent_common_ghost',target_present=False,gap0_m=500,perception='combined',radar_false_positive=True,camera={'false_positive':True}),
'brief_ghost':replace(base,id='brief_ghost',target_present=False,gap0_m=500,perception='combined',faults=[{'type':'radar_ghost','t_s':2,'until_s':2.03}]),
'genuine_close_camera_failed':replace(base,id='genuine_close_camera_failed',gap0_m=20,perception='combined',faults=[{'type':'camera_unavailable','t_s':0}]),
'genuine_occluded':replace(base,id='genuine_occluded',gap0_m=40,perception='combined',camera={'occlusion':.8}),
'genuine_low_confidence':replace(base,id='genuine_low_confidence',gap0_m=40,perception='combined',camera={'confidence':.5}),
'genuine_nominal':replace(base,id='genuine_nominal',perception='combined'),
'genuine_fog':replace(base,id='genuine_fog',gap0_m=40,perception='combined',camera={'visibility':.2})}
profiles={'union':{},'corroborated':{'perception_study':'corroborated'},'temporal':{'perception_study':'temporal'},
          'low_confidence':{'perception_study':'conservative'},'bounded_3mps2':{'brake_cap_mps2':3}}
records=[]
for name,sc in cases.items():
 for profile,opts in profiles.items():
  for seed in range(5):
   r=run_scenario(sc,seed,assurance=opts).to_dict();r.update(case=name,profile=profile);records.append(r)
 print(name,flush=True)
(OUT/'perception_study.json').write_text(json.dumps(records,indent=2))
if '--study-only' in sys.argv:sys.exit(0)
# Re-evaluate locked prior sets with candidate, retaining B/C as separate comparator policies.
old=json.loads((ROOT/'results/v0.4.0/case_manifest.json').read_text());from aegis_sim.scenario import Scenario,LeadEvent
locked=[]
for c in old:
 if c['split'] not in ('locked_v3_holdout','new_security_holdout'):continue
 if c['split']=='locked_v3_holdout' and c['security']['mode']!='C':continue
 if c['split']=='new_security_holdout' and c['security']['mode']=='A':continue
 cfg=dict(c['scenario']);cfg['lead_events']=[LeadEvent(**x) for x in cfg['lead_events']]
 r=run_scenario(Scenario(**cfg),c['seed'],security=c['security'],assurance={'prefer_latest_authenticated':True}).to_dict()
 r.update(split=c['split'],security_config=c['security'],original_config=c['scenario']);locked.append(r)
(OUT/'locked_candidate.json').write_text(json.dumps(locked,indent=2));print('locked',len(locked),flush=True)
