"""v0.2 regression evidence; limits are project hypotheses, not ISO thresholds."""
from dataclasses import replace
import _paths
from _paths import SCENARIOS
from aegis_sim.runner import run_scenario
from aegis_sim.scenario import load_scenario
from aegis_sim.can_bus import InProcessCanBus
from aegis_sim import ecu_bindings as eb

# TEST-ID: ST-V2-001 | VERIFIES: TSR-201, TSR-202, FSR-201, FSR-202
def test_clearance_and_retrigger_regressions():
    for name in ('S02_lead_sudden_braking.yaml', 'S04_lead_gradual_decel.yaml'):
        for seed in range(20):
            r = run_scenario(load_scenario(SCENARIOS/name), seed)
            assert not r.collision
            assert r.min_gap_m >= 2.0
            assert r.states_visited.count('BRAKING') == 1

# TEST-ID: ST-V2-002 | VERIFIES: TSR-201, FSR-201
def test_wet_road_and_outside_design_limits():
    base = load_scenario(SCENARIOS/'S03_stationary_target.yaml')
    for speed in (60,80):
        for seed in range(20):
            r = run_scenario(replace(base, mu=0.5, ego_speed_kph=speed, gap0_m=4*speed/3.6), seed)
            assert not r.collision
    r = run_scenario(replace(base, ego_speed_kph=81), 0)
    assert r.collision and r.first_brake_request_s is None

# TEST-ID: ST-V2-003 | VERIFIES: TSR-203, FSR-203
def test_command_loss_indicated_without_claiming_collision_avoidance():
    for seed in range(20):
        r = run_scenario(load_scenario(SCENARIOS/'FI02_brake_req_loss_during_braking.yaml'), seed)
        assert r.first_feedback_fault_s is not None
        assert 0 <= r.first_feedback_fault_s - 4.2 <= .12 + 1e-9
        assert r.unavailable_indicated
        assert r.collision  # remaining single-path actuator limitation

# TEST-ID: ST-V2-004 | VERIFIES: TSR-203, FSR-203
def test_status_loss_has_no_unnecessary_braking():
    bus = InProcessCanBus(drop_filter=lambda f: f.arbitration_id == eb.CAN_ID_BRAKE_STATUS)
    r = run_scenario(load_scenario(SCENARIOS/'S01_normal_following.yaml'), 0, bus=bus)
    assert r.first_feedback_fault_s == .11
    assert r.unavailable_indicated
    assert r.first_brake_request_s is None
