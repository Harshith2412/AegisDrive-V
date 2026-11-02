#!/usr/bin/env python3
import json,statistics as stats
from collections import defaultdict
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.stats import wilson_interval
OUT=ROOT/'results/v0.3.0'
def summary(runs,interval=True):
    n=len(runs);c=sum(x['collision'] for x in runs)
    def mean(k):
        v=[x[k] for x in runs if x.get(k) is not None]
        return round(stats.mean(v),4) if v else None
    return dict(n=n,collisions=c,collision_fraction=c/n,ci95=list(wilson_interval(c,n)) if interval else None,
                min_gap_m=min(x['min_gap_m'] for x in runs),missed_detection_cycles_total=sum(x.get('missed_detection_cycles',0) for x in runs),
                false_interventions=sum(x.get('false_intervention',False) for x in runs),
                retriggers_total=sum(x.get('retrigger_count',0) for x in runs),
                mean_first_brake_s=mean('first_brake_request_s'),mean_first_sensor_loss_s=mean('first_sensor_loss_s'),
                mean_feedback_fault_s=mean('first_feedback_fault_s'),mean_achieved_fault_s=mean('first_achieved_fault_s'),
                mean_unavailable_s=mean('unavailable_duration_s'),mean_cpu_call_us=mean('adas_cpu_mean_us'),
                max_cpu_call_us=max(x.get('adas_cpu_max_us',0) for x in runs),
                single_source_degraded_runs=sum(x.get('degraded_perception_cycles',0)>0 for x in runs),
                successful_degraded_runs=sum(x.get('degraded_perception_cycles',0)>0 and not x['collision'] for x in runs),
                mean_command_to_active_ms=stats.mean([1000*(x['first_achieved_brake_s']-x['first_brake_request_s']) for x in runs if x['first_achieved_brake_s'] is not None and x['first_brake_request_s'] is not None]) if any(x['first_achieved_brake_s'] is not None and x['first_brake_request_s'] is not None for x in runs) else None)
def main():
    data=json.loads((OUT/'experiment_runs.json').read_text());groups=defaultdict(list)
    for r in data:
        key=r['scenario_id'] if r['split'] in ('original','fault_sotif') else r['split']
        groups[key].append(r)
    summaries={k:summary(v) for k,v in groups.items()}
    (OUT/'experiment_summary.json').write_text(json.dumps(summaries,indent=2))
    old=json.loads((OUT/'baseline/scenarios/vertical_slice_results.json').read_text())
    before={r['scenario']:r for r in old['scenarios']}
    lines=['# v0.3.0 quantitative evaluation','',f'{len(data)} candidate runs; frozen case manifest and all raw outcomes retained.',
           'Six original scenarios × four configurations × 20 seeds (480); 18 fault/SOTIF cases × 10 seeds (180);',
           '48 development and 120 hold-out parameter samples. Baseline reproduction includes 6×20 scenarios plus the original 16×20 sweep.',
           '', '| Original | v0.2 collisions /20 | v0.3 radar /20 | camera /20 | combined /20 | combined+backup /20 |', '|---|---|---|---|---|---|']
    for sid in before:
        vals=[summaries[sid+'_'+mode]['collisions'] for mode in ['radar','camera','combined','combined_backup']]
        lines.append('| '+' | '.join(map(str,[sid,before[sid]['collisions']]+vals))+' |')
    lines+=['','| Original | Baseline minimum gap (m) | Combined+backup minimum gap (m) | Baseline mean first command (s) | New mean first command (s) |','|---|---|---|---|---|']
    for sid,r in before.items():
        n=summaries[sid+'_combined_backup']
        lines.append(f"| {sid} | {r['min_gap_m_min']} | {n['min_gap_m']:.3f} | {r['mean_first_brake_request_s']} | {n['mean_first_brake_s']} |")
    lines+=['','| Case/configuration | n | Collisions | 95% Wilson interval | Minimum gap (m) | False interventions | Missed-detection cycles | Retriggers |','|---|---|---|---|---|---|---|---|']
    for k,s in summaries.items():
        lo,hi=s['ci95'];lines.append(f"| {k} | {s['n']} | {s['collisions']} | [{lo:.3f}, {hi:.3f}] | {s['min_gap_m']:.3f} | {s['false_interventions']} | {s['missed_detection_cycles_total']} | {s['retriggers_total']} |")
    lines+=['','| Case | First sensor loss / fault indication (s) | First brake command (s) | Command→active (ms) | Mean unavailable (s) | Degraded runs / successful without collision | CPU mean/max call (µs) |','|---|---|---|---|---|---|---|']
    for k,s in summaries.items():
        lines.append(f"| {k} | {s['mean_first_sensor_loss_s']} / feedback {s['mean_feedback_fault_s']} / achieved {s['mean_achieved_fault_s']} | {s['mean_first_brake_s']} | {s['mean_command_to_active_ms']} | {s['mean_unavailable_s']} | {s['single_source_degraded_runs']} / {s['successful_degraded_runs']} | {s['mean_cpu_call_us']} / {s['max_cpu_call_us']} |")
    lines+=['','All timing columns use simulation-start reference; fault onset is stored in each case config.',
      'FI01 freeze onset 2 s; last radar sample 1.95 s. Per-source loss detected at 2.11 s (110 ms from freeze, 160 ms from sample).',
      'Software/actuator failure onset 3 s; sensor/common loss 2 s; both-channel loss 4.2 s.',
      'Startup camera latency can cause early camera-only unavailability; distinguish it from a later injected failure.',
      'Missed detection is counted per control cycle while a real target is within 120 m and no usable target exists.',
      'Cached frames make these cycles correlated, not independent Bernoulli detections.',
      'False intervention requires explicitly target_present=false; this does not classify all unnecessary braking in real traffic.',
      'Intervals for repeated scenario seeds apply only to toy sensor randomness. Hold-out/development intervals are conditional',
      'on the declared independent artificial uniform parameter samples, not a traffic population. No aggregate real-world rate is inferred.',
      'Mean/max process CPU duration includes Python FFI and timing overhead and scheduler effects; not ECU-only execution or target WCET.',
      'Baseline CPU/false-detection/unavailability metrics were not implemented; absent baseline values are not assumed zero.',
      'Baseline v0.2.0 physical contact timing used endpoint checks; v0.3.0 resolves first within-step contact and stops at horizon.',
      'Original inputs are identical; this numerical correction is disclosed rather than rewriting old results.',
      'The held-out manifest was fixed before outcomes; failures are retained, and no post-outcome threshold tuning was performed.']
    (OUT/'evaluation.md').write_text('\n'.join(lines)+'\n')
    print({k:v for k,v in summaries.items() if k.startswith(('FI01','FI02')) or k in ['holdout','development','ecu_failed','actuator_failed','radar_ghost']})
if __name__=='__main__':main()
