from dataclasses import replace
import _paths
from _paths import SCENARIOS
from aegis_sim.runner import run_scenario
from aegis_sim.scenario import load_scenario
BASE=load_scenario(SCENARIOS/'S03_stationary_target.yaml')

def run(mode,attack=None,empty=False,backup=False,**cfg):
    sc=replace(BASE,perception='combined',backup_enabled=backup,imu_monitor=True,
               target_present=not empty,gap0_m=500 if empty else BASE.gap0_m)
    return run_scenario(sc,0,security=dict(mode=mode,attack=attack,start_s=2,**cfg))

# TEST-ID: SEC-ST-001 | VERIFIES: SEC-403
def test_smallest_secure_command_path_and_status_broadcast():
    for mode in ('A','B','C'):
        r=run(mode)
        assert not r.collision and r.brake_rejected_frames==0
        assert r.brake_lamp_latency_ms<=10
        assert r.security_stats['counts'].get('legitimate_rejected',0)==0
        if mode!='A':assert r.security_stats['verifier_counts']['ACCEPT']>1000

# TEST-ID: SEC-ST-002 | VERIFIES: SEC-401, SEC-403, SEC-404
def test_forgery_rejection_is_distinct_from_trusted_compromise():
    for attack in ('A01','A03','A04'):
        assert run('A',attack,empty=True).unnecessary_braking
        r=run('B',attack,empty=True)
        assert not r.unnecessary_braking
        assert r.first_security_dtc_s is not None
    # Correct MAC from compromised authorized ADAS cannot establish benign intent.
    assert run('C','A12',empty=True).unnecessary_braking

# TEST-ID: SEC-ST-003 | VERIFIES: SEC-402, SEC-404
def test_desynchronization_has_safety_cost_and_bounded_resync_recovers():
    a,b,c=(run(m,'A06') for m in ('A','B','C'))
    assert not a.collision and b.collision and not c.collision
    assert b.security_stats['counts']['legitimate_rejected']>0
    assert c.security_stats['verifier_counts']['RESYNC']>0
    assert run('B','A06',backup=True,paths=['primary']).collision is False

# TEST-ID: SEC-ST-004 | VERIFIES: SEC-404, SEC-405
def test_gateway_loss_and_flood_are_availability_events():
    r=run('B',gateway_down=True,paths=['primary'])
    assert r.collision and r.first_feedback_fault_s is not None
    # Do not use injected gateway failure onset as a fabricated detection timestamp.
    assert r.security_stats['first_event_s'] is None
    flood=run('C','A07',backup=True)
    assert flood.security_stats['counts']['flood_injected']>0
    assert flood.security_stats['primary_max_backlog']<=64
    assert flood.security_stats['counts']['BUS_PRESSURE']>0
    # Authentication failure on legitimate commands can also defeat braking.
    assert run('B','CORRUPT_LEGIT',wrong_tag=True).collision
    assert not run('B','CORRUPT_LEGIT',wrong_tag=True,backup=True,paths=['primary']).collision

# TEST-ID: SEC-ST-005 | VERIFIES: SEC-402
def test_replay_stale_and_duplicates_rejected_without_claiming_avoidance():
    for attack,reason in [('A02','STALE'),('A05','STALE'),('A09','REPLAY')]:
        r=run('B',attack)
        assert r.security_stats['verifier_counts'][reason]>0
        assert r.security_stats['counts'].get('attack_accepted',0)==0
    delayed=run('B','A08')
    assert not delayed.collision and delayed.security_stats['counts']['attack_accepted']>0 # within configured age

# TEST-ID: SEC-ST-006 | VERIFIES: SEC-403
def test_authenticated_implausible_sensor_is_not_used_as_valid_target():
    sc=replace(BASE,perception='radar',imu_monitor=True)
    r=run_scenario(sc,0,security=dict(mode='B',attack='A11',start_s=2))
    assert r.security_stats['counts']['sensor_attack_accepted']>0 # MAC correct
    assert 'DEGRADED' in r.states_visited and r.first_brake_request_s is None
    assert r.collision # refusing all available perception is not collision prevention
