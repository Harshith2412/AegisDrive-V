#!/usr/bin/env python3
import json,statistics as st
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/v1.0.0'
def wilson(k,n):
 if n==0:return None
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*((p*(1-p)/n+z*z/(4*n*n))**.5)/d
 return [c-h,c+h]
def stats(runs):
 valid=[r for r in runs if r.get('supported',True)];n=len(valid)
 if not n:return dict(n=0,unsupported=len(runs))
 impacts=[r['impact_speed_mps'] for r in valid if r['collision']]
 missed=[r for r in valid if r.get('config',{}).get('scenario',{}).get('target_present',True) and r['collision'] and r['first_brake_request_s'] is None]
 reasons=defaultdict(int);legit=reject=0;cpu=[]
 for r in valid:
  sec=r.get('security_stats',{})
  for k,v in sec.get('verifier_counts',{}).items():reasons[k]+=v
  c=sec.get('counts',{});legit+=c.get('legitimate_offered',0);reject+=c.get('legitimate_rejected',0)
  if sec.get('verification_cpu_mean_us') is not None:cpu.append(sec['verification_cpu_mean_us'])
 return dict(n=n,unsupported=len(runs)-n,collisions=sum(r['collision'] for r in valid),
   unnecessary_braking=sum(r.get('unnecessary_braking',r.get('false_intervention',False)) for r in valid),
   min_clearance_m=min(r['min_gap_m'] for r in valid),mean_collision_impact_mps=st.mean(impacts) if impacts else None,
   max_collision_impact_mps=max(impacts) if impacts else None,missed_interventions=len(missed),
   native_timeout_runs=sum(r['brake_timeout_seen'] for r in valid),achieved_fault_runs=sum(r.get('first_achieved_fault_s') is not None for r in valid),
   selected_newer_backup_cycles=sum(r.get('authenticated_backup_preferred_cycles',0) for r in valid),
   mean_security_cpu_us=st.mean(cpu) if cpu else None,legitimate_rejections=reject,legitimate_offers=legit,
   verifier_decisions=dict(reasons))
def main():
 final={p:json.loads((OUT/f'final_{p}.json').read_text()) for p in ['v0.3.0','v0.4.0','candidate']}
 result={p:stats(r) for p,r in final.items()}
 cats=defaultdict(dict)
 for p,rs in final.items():
  for cat in sorted({r['category'] for r in rs}):cats[cat][p]=stats([r for r in rs if r['category']==cat])
 common={r['config']['scenario']['id'] for r in final['v0.3.0'] if r['supported']}
 result['matched_common_81']={p:stats([r for r in rs if (r.get('scenario_id') or r.get('id')) in common]) for p,rs in final.items()}
 (OUT/'comparison.json').write_text(json.dumps(dict(profiles=result,categories=cats),indent=2))
 lines=['# Final engineering robustness evaluation','',
  '108 predefined cases: twelve strata ×9 parameter samples (manifest seed1100907). This is a declared stratified case study, not a random traffic population.',
  'Actual archived v0.3.0 and v0.4.0 source/library builds are used. v0.3.0 has no security attack API: 27 cases are explicitly unsupported, never assigned invented outcomes.',
  'Common comparison denominator is 81 cases. Candidate is C + newest-authenticated-route selection, legacy union perception; study filters are not the default.',
  '', '| Stratum | v0.3 collisions/n | v0.4 collisions/n | Candidate collisions/n | Candidate unnecessary brake | Candidate max impact (m/s) |','|---|---|---|---|---|---|']
 for cat,data in cats.items():
  cells=[]
  for p in ['v0.3.0','v0.4.0','candidate']:
   s=data[p];cells.append(f"{s.get('collisions',0)}/{s['n']}" if s['n'] else 'UNSUPPORTED')
  c=data['candidate'];lines.append('| '+' | '.join([cat]+cells+[str(c['unnecessary_braking']),str(c['max_collision_impact_mps'])])+' |')
 lines+=['','Overall supported denominators: '+str({p:(r['collisions'],r['n']) for p,r in result.items() if p!='matched_common_81'}),
  'Strictly common 81-case comparison: '+str({p:(r['collisions'],r['n']) for p,r in result['matched_common_81'].items()}),
  'All raw minimum gaps, impact speeds, missed interventions, timeout/achieved-response indicators, authentication decisions, legitimate rejection counts and host CPU times are retained in comparison.json and final_*.json.',
  'Unnecessary-braking counts require target_present=false and achieved braking; a zero count with a real target does not establish justified timing/intensity. There is no following-vehicle model.',
  'The candidate route preference is exercised but does not reduce the overall collision count in this final set. No aggregate safety improvement is claimed.']
 locked=json.loads((OUT/'locked_candidate.json').read_text())
 lines+=['','| Existing locked set | n | Candidate collisions | Wilson 95% interval (conditional illustrative noise/sample model) |','|---|---|---|---|']
 for split,mode in [('locked_v3_holdout','C'),('new_security_holdout','B'),('new_security_holdout','C')]:
  rs=[r for r in locked if r['split']==split and r['security_config']['mode']==mode];k=sum(r['collision'] for r in rs)
  lo,hi=wilson(k,len(rs));lines.append(f'| {split} / {mode} | {len(rs)} | {k} | [{lo:.3f}, {hi:.3f}] |')
 lines+=['','These previously exposed sets are not unseen validation. Intervals describe conditional artificial sampling only; message counts are correlated and do not justify binomial attack-probability claims.',
  'No binomial interval is assigned to the intentionally stratified 108-case aggregate. Exact counts per stratum/denominator are the defensible result. Physical impact uses relative speed only, not injury severity or crash energy without mass.']
 study=json.loads((OUT/'perception_study.json').read_text());groups=defaultdict(list)
 for r in study:groups[(r['case'],r['profile'])].append(r)
 lines+=['','## Controlled perception/braking study','', '| Case | Profile | Collisions/n | Unnecessary braking/n | Max achieved decel | No request collisions |','|---|---|---|---|---|---|']
 for (case,profile),rs in groups.items():
  lines.append(f"| {case} | {profile} | {sum(r['collision'] for r in rs)}/{len(rs)} | {sum(r['unnecessary_braking'] for r in rs)}/{len(rs)} | {max(r['max_actual_decel_mps2'] for r in rs):.3f} | {sum(r['collision'] and r['first_brake_request_s'] is None for r in rs)} |")
 lines+=['','200 study runs, 216 locked-set candidate runs, and 297 actually supported final-version runs are distinct executed batches (713 runs), in addition to 846 baseline reproductions.',
  'A prior study attempt is retained: confidence was initially lowered after the fusion gate without being consumed by native ADAS; the corrected study explicitly re-gates availability. No final-hold-out threshold tuning occurred.',
  'Temporal/corroboration profiles can suppress brief/isolated ghosts while introducing genuine-obstacle misses/collisions. Persistent common ghosts remain. The 3 m/s² cap changes planning and emergency threshold as documented; no independent follower model exists.',
  'Logical cryptographic computation delay remains zero. Host CPU timing includes interpreter/FFI/OS effects and is not ECU target WCET.',
  'Recovery selection/time: verified requests are compared in the same 10 ms control step; per-path freshness policy remains B/C. Diagnostic pressure recovery requires 100 ms clear dwell; event traces/tests define transition timing, not a guaranteed collision rescue deadline.']
 (OUT/'evaluation.md').write_text('\n'.join(lines)+'\n')
 print({p:(r['collisions'],r['n']) for p,r in result.items() if p!='matched_common_81'})
if __name__=='__main__':main()
