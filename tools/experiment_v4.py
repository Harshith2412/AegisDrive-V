#!/usr/bin/env python3
"""Matched communication policies; original hold-outs locked, new security set fixed first."""
import json,hashlib,sys
from pathlib import Path
from dataclasses import replace,asdict
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.scenario import Scenario,LeadEvent,load_all,load_scenario
from aegis_sim.runner import run_scenario
OUT=ROOT/'results/v0.4.0'
def reconstruct(cfg):
    cfg=dict(cfg);cfg['lead_events']=[LeadEvent(**x) for x in cfg['lead_events']];return Scenario(**cfg)
def design():
    cases=[];base=load_scenario(ROOT/'scenarios/S03_stationary_target.yaml')
    for attack in ['A%02d'%i for i in range(1,13)]:
        for seed in range(5):
            sc=replace(base,id=attack,perception='combined',imu_monitor=True)
            if attack in ('A01','A03','A04','A12'):sc=replace(sc,target_present=False,gap0_m=500)
            if attack=='A11':sc=replace(sc,perception='radar')
            cfg=dict(attack=attack,start_s=4 if attack=='A10' else 2)
            for mode in ('A','B','C'):cases.append(('attack_matrix',seed,sc,dict(cfg,mode=mode)))
    interactions={
      'C01_forged_rejected':dict(attack='A03'),
      'C02_legitimate_bad_auth':dict(attack='CORRUPT_LEGIT',wrong_tag=True),
      'C03_desync':dict(attack='A06'),
      'C04_flood':dict(attack='A07',paths=['primary','backup']),
      'C05_gateway_down':dict(gateway_down=True,paths=['primary','backup']),
      'C06_primary_bad_backup_healthy':dict(attack='CORRUPT_LEGIT',wrong_tag=True),
      'C07_shared_compromise':dict(attack='SHARED_COMPROMISE',shared_key_compromise=True,paths=['primary','backup']),
      'C08_trusted_ecu':dict(attack='A12',paths=['primary','backup'])}
    for name,cfg in interactions.items():
        for seed in range(3):
            empty=name in ('C01_forged_rejected','C07_shared_compromise','C08_trusted_ecu')
            sc=replace(base,id=name,perception='combined',imu_monitor=True,backup_enabled=True,
                       target_present=not empty,gap0_m=500 if empty else base.gap0_m)
            if name in ('C02_legitimate_bad_auth','C03_desync'):sc=replace(sc,backup_enabled=False)
            for mode in ('A','B','C'):cases.append(('coengineering',seed,sc,dict(cfg,mode=mode,start_s=2)))
    for sc in load_all(ROOT/'scenarios'):
        sc=replace(sc,perception='combined',backup_enabled=True,imu_monitor=True)
        for seed in range(5):
            for mode in ('A','B','C'):cases.append(('attack_free',seed,sc,dict(mode=mode)))
    locked=json.loads((ROOT/'results/v0.3.0/case_manifest.json').read_text())
    for case in locked:
        if case['split']=='holdout':
            sc=reconstruct(case['scenario'])
            for mode in ('A','B','C'):cases.append(('locked_v3_holdout',case['seed'],sc,dict(mode=mode)))
    rng=np.random.default_rng(400903)
    for i in range(48):
        attack='A%02d'%int(rng.integers(1,13));empty=attack in ('A01','A03','A04','A12')
        sc=replace(base,id=f'security_holdout_{i:03}',perception='combined',imu_monitor=True,
            backup_enabled=bool(rng.integers(0,2)),ego_speed_kph=float(rng.uniform(20,80)),
            gap0_m=500 if empty else float(rng.uniform(20,100)),target_present=not empty,
            mu=float(rng.uniform(.3,.9)),network_delay_ms=int(rng.choice([0,20,60])))
        if i%4==0:sc=replace(sc,faults=[{'type':'drop_feedback','t_s':3}])
        cfg=dict(attack=attack,start_s=round(float(rng.uniform(1,4)),2),
                 paths=['primary','backup'] if i%3==0 else ['primary'],delay_ms=int(rng.choice([60,120,200])))
        seed=int(rng.integers(0,2**31))
        for mode in ('A','B','C'):cases.append(('new_security_holdout',seed,sc,dict(cfg,mode=mode)))
    return cases

def main():
    cases=design();manifest=[dict(split=g,seed=s,scenario=asdict(sc),security=cfg) for g,s,sc,cfg in cases]
    encoded=json.dumps(manifest,indent=2);p=OUT/'case_manifest.json'
    if p.exists():assert p.read_text()==encoded,'locked security manifest changed'
    else:p.write_text(encoded)
    (OUT/'case_manifest.sha256').write_text(hashlib.sha256(encoded.encode()).hexdigest()+'\n')
    runs=[]
    for i,(split,seed,sc,cfg) in enumerate(cases):
        trace=OUT/'traces'/f'{sc.id}_{cfg["mode"]}.csv' if seed==0 else None
        r=run_scenario(sc,seed,trace_path=trace,security=cfg).to_dict()
        r.update(split=split,config=asdict(sc),security_config=cfg)
        runs.append(r)
        if (i+1)%30==0:print(i+1,'/',len(cases),split,sc.id,flush=True)
    (OUT/'experiment_runs.json').write_text(json.dumps(runs,indent=2));print('complete',len(runs),flush=True)
if __name__=='__main__':main()
