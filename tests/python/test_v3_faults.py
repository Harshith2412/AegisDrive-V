from dataclasses import replace
import _paths
from _paths import SCENARIOS
from aegis_sim.runner import run_scenario
from aegis_sim.scenario import load_scenario
BASE=load_scenario(SCENARIOS/'S03_stationary_target.yaml')

# TEST-ID: ST-V3-001 | VERIFIES: PER-302
def test_radar_loss_camera_recovery_and_both_sensor_loss():
    sc=load_scenario(SCENARIOS/'FI01_radar_freeze_before_threat.yaml')
    for seed in range(20):
        r=run_scenario(replace(sc,perception='combined'),seed)
        assert not r.collision and 'CAMERA_ONLY' in r.perception_modes
        assert abs(r.first_sensor_loss_s-2.11)<1e-9
    r=run_scenario(replace(BASE,perception='combined',faults=[{'type':'both_unavailable','t_s':2}]),0)
    assert r.collision and r.unavailable_indicated
    assert r.first_brake_request_s is None # no blind emergency initiation

# TEST-ID: ST-V3-002 | VERIFIES: BRK-301
def test_backup_command_path_and_common_actuator_failures():
    sc=load_scenario(SCENARIOS/'FI02_brake_req_loss_during_braking.yaml')
    for seed in range(20):
        r=run_scenario(replace(sc,perception='combined',backup_enabled=True,imu_monitor=True),seed)
        assert not r.collision and not r.brake_timeout_seen
        assert r.backup_received_cycles>0
    for kind in ('brake_software_failure','actuator_failure'):
        r=run_scenario(replace(BASE,perception='combined',backup_enabled=True,imu_monitor=True,
                              faults=[{'type':kind,'t_s':3}]),0)
        assert r.collision # same physical actuator; backup CAN cannot brake it
        assert r.first_achieved_fault_s is not None
        assert r.first_achieved_fault_s<4.5

# TEST-ID: ST-V3-003 | VERIFIES: DIA-301
def test_feedback_loss_intermittent_delays_and_duplicates():
    r=run_scenario(replace(BASE,imu_monitor=True,faults=[{'type':'drop_feedback','t_s':2}]),0)
    assert not r.collision and r.first_feedback_fault_s==2.11
    for cfg in ({'faults':[{'type':'intermittent_req','t_s':2}]},
                {'network_delay_ms':60}, {'network_duplicate':True}):
        r=run_scenario(replace(BASE,backup_enabled=True,imu_monitor=True,**cfg),0)
        assert not r.collision and r.illegal_transitions==0

# TEST-ID: ST-V3-004 | VERIFIES: PER-302
def test_camera_unavailable_disagreement_and_false_intervention_limit():
    r=run_scenario(replace(BASE,perception='combined',faults=[{'type':'camera_unavailable','t_s':2}]),0)
    assert not r.collision and 'RADAR_ONLY' in r.perception_modes
    r=run_scenario(replace(BASE,perception='combined',radar_bias_m=30),0)
    assert r.disagreement_cycles>0 and r.collision # no justified winning sensor
    empty=replace(BASE,target_present=False,gap0_m=500,perception='combined')
    assert not run_scenario(empty,0).false_intervention
    # A plausible isolated high-confidence ghost can pass current union policy.
    ghost=run_scenario(replace(empty,radar_false_positive=True),0)
    assert ghost.false_intervention # negative evidence retained
