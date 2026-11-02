"""Radar sensor model for the vertical slice (single in-path object).

Measurement model:
    range_meas      = true_gap + N(0, sigma_r^2)
    range_rate_meas = true_rel_speed + N(0, sigma_rr^2)     (rel = lead - ego; <0 closing)
Sampled every period_ms, delivered latency_ms after sampling, stamped with the
SAMPLING time. Zero-order hold between deliveries. Object reported only within
max_range_m. Deterministic: numpy Generator seeded per run.

Fault injection hooks (communication/HW faults, NOT perception limitations):
    freeze_at_ms : from this time the sensor keeps re-sending its last measurement
                   with the same (old) timestamp — models frozen data (hazard H5).
Camera and fusion research models are implemented separately in perception.py;
this module preserves the baseline radar measurement model.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass
class RadarMeasurement:
    ts_ms: int
    object_present: bool
    range_m: float
    range_rate_mps: float
    sensor_ok: bool = True


class RadarModel:
    def __init__(self, rng: np.random.Generator, period_ms: int = 50, latency_ms: int = 0,
                 range_sigma_m: float = 0.10, range_rate_sigma_mps: float = 0.10,
                 max_range_m: float = 150.0, freeze_at_ms: int | None = None):
        if period_ms <= 0 or latency_ms < 0:
            raise ValueError("invalid radar timing")
        self.rng = rng
        self.period_ms, self.latency_ms = period_ms, latency_ms
        self.sr, self.srr = range_sigma_m, range_rate_sigma_mps
        self.max_range_m = max_range_m
        self.freeze_at_ms = freeze_at_ms
        self._in_flight: deque[tuple[int, RadarMeasurement]] = deque()
        self.latest: RadarMeasurement | None = None

    def update(self, now_ms: int, true_gap_m: float, true_rel_speed_mps: float) -> RadarMeasurement | None:
        frozen = self.freeze_at_ms is not None and now_ms >= self.freeze_at_ms
        if now_ms % self.period_ms == 0 and not frozen:
            present = 0.0 <= true_gap_m <= self.max_range_m
            r = true_gap_m + self.rng.normal(0.0, self.sr) if present else 0.0
            rr = true_rel_speed_mps + self.rng.normal(0.0, self.srr) if present else 0.0
            self._in_flight.append((now_ms + self.latency_ms,
                                    RadarMeasurement(now_ms, present, max(r, 0.0) if present else 0.0, rr)))
        while self._in_flight and self._in_flight[0][0] <= now_ms:
            self.latest = self._in_flight.popleft()[1]
        return self.latest
