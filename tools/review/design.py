#!/usr/bin/env python3
"""Fixed stratified review cases; no tuning from final-case outcomes."""
import sys,json,hashlib
from pathlib import Path
from dataclasses import asdict,replace
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.scenario import load_scenario
OUT=ROOT/'results/v1.0.0'
def build():
    base=load_scenario(ROOT/'scenarios/S03_stationary_target.yaml');cases=[]
    categories=['normal','hard_braking','low_friction','sensor_failure','communication_failure',
      'security_attack','authentication_recovery','ghost','shared_ecu','actuator','combined','boundary']
    rng=np.random.default_rng(1100907)
    for category in categories:
      for i in range(9):
        sc=replace(base,id=f'review_{category}_{i:02}',perception='combined',backup_enabled=True,imu_monitor=True,
                   ego_speed_kph=float(rng.uniform(20,78)),gap0_m=float(rng.uniform(20,100)),mu=float(rng.uniform(.45,.95)),duration_s=18)
        sec={'mode':'C'}
        if category=='normal':sc=replace(sc,lead_speed_kph=sc.ego_speed_kph,gap0_m=40)
        elif category=='hard_braking':
          from aegis_sim.scenario import LeadEvent
          sc=replace(sc,lead_speed_kph=sc.ego_speed_kph,gap0_m=float(rng.uniform(12,40)),lead_events=[LeadEvent(2,-float(rng.uniform(4,8)))])
        elif category=='low_friction':sc=replace(sc,mu=float(rng.uniform(.15,.4)))
        elif category=='sensor_failure':sc=replace(sc,faults=[{'type':('radar_freeze','camera_unavailable','both_unavailable')[i%3],'t_s':2}])
        elif category=='communication_failure':sc=replace(sc,backup_enabled=i%3!=0,faults=[{'type':('drop_brake_req','drop_feedback','both_channels_lost')[i%3],'t_s':2}])
        elif category=='security_attack':sec.update(attack=('A02','A04','A12')[i%3],start_s=2,paths=['primary','backup'] if i%2 else ['primary'])
        elif category=='authentication_recovery':sec.update(attack=('A06','A10','CORRUPT_LEGIT')[i%3],wrong_tag=i%3==2,start_s=2)
        elif category=='ghost':sc=replace(sc,target_present=False,gap0_m=500,radar_false_positive=True,camera={'false_positive':i%3==0})
        elif category=='shared_ecu':sc=replace(sc,faults=[{'type':'brake_software_failure','t_s':2}])
        elif category=='actuator':sc=replace(sc,faults=[{'type':'actuator_failure','t_s':2}])
        elif category=='combined':
          sc=replace(sc,mu=.3,faults=[{'type':'radar_freeze','t_s':2},{'type':'drop_feedback','t_s':2.5}]);sec.update(attack='A08',start_s=2,delay_ms=120)
        elif category=='boundary':sc=replace(sc,ego_speed_kph=[9.9,10.,10.1,79.9,80.,80.1,0.,50.,81.][i],gap0_m=[8,8,8,60,60,60,4,5,60][i])
        cases.append(dict(category=category,seed=int(rng.integers(0,2**31)),scenario=asdict(sc),security=sec))
    return dict(method='12 predefined strata x9 independent parameter samples; seed1100907; descriptive stratified counts, not a traffic population',
                candidate=dict(security_policy='C',prefer_latest_authenticated=True,default_perception='legacy union; study alternatives not adopted'),cases=cases)
def main():
    manifest=build();data=json.dumps(manifest,indent=2);p=OUT/'final_case_manifest.json'
    if p.exists():assert p.read_text()==data,'final case manifest changed'
    else:p.write_text(data)
    (OUT/'final_case_manifest.sha256').write_text(hashlib.sha256(data.encode()).hexdigest()+'\n')
    print('frozen',len(manifest['cases']),'stratified cases')
if __name__=='__main__':main()
