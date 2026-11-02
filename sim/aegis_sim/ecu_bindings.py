"""ctypes bindings to the compiled C++ ECU library (libaegis_ecu).

The ECU algorithms exist ONLY in C++ (ecu/src). Python merely mirrors the C struct
layouts declared in ecu/include/aegis/aegis_types.h and verifies, at load time,
that the ABI version and every struct size match the compiled library
(SWR-001). A mismatch raises AbiMismatchError instead of silently corrupting memory.
"""
from __future__ import annotations

import ctypes as C
import os
import sys
from pathlib import Path

ABI_VERSION = 4

ADAS_STATES = ["DISABLED", "STANDBY", "MONITORING", "WARNING", "BRAKING", "DEGRADED", "FAULT"]
CAN_ID_BRAKE_REQ = 0x120
CAN_ID_ADAS_STATUS = 0x130
CAN_ID_BRAKE_STATUS = 0x220

U8x8 = C.c_uint8 * 8


class AbiMismatchError(RuntimeError):
    pass


class AdasConfig(C.Structure):
    _fields_ = [(n, C.c_double) for n in (
        "ttc_warning_s", "ttc_brake_s", "ttc_hysteresis_s", "min_closing_speed_mps", "stop_margin_m",
        "decel_gain", "min_brake_decel_mps2", "max_brake_decel_mps2", "emergency_decel_mps2",
        "min_active_speed_mps", "max_active_speed_mps", "standstill_speed_mps", "max_range_m",
        "max_abs_range_rate_mps", "max_ego_speed_mps")] + [(n, C.c_uint32) for n in (
        "stale_timeout_ms", "standstill_hold_ms", "threat_clear_ms", "degraded_to_fault_ms", "recovery_cycles")] + [("planning_decel_mps2", C.c_double)]


class AdasInput(C.Structure):
    _fields_ = [("now_ms", C.c_uint64), ("function_enabled", C.c_uint8), ("ego_speed_valid", C.c_uint8),
                ("sensor_ok", C.c_uint8), ("object_present", C.c_uint8), ("reserved0", C.c_uint8 * 4),
                ("ego_speed_mps", C.c_double), ("ego_speed_ts_ms", C.c_uint64), ("range_m", C.c_double),
                ("range_rate_mps", C.c_double), ("meas_ts_ms", C.c_uint64), ("feedback_monitor_enabled", C.c_uint8),
                ("brake_status_present", C.c_uint8), ("brake_status_dlc", C.c_uint8),
                ("brake_status_frame", U8x8), ("achieved_monitor_enabled",C.c_uint8),
                ("achieved_valid",C.c_uint8),("achieved_decel_mps2",C.c_double),("achieved_ts_ms",C.c_uint64),("security_event",C.c_uint8)]


class AdasOutput(C.Structure):
    _fields_ = [("state", C.c_uint8), ("warning_active", C.c_uint8), ("brake_request_active", C.c_uint8),
                ("function_unavailable", C.c_uint8), ("emergency", C.c_uint8), ("standstill", C.c_uint8),
                ("reserved0", C.c_uint8 * 2), ("dtc_flags", C.c_uint32), ("illegal_transition_count", C.c_uint32),
                ("ttc_s", C.c_double), ("required_decel_mps2", C.c_double), ("decel_request_mps2", C.c_double),
                ("brake_req_frame", U8x8), ("adas_status_frame", U8x8)]


class BrakeConfig(C.Structure):
    _fields_ = [("timeout_ms", C.c_uint32), ("max_counter_delta", C.c_uint32), ("max_decel_mps2", C.c_double),
                ("actuator_tau_s", C.c_double), ("active_threshold_mps2", C.c_double)]


class BrakeInput(C.Structure):
    _fields_ = [("now_ms", C.c_uint64), ("dt_s", C.c_double), ("driver_brake_mps2", C.c_double),
                ("can_id", C.c_uint32), ("frame_present", C.c_uint8), ("frame_dlc", C.c_uint8),
                ("frame", U8x8), ("reserved0", C.c_uint8 * 2),
                ("backup_present",C.c_uint8),("backup_dlc",C.c_uint8),("backup_frame",U8x8)]


class BrakeOutput(C.Structure):
    _fields_ = [("aeb_target_decel_mps2", C.c_double), ("target_decel_mps2", C.c_double),
                ("actual_decel_mps2", C.c_double), ("brake_active", C.c_uint8), ("status", C.c_uint8),
                ("last_reject_reason", C.c_uint8), ("frame_accepted", C.c_uint8), ("accepted_frames", C.c_uint32),
                ("rejected_frames", C.c_uint32), ("reserved0", C.c_uint8 * 4), ("status_frame", U8x8)]


class BodyConfig(C.Structure):
    _fields_ = [("timeout_ms", C.c_uint32), ("hazard_hold_ms", C.c_uint32)]


class BodyInput(C.Structure):
    _fields_ = [("now_ms", C.c_uint64), ("brake_status_present", C.c_uint8), ("brake_status_dlc", C.c_uint8),
                ("adas_status_present", C.c_uint8), ("adas_status_dlc", C.c_uint8),
                ("brake_status_frame", U8x8), ("adas_status_frame", U8x8), ("reserved0", C.c_uint8 * 4)]


class BodyOutput(C.Structure):
    _fields_ = [("brake_lamp", C.c_uint8), ("warning_indicator", C.c_uint8),
                ("aeb_unavailable_indicator", C.c_uint8), ("hazard_lamps", C.c_uint8),
                ("fault_brake_status_timeout", C.c_uint8), ("fault_adas_status_timeout", C.c_uint8),
                ("reserved0", C.c_uint8 * 2), ("rejected_frames", C.c_uint32)]


_STRUCTS = [AdasConfig, AdasInput, AdasOutput, BrakeConfig, BrakeInput, BrakeOutput,
            BodyConfig, BodyInput, BodyOutput]


def _candidate_paths() -> list[Path]:
    env = os.environ.get("AEGIS_ECU_LIB")
    root = Path(__file__).resolve().parents[2]
    names = ["libaegis_ecu.dylib", "libaegis_ecu.so", "aegis_ecu.dll"]
    paths = [Path(env)] if env else []
    for d in (root / "build", root / "build" / "ecu", root / "build" / "lib"):
        paths += [d / n for n in names]
    return paths


def load_library(path: str | os.PathLike | None = None) -> C.CDLL:
    paths = [Path(path)] if path else _candidate_paths()
    for p in paths:
        if p.exists():
            lib = C.CDLL(str(p))
            _declare(lib)
            verify_abi(lib)
            return lib
    raise FileNotFoundError("libaegis_ecu not found; build it first (see README). Tried: "
                            + ", ".join(str(p) for p in paths))


def _declare(lib: C.CDLL) -> None:
    P = C.POINTER
    sig = {
        "aegis_abi_version": (C.c_uint32, []),
        "aegis_struct_size": (C.c_size_t, [C.c_int]),
        "aegis_crc8_j1850": (C.c_uint8, [P(C.c_uint8), C.c_size_t]),
        "aegis_adas_default_config": (AdasConfig, []),
        "aegis_adas_config_valid": (C.c_int, [P(AdasConfig)]),
        "aegis_adas_create": (C.c_void_p, [P(AdasConfig)]),
        "aegis_adas_destroy": (None, [C.c_void_p]),
        "aegis_adas_step": (C.c_int, [C.c_void_p, P(AdasInput), P(AdasOutput)]),
        "aegis_adas_state": (C.c_uint8, [C.c_void_p]),
        "aegis_adas_request_transition": (C.c_int, [C.c_void_p, C.c_uint8]),
        "aegis_adas_transition_allowed": (C.c_int, [C.c_uint8, C.c_uint8]),
        "aegis_compute_ttc": (C.c_double, [C.c_double, C.c_double, C.c_double]),
        "aegis_compute_required_decel": (C.c_double, [C.c_double, C.c_double, C.c_double]),
        "aegis_brake_default_config": (BrakeConfig, []),
        "aegis_brake_create": (C.c_void_p, [P(BrakeConfig)]),
        "aegis_brake_destroy": (None, [C.c_void_p]),
        "aegis_brake_step": (C.c_int, [C.c_void_p, P(BrakeInput), P(BrakeOutput)]),
        "aegis_body_default_config": (BodyConfig, []),
        "aegis_body_create": (C.c_void_p, [P(BodyConfig)]),
        "aegis_body_destroy": (None, [C.c_void_p]),
        "aegis_body_step": (C.c_int, [C.c_void_p, P(BodyInput), P(BodyOutput)]),
    }
    for name, (res, args) in sig.items():
        fn = getattr(lib, name)
        fn.restype = res
        fn.argtypes = args


def verify_abi(lib: C.CDLL) -> None:
    v = lib.aegis_abi_version()
    if v != ABI_VERSION:
        raise AbiMismatchError(f"ABI version {v} != expected {ABI_VERSION}")
    for idx, st in enumerate(_STRUCTS):
        native = lib.aegis_struct_size(idx)
        if native != C.sizeof(st):
            raise AbiMismatchError(f"{st.__name__}: native size {native} != ctypes size {C.sizeof(st)}")


_LIB: C.CDLL | None = None


def lib() -> C.CDLL:
    global _LIB
    if _LIB is None:
        _LIB = load_library()
    return _LIB


def crc8(data: bytes) -> int:
    buf = (C.c_uint8 * len(data)).from_buffer_copy(data)
    return lib().aegis_crc8_j1850(buf, len(data))


class _Handle:
    _destroy = ""

    def __init__(self, handle: int):
        if not handle:
            raise MemoryError("ECU handle allocation failed")
        self._h = handle

    def close(self) -> None:
        if getattr(self, "_h", None):
            getattr(lib(), self._destroy)(self._h)
            self._h = None

    def __del__(self):
        try:
            self.close()
        except Exception:  # interpreter shutdown
            pass


class AdasEcu(_Handle):
    _destroy = "aegis_adas_destroy"

    def __init__(self, config: AdasConfig | None = None):
        self.config = config if config is not None else lib().aegis_adas_default_config()
        super().__init__(lib().aegis_adas_create(C.byref(self.config)))

    def step(self, inp: AdasInput) -> AdasOutput:
        out = AdasOutput()
        if lib().aegis_adas_step(self._h, C.byref(inp), C.byref(out)) != 0:
            raise RuntimeError("aegis_adas_step failed")
        return out

    @property
    def state(self) -> int:
        return lib().aegis_adas_state(self._h)

    def request_transition(self, to_state: int) -> bool:
        return bool(lib().aegis_adas_request_transition(self._h, to_state))


class BrakeEcu(_Handle):
    _destroy = "aegis_brake_destroy"

    def __init__(self, config: BrakeConfig | None = None):
        self.config = config if config is not None else lib().aegis_brake_default_config()
        super().__init__(lib().aegis_brake_create(C.byref(self.config)))

    def step(self, inp: BrakeInput) -> BrakeOutput:
        out = BrakeOutput()
        if lib().aegis_brake_step(self._h, C.byref(inp), C.byref(out)) != 0:
            raise RuntimeError("aegis_brake_step failed")
        return out


class BodyEcu(_Handle):
    _destroy = "aegis_body_destroy"

    def __init__(self, config: BodyConfig | None = None):
        self.config = config if config is not None else lib().aegis_body_default_config()
        super().__init__(lib().aegis_body_create(C.byref(self.config)))

    def step(self, inp: BodyInput) -> BodyOutput:
        out = BodyOutput()
        if lib().aegis_body_step(self._h, C.byref(inp), C.byref(out)) != 0:
            raise RuntimeError("aegis_body_step failed")
        return out


def frame_bytes(arr) -> bytes:
    return bytes(arr[i] for i in range(8))
