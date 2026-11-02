"""Scenario definition and YAML loading."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class LeadEvent:
    t_s: float
    accel_mps2: float  # signed; negative = braking


@dataclass
class Scenario:
    id: str
    title: str
    duration_s: float = 15.0
    dt_s: float = 0.01
    mu: float = 0.9
    ego_speed_kph: float = 50.0
    lead_speed_kph: float = 0.0
    gap0_m: float = 80.0
    lead_events: list[LeadEvent] = field(default_factory=list)
    radar: dict = field(default_factory=dict)
    camera: dict = field(default_factory=dict)
    perception: str = "radar"
    backup_enabled: bool = False
    network_delay_ms: int = 0
    network_duplicate: bool = False
    imu_monitor: bool = False
    radar_bias_m: float = 0.0
    radar_false_positive: bool = False
    target_present: bool = True
    faults: list[dict] = field(default_factory=list)
    expected: dict = field(default_factory=dict)
    requirement_links: list[str] = field(default_factory=list)
    description: str = ""

    @staticmethod
    def from_dict(d: dict) -> "Scenario":
        return Scenario(
            id=d["id"], title=d["title"], description=d.get("description", ""),
            duration_s=float(d.get("duration_s", 15.0)), dt_s=float(d.get("dt_s", 0.01)),
            mu=float(d.get("road", {}).get("mu", 0.9)),
            ego_speed_kph=float(d["ego"]["initial_speed_kph"]),
            lead_speed_kph=float(d["lead"]["initial_speed_kph"]),
            gap0_m=float(d["lead"]["gap0_m"]),
            lead_events=[LeadEvent(float(e["t_s"]), float(e["accel_mps2"])) for e in d["lead"].get("events", [])],
            target_present=bool(d.get("target_present",True)),
            camera=dict(d.get("camera", {})), perception=d.get("perception", "radar"),
            backup_enabled=bool(d.get("backup_enabled",False)),
            network_delay_ms=int(d.get("network_delay_ms",0)), network_duplicate=bool(d.get("network_duplicate",False)),
            imu_monitor=bool(d.get("imu_monitor",False)), radar_bias_m=float(d.get("radar_bias_m",0)),
            radar_false_positive=bool(d.get("radar_false_positive",False)),
            radar=dict(d.get("radar", {})), faults=list(d.get("faults", [])),
            expected=dict(d.get("expected", {})), requirement_links=list(d.get("requirement_links", [])),
        )


def load_scenario(path: str | Path) -> Scenario:
    with open(path, encoding="utf-8") as fh:
        return Scenario.from_dict(yaml.safe_load(fh))


def load_all(directory: str | Path) -> list[Scenario]:
    return [load_scenario(p) for p in sorted(Path(directory).glob("*.yaml"))]
