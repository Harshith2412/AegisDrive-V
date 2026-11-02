#!/usr/bin/env python3
"""Frozen design and hold-out case manifest, followed by unfiltered experiment runs."""
import json,sys,hashlib
from pathlib import Path
from dataclasses import asdict,replace
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.scenario import load_all,load_scenario
from aegis_sim.runner import run_scenario
OUT=ROOT/'results/v0.3.0'

def design():
    cases=[]
    for sc in load_all(ROOT/'scenarios'):
        for mode,backup in [('radar',False),('camera',False),('combined',False),('combined',True)]:
            for seed in range(20):cases.append(('original',seed,replace(sc,id=sc.id+'_'+mode+('_backup' if backup else ''),perception=mode,backup_enabled=backup,imu_monitor=True)))
    base=load_scenario(ROOT/'scenarios/S03_stationary_target.yaml')
    variants={
      'camera_unavailable':dict(faults=[{'type':'camera_unavailable','t_s':2}]),
      'both_unavailable':dict(faults=[{'type':'both_unavailable','t_s':2}]),
      'both_frozen':dict(faults=[{'type':'radar_freeze','t_s':2},{'type':'camera_freeze','t_s':2}]),
      'radar_ambiguity':dict(radar_bias_m=30),
      'common_bias':dict(faults=[{'type':'correlated_bias','t_s':2}]),
      'fog':dict(camera={'visibility':.3}),
      'occlusion':dict(camera={'occlusion':.7}),
      'camera_false_negative':dict(camera={'detection_probability':0}),
      'feedback_lost':dict(faults=[{'type':'drop_feedback','t_s':2}]),
      'ecu_failed':dict(faults=[{'type':'brake_software_failure','t_s':3}]),
      'actuator_failed':dict(faults=[{'type':'actuator_failure','t_s':3}]),
      'both_channels_lost':dict(faults=[{'type':'both_channels_lost','t_s':4.2}]),
      'intermittent':dict(faults=[{'type':'intermittent_req','t_s':2}]),
      'delayed':dict(network_delay_ms=180),
      'duplicate':dict(network_duplicate=True),
      'no_target':dict(target_present=False,gap0_m=500),
      'radar_ghost':dict(target_present=False,gap0_m=500,radar_false_positive=True),
      'common_ghost':dict(target_present=False,gap0_m=500,radar_false_positive=True,camera={'false_positive':True})}
    for name,kw in variants.items():
        for seed in range(10):cases.append(('fault_sotif',seed,replace(base,id=name,perception='combined',backup_enabled=True,imu_monitor=True,**kw)))
    # Disjoint PRNGs fixed before results: no tuning against hold-out outcomes.
    for split,count,master in [('development',48,3301),('holdout',120,77903)]:
        rng=np.random.default_rng(master)
        for i in range(count):
            speed=float(rng.uniform(12,85)); gap=float(rng.uniform(8,110));mu=float(rng.uniform(.2,1.))
            cam=dict(latency_ms=int(rng.choice([40,80,120])),visibility=float(rng.uniform(.25,1)),
                     occlusion=float(rng.uniform(0,.6)),detection_probability=float(rng.uniform(.65,1)))
            sc=replace(base,id=f'{split}_{i:03}',ego_speed_kph=speed,gap0_m=gap,mu=mu,
                       perception='combined',backup_enabled=True,imu_monitor=True,camera=cam,
                       radar={'latency_ms':int(rng.choice([0,30,60])), 'range_sigma_m':float(rng.uniform(.1,.8))},
                       network_delay_ms=int(rng.choice([0,20,60])),duration_s=20)
            cases.append((split,int(rng.integers(0,2**31)),sc))
    return cases

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    cases=design()
    manifest=[dict(split=split,seed=seed,scenario=asdict(sc)) for split,seed,sc in cases]
    path=OUT/'case_manifest.json'
    encoded=json.dumps(manifest,indent=2)
    if path.exists():assert path.read_text()==encoded,'case manifest changed'
    else:path.write_text(encoded)
    (OUT/'case_manifest.sha256').write_text(hashlib.sha256(encoded.encode()).hexdigest()+'\n')
    records=[]
    for i,(split,seed,sc) in enumerate(cases):
        trace=OUT/'traces'/f'{sc.id}.csv' if seed==0 else None
        r=run_scenario(sc,seed,trace_path=trace)
        d=r.to_dict();d.update(split=split,config=asdict(sc))
        d['retrigger_count']=max(0,r.states_visited.count('BRAKING')-1)
        records.append(d)
        if (i+1)%20==0:print(i+1,'/',len(cases),sc.id,flush=True)
    (OUT/'experiment_runs.json').write_text(json.dumps(records,indent=2))
    print('complete',len(records),flush=True)
if __name__=='__main__':main()
