"""Deterministic longitudinal point-mass vehicle model.

Equations (per step of length dt, constant acceleration a within the step):
    if v + a*dt >= 0:  x' = x + v*dt + a*dt^2/2,   v' = v + a*dt
    else (stops inside the step, t_s = -v/a):  x' = x + v*t_s + a*t_s^2/2,  v' = 0
Braking deceleration is limited by tyre-road friction:  |a_brake| <= mu * g.
No reversing, aerodynamic drag, rolling resistance, grade, load transfer or tyre
dynamics are modelled (see docs/04_assumptions_limitations.md, LIM-VEH-*).
"""
from __future__ import annotations

from dataclasses import dataclass

G_MPS2 = 9.81


@dataclass
class Vehicle:
    x_m: float
    v_mps: float
    a_mps2: float = 0.0

    def step(self, dt_s: float, accel_mps2: float) -> None:
        if dt_s <= 0:
            raise ValueError("dt must be positive")
        v, a = self.v_mps, accel_mps2
        if v + a * dt_s >= 0.0:
            self.x_m += v * dt_s + 0.5 * a * dt_s * dt_s
            self.v_mps = v + a * dt_s
        else:
            t_s = -v / a
            self.x_m += v * t_s + 0.5 * a * t_s * t_s
            self.v_mps = 0.0
        self.a_mps2 = a


def friction_limited_decel(requested_decel_mps2: float, mu: float) -> float:
    """Achievable deceleration magnitude for a requested magnitude on friction mu."""
    return min(max(requested_decel_mps2, 0.0), mu * G_MPS2)


@dataclass
class InattentiveDriver:
    """Driver model used in AEB testing: holds a set speed, never brakes on their own.

    Assumption DRV-A-01: the driver does not react to the hazard or the FCW warning.
    Assumption DRV-A-02: after AEB has brought the vehicle to standstill, the driver
    takes over and keeps the vehicle stationary (target speed becomes 0).
    """
    target_speed_mps: float
    gain_per_s: float = 0.5
    max_accel_mps2: float = 2.0
    max_decel_mps2: float = 3.0

    def accel(self, v_mps: float) -> float:
        a = self.gain_per_s * (self.target_speed_mps - v_mps)
        return max(-self.max_decel_mps2, min(self.max_accel_mps2, a))


def pair_step(ego: Vehicle, lead: Vehicle, dt_s: float, ego_a: float, lead_a: float):
    """Advance to first contact or horizon, returning (contact_offset_s, min_gap).

    Split at each stop time. On each segment separation is a quadratic; check
    its stationary point and solve first zero by bisection on the decreasing arc.
    No penetration is integrated beyond first contact.
    """
    cuts = {0.0, dt_s}
    for car, a in ((ego, ego_a), (lead, lead_a)):
        if a < 0 and 0 < -car.v_mps / a < dt_s:
            cuts.add(-car.v_mps / a)
    cuts = sorted(cuts)
    minimum = lead.x_m - ego.x_m
    if minimum <= 0:
        return 0.0, minimum
    for start, end in zip(cuts, cuts[1:]):
        h = end - start
        ae = ego_a if ego.v_mps > 0 or ego_a > 0 else 0.0
        al = lead_a if lead.v_mps > 0 or lead_a > 0 else 0.0
        gap, rv, ra = lead.x_m-ego.x_m, lead.v_mps-ego.v_mps, al-ae
        def separation(t): return gap + rv*t + .5*ra*t*t
        candidates = [h]
        if ra != 0 and 0 < -rv/ra < h: candidates.append(-rv/ra)
        t_min = min(candidates, key=separation)
        minimum = min(minimum, separation(t_min))
        if minimum <= 0:
            lo, hi = 0.0, t_min
            for _ in range(60):
                mid = (lo+hi)/2
                if separation(mid) > 0: lo = mid
                else: hi = mid
            ego.step(hi, ae); lead.step(hi, al)
            return start+hi, 0.0
        ego.step(h, ae); lead.step(h, al)
    return None, minimum
