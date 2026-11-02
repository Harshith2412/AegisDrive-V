"""Software integration tests: Python <-> compiled C++ ECU library via the C ABI."""
import ctypes
import math

import _paths  # noqa: F401
from aegis_sim import ecu_bindings as eb


# TEST-ID: IT-ABI-001 | VERIFIES: SWR-001
def test_abi_version_and_struct_layouts_match():
    lib = eb.lib()
    assert lib.aegis_abi_version() == eb.ABI_VERSION
    for idx, st in enumerate(eb._STRUCTS):
        assert lib.aegis_struct_size(idx) == ctypes.sizeof(st), st.__name__
    assert lib.aegis_struct_size(99) == 0


# TEST-ID: IT-ABI-002 | VERIFIES: SWR-001
def test_mismatched_layout_is_refused():
    class Lib:  # stand-in library reporting a different struct size
        @staticmethod
        def aegis_abi_version():
            return eb.ABI_VERSION

        @staticmethod
        def aegis_struct_size(idx):
            return 1

    try:
        eb.verify_abi(Lib())
    except eb.AbiMismatchError:
        return
    raise AssertionError("ABI mismatch was not detected")


# TEST-ID: IT-ABI-003 | VERIFIES: SWR-002, ADAS-REQ-001
def test_python_calls_real_cpp_algorithms():
    assert eb.crc8(b"123456789") == 0x4B
    lib = eb.lib()
    assert math.isclose(lib.aegis_compute_ttc(20.0, -10.0, 0.5), 2.0)
    assert math.isinf(lib.aegis_compute_ttc(20.0, 1.0, 0.5))
    cfg = lib.aegis_adas_default_config()
    assert math.isclose(cfg.ttc_warning_s, 2.6) and math.isclose(cfg.ttc_brake_s, 1.6)
    assert cfg.stale_timeout_ms == 150


# TEST-ID: IT-ABI-004 | VERIFIES: ADAS-REQ-007
def test_illegal_transition_rejected_through_c_api():
    ecu = eb.AdasEcu()
    assert ecu.state == 0
    assert not ecu.request_transition(4)  # DISABLED -> BRAKING
    assert ecu.request_transition(1)       # DISABLED -> STANDBY
    assert not ecu.request_transition(4)  # STANDBY -> BRAKING
    assert ecu.state == 1
    ecu.close()
