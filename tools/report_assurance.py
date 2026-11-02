#!/usr/bin/env python3
"""Summarize every paired input, retaining adverse outcomes and undefined latencies."""
import json
import statistics as st
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/v0.2.0'
def group(path):
    d=defaultdict(list)
    for r in json.loads(path.read_text()): d[r['scenario_id']].append(r)
    return d

def mean(v,key):
    vals=[r[key] for r in v if r.get(key) is not None]
    return round(st.mean(vals),3) if vals else None

def main():
    old=group(ROOT/'baseline/v0.1.0/paired/runs.json'); new=group(OUT/'paired/runs.json')
    assert old.keys()==new.keys()
    rows=[]
    for sid in old:
        assert [r['seed'] for r in old[sid]]==[r['seed'] for r in new[sid]]==list(range(20))
        row={'scenario':sid}
        for label,runs in [('baseline',old[sid]),('modified',new[sid])]:
            row[label]=dict(collisions=sum(r['collision'] for r in runs),runs=len(runs),
                collision_rate=sum(r['collision'] for r in runs)/len(runs),
                min_separation_m=round(min(r['min_gap_m'] for r in runs),3),
                aeb_retriggers_total=sum(r['aeb_retriggers'] for r in runs),
                mean_first_warning_s=mean(runs,'first_warning_s'),
                mean_first_brake_request_s=mean(runs,'first_brake_request_s'),
                mean_braking_latency_ms=mean(runs,'braking_latency_ms'),
                mean_fault_detection_latency_ms=mean(runs,'fault_detection_latency_ms'))
        rows.append(row)
    (OUT/'comparison.json').write_text(json.dumps(rows,indent=2))
    lines=['# Before/after evaluation','',
      'Same scenario YAML, dt=10 ms, seeds 0–19 and common macOS dependency environment for both versions.',
      '420 paired runs per version: 6 original scenarios and 15 boundary/adverse configurations.',
      'The original 16-point stationary sweep is separately rerun for each version (320 runs each).',
      'Original v0.1.0 Linux evidence remains archived as well as the local macOS reproduction.','',
      '| Input | Collisions old → new (/20) | Minimum separation old → new (m) | Retriggers old → new (total) |',
      '|---|---|---|---|']
    for r in rows:
        a,b=r['baseline'],r['modified']
        lines.append(f"| {r['scenario']} | {a['collisions']} → {b['collisions']} | {a['min_separation_m']} → {b['min_separation_m']} | {a['aeb_retriggers_total']} → {b['aeb_retriggers_total']} |")
    lines+=['','| Scenario | First warning old → new (s) | First command old → new (s) | Command-to-active old → new (ms) | Fault detection old → new (ms) |','|---|---|---|---|---|']
    for r in rows[:6]:
        a,b=r['baseline'],r['modified']
        vals=[r['scenario']]+[f"{a[k]} → {b[k]}" for k in ['mean_first_warning_s','mean_first_brake_request_s','mean_braking_latency_ms','mean_fault_detection_latency_ms']]
        lines.append('| '+' | '.join(vals)+' |')
    lines+=['', 'Warning/command times are from simulation start. For S02/S04 the lead event begins at 2 s;',
      'subtract 2 s to obtain event-to-indication/command latency. S03 target exists at t=0.',
      'No independent ground-truth detection declaration exists: first warning is a decision timing proxy,',
      'not measured perception detection latency. Radar sampling is 50 ms; availability is checked each 10 ms.',
      'FI01 detection is 110 ms from freeze onset at 2 s, or 160 ms from last valid sample at 1.95 s.',
      'FI02 feedback fault is 120 ms from drop onset at 4.2 s. None means no measurement/undefined, never zero.',
      'Negative separation is not integrated after contact: min separation is clamped to 0 on collision.',
      'At 81 km/h activation is outside the speed window; collision is an intentional residual limitation.',
      'At mu=0.3 the planning assumption fails; these collisions remain in the report.',
      'At mu=0.5 the expanded envelope avoids the tested high-speed impacts; it is not a wet-road guarantee.',
      'Zero failures in 20 seeds gives a Wilson 95% upper collision-rate bound about 16.1%.',
      'Seeds vary only nominal radar noise. They do not sample real traffic populations or confidence errors.',
      'Wall-clock ctypes durations in raw JSON are host/FFI timings, not WCET.','',
      'Coverage: see coverage/summary.txt, coverage/mcdc-summary.txt and coverage/html/index.html.',
      'LLVM source coverage is scoped to six ecu/src C++ files from C++ unit + Python integration tests;',
      'scenario sweeps are not included. Baseline gcov is a different tool/denominator (unit tests only),',
      'so its percentages are preserved but not compared numerically to LLVM.',
      'Measured MC/DC condition coverage is partial, not a structural coverage adequacy claim.',
      'Requirement verification: see traceability_matrix.md (39/39 linked tests pass); this does not',
      'discharge the full safety goals or close the open issues in docs/v0.2.0_safety.md.']
    (OUT/'evaluation.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
