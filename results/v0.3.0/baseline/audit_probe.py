import sys,json
sys.path.insert(0,'sim')
from aegis_sim.runner import run_scenario
from aegis_sim.scenario import load_scenario
from dataclasses import replace
sc=load_scenario('scenarios/S03_stationary_target.yaml')
runs=[run_scenario(sc,s).to_dict() for s in range(5)]
for r in runs:
 r.pop('adas_step_mean_us');r.pop('adas_step_max_us')
json.dump(dict(distinct_full_runs=len({json.dumps(r,sort_keys=True) for r in runs}),runs=runs),open('results/v0.3.0/baseline/seed_probe.json','w'),indent=2)
