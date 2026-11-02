"""Unit tests for the simulation plant, sensor model and virtual CAN bus."""
import math

import numpy as np

import _paths  # noqa: F401
from aegis_sim.can_bus import CanFrame, InProcessCanBus
from aegis_sim.sensors import RadarModel
from aegis_sim.vehicle import G_MPS2, Vehicle, friction_limited_decel


# TEST-ID: UT-SIM-001 | VERIFIES: SIM-REQ-001
def test_constant_decel_stopping_distance_matches_closed_form():
    v0, a = 13.89, 8.0
    veh = Vehicle(0.0, v0)
    for _ in range(1000):
        veh.step(0.01, -a)
    assert veh.v_mps == 0.0
    assert math.isclose(veh.x_m, v0 * v0 / (2 * a), rel_tol=1e-9)


# TEST-ID: UT-SIM-002 | VERIFIES: SIM-REQ-001
def test_friction_limits_braking():
    assert math.isclose(friction_limited_decel(9.0, 0.5), 0.5 * G_MPS2)
    assert friction_limited_decel(-1.0, 0.9) == 0.0
    assert friction_limited_decel(3.0, 0.9) == 3.0


# TEST-ID: UT-SIM-003 | VERIFIES: SIM-REQ-002
def test_radar_is_deterministic_and_timestamped():
    def run(seed):
        r = RadarModel(np.random.default_rng(seed), period_ms=50, latency_ms=20)
        out = []
        for t in range(0, 300, 10):
            m = r.update(t, 50.0, -5.0)
            out.append(None if m is None else (m.ts_ms, round(m.range_m, 9)))
        return out
    a, b, c = run(7), run(7), run(8)
    assert a == b and a != c
    assert a[0] is None and a[1] is None and a[2] == (0, a[2][1])  # 20 ms latency, ts = sampling time
    assert a[7][0] == 50


# TEST-ID: UT-SIM-004 | VERIFIES: SIM-REQ-002, FSR-001
def test_radar_freeze_stops_timestamp():
    r = RadarModel(np.random.default_rng(0), freeze_at_ms=100)
    seen = {r.update(t, 40.0, 0.0).ts_ms for t in range(0, 500, 10)}
    assert max(seen) == 50


# TEST-ID: UT-SIM-005 | VERIFIES: SIM-REQ-003
def test_bus_has_one_cycle_latency_and_logs_frames():
    bus = InProcessCanBus()
    bus.send(CanFrame(0x120, bytes(8), 0, "ADAS"))
    assert bus.receive(0x120) is None
    bus.advance()
    assert bus.receive(0x120).timestamp_ms == 0
    bus.advance()
    assert bus.receive(0x120) is None
    assert len(bus.log) == 1
    try:
        CanFrame(0x800, bytes(8), 0, "x")
    except ValueError:
        return
    raise AssertionError("29-bit id accepted")
