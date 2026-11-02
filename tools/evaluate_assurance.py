#!/usr/bin/env python3
"""Paired inputs for baseline and candidate; timings are simulation times, not WCET."""
import csv
import json
import os
import sys
from dataclasses import replace
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(os.environ.get('AEGIS_SOURCE_ROOT', ROOT)) / 'sim'))
from aegis_sim.scenario import load_all, load_scenario
from aegis_sim.runner import run_scenario

def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    cases = load_all(ROOT / 'scenarios')
    base = load_scenario(ROOT / 'scenarios/S03_stationary_target.yaml')
    for mu in (0.9, 0.5, 0.3):
        for speed in (10, 50, 60, 80, 81):
            cases.append(replace(base, id=f'B_mu{mu}_v{speed}', mu=mu, ego_speed_kph=speed,
                                 gap0_m=max(40., 4*speed/3.6), duration_s=22.))
    records = []
    for sc in cases:
        for seed in range(20):
            trace = out / 'trace.csv'
            r = run_scenario(sc, seed=seed, trace_path=trace)
            rows = list(csv.DictReader(trace.open()))
            states = [x['adas_state'] for x in rows]
            entries = sum(s == 'BRAKING' and (i == 0 or states[i-1] != s) for i,s in enumerate(states))
            d = r.to_dict()
            d.update(aeb_retriggers=max(0,entries-1), mu=sc.mu, ego_speed_kph=sc.ego_speed_kph,
                     braking_latency_ms=None if r.first_brake_active_s is None or r.first_brake_request_s is None else
                     round(1000*(r.first_brake_active_s-r.first_brake_request_s),3))
            if sc.faults:
                onset = sc.faults[0]['t_s']
                detected = getattr(r, 'first_feedback_fault_s', None) if sc.id == 'FI02' else r.first_degraded_s
                d['fault_detection_latency_ms'] = None if detected is None else round(1000*(detected-onset),3)
            records.append(d)
        print(sc.id, sum(x['collision'] for x in records[-20:]), flush=True)
    trace.unlink()
    (out/'runs.json').write_text(json.dumps(records, indent=2))

if __name__ == '__main__': main()
