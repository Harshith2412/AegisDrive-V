#!/usr/bin/env python3
import sys,json
from pathlib import Path
from dataclasses import replace
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.scenario import load_scenario
from aegis_sim.runner import run_scenario
OUT=ROOT/'results/v1.0.0/reference';OUT.mkdir(parents=True,exist_ok=True)
sc=replace(load_scenario(ROOT/'scenarios/S03_stationary_target.yaml'),perception='combined',backup_enabled=True,imu_monitor=True)
config=dict(mode='C',attack='A08',start_s=2,delay_ms=60,paths=['primary'])
events=[]
r=run_scenario(sc,0,trace_path=OUT/'trace.csv',security=config,assurance={'prefer_latest_authenticated':True},event_sink=events.append)
(OUT/'result.json').write_text(json.dumps(dict(config=config,result=r.to_dict(),events=events),indent=2))
print(json.dumps(dict(collision=r.collision,min_gap_m=r.min_gap_m,newer_backup_selected_cycles=r.authenticated_backup_preferred_cycles,
                     first_request_s=r.first_brake_request_s,first_achieved_brake_s=r.first_achieved_brake_s,
                     evidence='results/v1.0.0/reference/result.json'),indent=2))
