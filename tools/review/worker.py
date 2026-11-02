#!/usr/bin/env python3
"""Actual archived-version modules/library, with explicit unsupported security cases in v0.3."""
import os,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/v1.0.0'
profile=sys.argv[1];assert profile in ('v0.3.0','v0.4.0','candidate')
source=ROOT if profile=='candidate' else ROOT/'build/frozen'/profile
sys.path.insert(0,str(source/'sim'))
if profile!='candidate':os.environ['AEGIS_ECU_LIB']=str(source/'build/libaegis_ecu.dylib')
from aegis_sim.scenario import Scenario,LeadEvent
from aegis_sim.runner import run_scenario
cases=json.loads((OUT/'final_case_manifest.json').read_text())['cases'];runs=[]
for i,c in enumerate(cases):
    if profile=='v0.3.0' and c['security'].get('attack'):
        runs.append(dict(category=c['category'],id=c['scenario']['id'],supported=False,reason='Actual v0.3 has no attack/security-gateway API; no fabricated proxy result',config=c));continue
    cfg=dict(c['scenario']);cfg['lead_events']=[LeadEvent(**x) for x in cfg['lead_events']];sc=Scenario(**cfg)
    kwargs={}
    if profile!='v0.3.0':kwargs['security']=c['security']
    if profile=='candidate':kwargs['assurance']={'prefer_latest_authenticated':True}
    r=run_scenario(sc,c['seed'],**kwargs).to_dict()
    r.update(category=c['category'],supported=True,config=c);runs.append(r)
    if (i+1)%18==0:print(profile,i+1,flush=True)
(OUT/f'final_{profile}.json').write_text(json.dumps(runs,indent=2))
