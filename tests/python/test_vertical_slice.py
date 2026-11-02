"""System-level SiL tests of the vertical slice (real C++ ECUs in closed loop)."""
from dataclasses import replace

import _paths  # noqa: F401
from _paths import SCENARIOS
from aegis_sim import ecu_bindings as eb
from aegis_sim.can_bus import CanFrame, InProcessCanBus
from aegis_sim.runner import run_scenario
from aegis_sim.scenario import load_all, load_scenario

S01 = SCENARIOS / "S01_normal_following.yaml"
S02 = SCENARIOS / "S02_lead_sudden_braking.yaml"
S03 = SCENARIOS / "S03_stationary_target.yaml"
S04 = SCENARIOS / "S04_lead_gradual_decel.yaml"
FI01 = SCENARIOS / "FI01_radar_freeze_before_threat.yaml"
FI02 = SCENARIOS / "FI02_brake_req_loss_during_braking.yaml"


# TEST-ID: ST-SLICE-001 | VERIFIES: SYS-REQ-001, ADAS-REQ-002, ADAS-REQ-003, ADAS-REQ-005, BRK-REQ-005, BCM-REQ-001, BCM-REQ-003
def test_end_to_end_stationary_target_chain():
    r = run_scenario(load_scenario(S03), seed=0)
    assert not r.collision
    assert r.first_warning_s is not None and r.first_brake_request_s is not None
    assert r.first_warning_s < r.first_brake_request_s
    assert 1.6 < r.ttc_at_brake_request_s < 2.6  # stopping envelope acts before legacy TTC
    assert r.first_brake_active_s is not None
    assert r.brake_lamp_latency_ms is not None and r.brake_lamp_latency_ms <= 10.0
    assert r.hazard_activated == (r.max_requested_decel_mps2 >= 6.0)
    assert r.states_visited == ["MONITORING", "WARNING", "BRAKING", "STANDBY"]
    assert r.final_ego_speed_mps == 0.0
    assert r.brake_rejected_frames == 0 and r.body_rejected_frames == 0 and r.illegal_transitions == 0


# TEST-ID: ST-SLICE-002 | VERIFIES: SYS-REQ-001
def test_stationary_target_speed_points_are_avoided():
    base = load_scenario(S03)
    for kph in (20, 30, 40, 50):
        for seed in range(20):
            r = run_scenario(replace(base, ego_speed_kph=float(kph)), seed=seed)
            assert not r.collision, (kph, seed, r.impact_speed_mps)


# TEST-ID: ST-SLICE-003 | VERIFIES: SYS-REQ-002, ADAS-REQ-002
def test_no_intervention_without_threat():
    for seed in range(10):
        r = run_scenario(load_scenario(S01), seed=seed)
        assert not r.collision
        assert r.first_warning_s is None and r.first_brake_request_s is None
        assert r.states_visited == ["MONITORING"]


# TEST-ID: ST-SLICE-004 | VERIFIES: SYS-REQ-003
def test_lead_braking_scenarios_are_avoided():
    for path in (S02, S04):
        for seed in range(10):
            r = run_scenario(load_scenario(path), seed=seed)
            assert not r.collision, (path.name, seed)


# TEST-ID: ST-FI-001 | VERIFIES: FSR-001, TSR-001, BCM-REQ-004
def test_frozen_radar_is_detected_and_brake_not_requested():
    r = run_scenario(load_scenario(FI01), seed=0)
    last_valid_ts_s = 1.95  # last radar sample before the freeze at t = 2.0 s (50 ms period)
    assert r.first_degraded_s is not None
    assert r.first_degraded_s - last_valid_ts_s <= 0.150 + 0.010 + 1e-9
    assert r.first_brake_request_s is None
    assert r.unavailable_indicated
    # Documented consequence (not a pass criterion of the mechanism): without a redundant
    # sensor, AEB is unavailable and the collision is NOT mitigated. See results report.
    assert r.collision


# TEST-ID: ST-FI-002 | VERIFIES: BRK-REQ-002, TSR-003
def test_brake_command_loss_triggers_timeout():
    r = run_scenario(load_scenario(FI02), seed=0)
    assert r.first_brake_request_s is not None and r.first_brake_request_s < 4.2
    assert r.brake_timeout_seen
    assert r.first_brake_timeout_s - r.last_brake_req_delivered_s <= 0.110 + 1e-9


def _tamper_brake_req(fix_crc: bool, decel_raw: int):
    def tamper(fr: CanFrame) -> CanFrame:
        if fr.arbitration_id != eb.CAN_ID_BRAKE_REQ:
            return fr
        d = bytearray(fr.data)
        d[2] = 0x03  # active + emergency
        d[3], d[4] = decel_raw & 0xFF, decel_raw >> 8
        if fix_crc:
            d[0] = eb.crc8(bytes([0x20, 0x01]) + bytes(d[1:8]))
        return CanFrame(fr.arbitration_id, bytes(d), fr.timestamp_ms, fr.sender + "+tampered")
    return tamper


# TEST-ID: ST-INV-001 | VERIFIES: BRK-REQ-001, TSR-002
def test_corrupted_brake_commands_are_rejected_without_actuation():
    sc = replace(load_scenario(S01), duration_s=3.0)
    for fix_crc, raw in ((False, 900), (True, 1200)):  # bad CRC; valid CRC but out of range (12 m/s^2)
        bus = InProcessCanBus(tamper=_tamper_brake_req(fix_crc, raw))
        r = run_scenario(sc, seed=0, bus=bus)
        assert r.first_brake_active_s is None and r.max_actual_decel_mps2 < 0.5
        assert r.brake_rejected_frames >= 290


# TEST-ID: ST-INV-002 | CHARACTERIZES: OI-005
def test_known_gap_crc_is_not_authentication():
    """A manipulated frame with a recomputed CRC and an in-range value IS accepted.

    This characterises the expected limitation of E2E protection (fault detection, not
    security). It must start failing once Phase 7 message authentication is added.
    """
    sc = replace(load_scenario(S01), duration_s=3.0)
    bus = InProcessCanBus(tamper=_tamper_brake_req(True, 800))
    r = run_scenario(sc, seed=0, bus=bus)
    assert r.first_brake_active_s is not None  # unnecessary braking was induced
    assert r.max_actual_decel_mps2 > 7.0


# TEST-ID: ST-SLICE-005 | VERIFIES: SIM-REQ-002
def test_runs_are_reproducible_per_seed():
    sc = load_scenario(S03)
    a, b, c = (run_scenario(sc, seed=s) for s in (3, 3, 4))
    strip = lambda r: {k: v for k, v in r.to_dict().items() if not k.startswith(("adas_step", "adas_cpu"))}  # noqa: E731
    assert strip(a) == strip(b)
    assert strip(a) != strip(c)


# TEST-ID: ST-SLICE-006 | VERIFIES: ADAS-REQ-007
def test_no_illegal_transitions_in_any_scenario():
    for sc in load_all(SCENARIOS):
        assert run_scenario(sc, seed=0).illegal_transitions == 0, sc.id
