#!/usr/bin/env python3
"""Descriptive matched security/safety metrics, retaining all negative outcomes."""
import json,statistics as st,sys
from collections import defaultdict,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/v0.4.0'
def summarize(runs):
    c=Counter();reasons=Counter();verify=[];tx=[]
    for r in runs:
        q=r['security_stats'];c.update(q['counts']);reasons.update(q['verifier_counts'])
        if q['verification_cpu_mean_us'] is not None:verify.append(q['verification_cpu_mean_us'])
        if q['tx_cpu_mean_us'] is not None:tx.append(q['tx_cpu_mean_us'])
    def mean(k):
        vals=[r[k] for r in runs if r.get(k) is not None];return st.mean(vals) if vals else None
    return dict(n=len(runs),collisions=sum(r['collision'] for r in runs),unnecessary_braking_runs=sum(r['unnecessary_braking'] for r in runs),
      min_gap_m=min(r['min_gap_m'] for r in runs),mean_first_request_s=mean('first_brake_request_s'),mean_first_achieved_brake_s=mean('first_achieved_brake_s'),
      mean_unavailable_s=mean('unavailable_duration_s'),mean_security_dtc_s=mean('first_security_dtc_s'),
      mean_observed_security_event_s=st.mean(v) if (v:=[r['security_stats']['first_event_s'] for r in runs if r['security_stats']['first_event_s'] is not None]) else None,
      adas_mean_cpu_us=mean('adas_cpu_mean_us'),mean_verification_cpu_us=st.mean(verify) if verify else None,
      max_verification_cpu_us=max((r['security_stats']['verification_cpu_max_us'] or 0 for r in runs),default=0),
      mean_tx_cpu_us=st.mean(tx) if tx else None,counts=dict(c),verifier_decisions=dict(reasons),
      gateway_command_delivery_fraction=c['commands_gateway_delivered']/c['commands_generated'] if c['commands_generated'] else None,
      legitimate_rejection_fraction=c['legitimate_rejected']/c['legitimate_offered'] if c['legitimate_offered'] else None,
      attack_gateway_acceptance_fraction=c['attack_accepted']/c['attack_offered'] if c['attack_offered'] else None,
      native_attack_acceptance_primary_only=c['native_attack_accepted_primary_only']/c['native_attack_offered_primary_only'] if c['native_attack_offered_primary_only'] else None,
      security_related_degraded_runs=sum(r['first_security_dtc_s'] is not None for r in runs),
      maximum_queue_backlog=max(r['security_stats']['primary_max_backlog'] for r in runs),
      queue_drops_total=sum(r['security_stats']['primary_queue_drops']+r['security_stats']['backup_queue_drops'] for r in runs))

def main():
    runs=json.loads((OUT/'experiment_runs.json').read_text());groups=defaultdict(list)
    for r in runs:
        key=r['scenario_id'] if r['split'] not in ('locked_v3_holdout','new_security_holdout') else r['split']
        groups[(r['split'],key,r['security_config']['mode'])].append(r)
    stats={f'{split}/{case}/{mode}':summarize(v) for (split,case,mode),v in groups.items()}
    (OUT/'experiment_summary.json').write_text(json.dumps(stats,indent=2))
    lines=['# v0.4.0 security and safety evaluation','',f'{len(runs)} runs: 180 attack-matrix, 72 safety-security interaction, 90 attack-free, 360 locked-v0.3 hold-out, 144 new security hold-out.',
      'A = existing unauthenticated payloads/E2E, B = authentication + strict freshness, C = authentication + bounded authenticated resynchronization.',
      'All policies use matched inputs/seeds and the same bounded frame-budget fabric. Original v0.3 behavior is reproduced separately in baseline/.',
      '', '| Split / case | Mode | n | Collisions | Unnecessary braking | Minimum gap (m) | Legitimate rejections / offered | Attack rejected / offered | Native attack accepted / offered (primary only) |',
      '|---|---|---|---|---|---|---|---|---|']
    for key,s in stats.items():
        split,case,mode=key.split('/');c=s['counts']
        lines.append(f"| {split}/{case} | {mode} | {s['n']} | {s['collisions']} | {s['unnecessary_braking_runs']} | {s['min_gap_m']:.3f} | {c.get('legitimate_rejected',0)} / {c.get('legitimate_offered',0)} | {c.get('attack_rejected',0)} / {c.get('attack_offered',0)} | {c.get('native_attack_accepted_primary_only',0)} / {c.get('native_attack_offered_primary_only',0)} |")
    lines+=['','| Case/config | Gateway command availability | Verification CPU mean/max (µs) | Tx CPU mean (µs) | First request / achieved brake (s) | First observed event / C++ DTC (s) | Mean unavailable (s) | Queue drops |','|---|---|---|---|---|---|---|---|']
    for key,s in stats.items():
        lines.append(f"| {key} | {s['gateway_command_delivery_fraction']} | {s['mean_verification_cpu_us']} / {s['max_verification_cpu_us']} | {s['mean_tx_cpu_us']} | {s['mean_first_request_s']} / {s['mean_first_achieved_brake_s']} | {s['mean_observed_security_event_s']} / {s['mean_security_dtc_s']} | {s['mean_unavailable_s']} | {s['queue_drops_total']} |")
    lines+=['','Metrics and interpretation:',
      '- Message rates are descriptive, not independent Bernoulli trials: cached sensor PDUs, repeated commands and broadcast subscriptions are correlated.',
      '- Native acceptance is reported only with no backup so the accepted channel is unambiguous. Gateway delivery is not proof of CRC acceptance or safe actuation.',
      '- Sensor attack accepted/rejected counts are separate in raw JSON; A01/11 do not inject a command directly. Unnecessary braking measures achieved braking with no actual target, including injected actuation invisible to ADAS request state.',
      '- In attack-free runs, correctly formed in-policy legitimate offers measure false rejection. Operational legitimate-demand loss under tag/freshness faults is a different quantity. Bad-tag rejection is correct cryptographic behavior, even when it removes a legitimate driver-assistance demand.',
      '- Legitimate rejection includes explicitly valid producer/freshness faults and bad-tag transmission, and counts verifier offers; withheld or queue-dropped messages are separately recorded, not silently called accepted.',
      '- Command availability = gateway-delivered command frames / generated frames across configured paths; it is not physical braking availability. Body/ADAS broadcast subscribers are counted separately in verifier offer statistics.',
      '- First-event and DTC times use simulation start; subtract each stored injection onset for response latency. Gateway-down injection itself is not an observed detection; existing native feedback timeout provides that signal.',
      '- First request and achieved-brake columns together support intervention/build-up latency; None means undefined, never zero. CPU measurements are host process timings including Python parsing, HMAC, FFI and concurrent host effects, not target ECU WCET.',
      '- Protected packets are 64 CAN FD bytes versus 8 legacy payload bytes: 56 added bytes per command/status. Sensor messages have 21 bytes payload plus 43 envelope/padding/tag bytes. Sensor crypto/transport scheduling is not physically modeled; measured CPU is not injected into logical time.',
      '- No aggregate attack probability is inferred. For repeated per-case seeds, safety counts are conditional on the toy noise model. New security hold-outs use a fixed artificial parameter/attack mixture; no real-world frequency claim.',
      '- Original 120 hold-outs are unchanged and already known; the 48 new security cases were fixed before execution, not described as hidden from the implementer. No thresholds were tuned against their outcomes.']
    old=json.loads((ROOT/'results/v0.3.0/experiment_runs.json').read_text())
    old_by={r['scenario_id']:r for r in old if r['split']=='holdout'}
    mismatches=[]
    for r in runs:
        if r['split']=='locked_v3_holdout' and r['security_config']['mode']=='A':
            o=old_by[r['scenario_id']]
            if r['config']!=o['config'] or r['seed']!=o['seed']:mismatches.append(r['scenario_id'])
    assert not mismatches
    (OUT/'evaluation.md').write_text('\n'.join(lines)+'\n')
    print('wrote',len(stats),'matched summaries')
if __name__=='__main__':main()
