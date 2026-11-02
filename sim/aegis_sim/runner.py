"""Closed-loop SiL runner: vehicles + radar + ADAS/Brake/Body ECUs (real C++) + virtual CAN.

Step order at simulation time t_k (dt = 10 ms):
  1. bus.advance()            frames sent at t_{k-1} become receivable (1-cycle latency)
  2. radar.update()           new sample every period_ms (timestamp = sampling time)
  3. ADAS ECU step            -> BRAKE_REQ (0x120) + ADAS_STATUS (0x130) sent
  4. Brake ECU step           consumes BRAKE_REQ received this step -> BRAKE_STATUS (0x220) sent
  5. Body ECU step            consumes BRAKE_STATUS / ADAS_STATUS received this step
  6. vehicle integration      ego decel = friction-limited Brake ECU actuator output
"""
from __future__ import annotations

import csv
import math
import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

import numpy as np

from . import ecu_bindings as eb
from .can_bus import CanFrame, InProcessCanBus
from .scenario import Scenario
from .sensors import RadarModel
from .perception import CameraModel, Fusion, Observation
from .transport import ScheduledBus
from .vehicle import InattentiveDriver, Vehicle, friction_limited_decel, pair_step

KPH = 1.0 / 3.6


@dataclass
class RunResult:
    scenario_id: str
    seed: int
    collision: bool = False
    collision_time_s: float | None = None
    impact_speed_mps: float = 0.0
    min_gap_m: float = math.inf
    first_warning_s: float | None = None
    first_brake_request_s: float | None = None
    ttc_at_brake_request_s: float | None = None
    first_brake_active_s: float | None = None
    first_brake_lamp_s: float | None = None
    brake_lamp_latency_ms: float | None = None
    max_actual_decel_mps2: float = 0.0
    max_requested_decel_mps2: float = 0.0
    final_ego_speed_mps: float = 0.0
    final_adas_state: str = ""
    states_visited: list[str] = field(default_factory=list)
    dtc_flags_union: int = 0
    first_degraded_s: float | None = None
    brake_rejected_frames: int = 0
    body_rejected_frames: int = 0
    hazard_activated: bool = False
    illegal_transitions: int = 0
    brake_timeout_seen: bool = False
    first_brake_timeout_s: float | None = None
    last_brake_req_delivered_s: float | None = None
    unavailable_indicated: bool = False
    adas_step_mean_us: float = 0.0
    adas_step_max_us: float = 0.0
    first_feedback_fault_s: float | None = None
    perception_modes: list[str] = field(default_factory=list)
    first_sensor_loss_s: float | None = None
    first_achieved_brake_s: float | None = None
    first_achieved_fault_s: float | None = None
    unavailable_duration_s: float = 0.0
    missed_detection_cycles: int = 0
    false_intervention: bool = False
    backup_received_cycles: int = 0
    disagreement_cycles: int = 0
    degraded_perception_cycles: int = 0
    adas_cpu_mean_us: float = 0.0
    adas_cpu_max_us: float = 0.0
    authenticated_backup_preferred_cycles: int = 0
    confirmation_suppressed_cycles: int = 0
    unnecessary_braking: bool = False
    first_security_dtc_s: float | None = None
    security_stats: dict = field(default_factory=dict)
    steps: int = 0

    def to_dict(self) -> dict:
        d = asdict(self)
        return {k: (None if isinstance(v, float) and math.isinf(v) else v) for k, v in d.items()}


def lead_accel(sc: Scenario, t_s: float) -> float:
    a = 0.0
    for e in sc.lead_events:
        if t_s >= e.t_s:
            a = e.accel_mps2
    return a


def run_scenario(sc: Scenario, seed: int = 0, trace_path: str | Path | None = None,
                 bus: InProcessCanBus | None = None, security: dict | None = None,
                 assurance: dict | None = None, event_sink=None) -> RunResult:
    """Run one scenario. A pre-configured bus (e.g. with a tamper hook) may be supplied."""
    assurance=assurance or {}
    if assurance.get('prefer_latest_authenticated') and (security is None or security.get('mode')=='A'):
        raise ValueError('authenticated route arbitration requires B/C verification')
    confirmation=None
    if assurance.get('perception_study'):
        from .assurance import ConfirmationStudy
        confirmation=ConfirmationStudy(assurance['perception_study'])
    dt_ms = int(round(sc.dt_s * 1000))
    if dt_ms <= 0 or abs(dt_ms / 1000.0 - sc.dt_s) > 1e-12:
        raise ValueError("dt_s must be a whole number of milliseconds")
    if (not math.isfinite(sc.mu) or not 0<=sc.mu<=1.5 or sc.duration_s<=0 or
        sc.perception not in ('radar','camera','combined') or
        not all(math.isfinite(x) and x>=0 for x in (sc.ego_speed_kph,sc.lead_speed_kph,sc.gap0_m))):
        raise ValueError('invalid scenario physics/configuration')
    def fault(kind,t):
        return any(f['type']==kind and t>=f['t_s'] and t<f.get('until_s',math.inf) for f in sc.faults)
    rng = np.random.default_rng(seed)
    freeze = next((int(f["t_s"] * 1000) for f in sc.faults if f["type"] == "radar_freeze"), None)
    radar = RadarModel(rng, freeze_at_ms=freeze, **sc.radar)
    cam_config=dict(sc.camera)
    cf=next((int(f['t_s']*1000) for f in sc.faults if f['type']=='camera_freeze'),None)
    if cf is not None: cam_config['freeze_at_ms']=cf
    camera=CameraModel(np.random.default_rng(np.random.SeedSequence([seed,1])),**cam_config)
    fusion=Fusion()
    bus = bus or ScheduledBus(sc.network_delay_ms,sc.network_duplicate)
    backup=ScheduledBus(20) if sc.backup_enabled else None
    drop_from = next((int(f["t_s"] * 1000) for f in sc.faults if f["type"] == "drop_brake_req"), None)
    original_filter=bus.drop_filter
    def drops(fr):
        t=fr.timestamp_ms/1000
        return ((original_filter is not None and original_filter(fr)) or
            (fr.arbitration_id==eb.CAN_ID_BRAKE_REQ and
             (fault('drop_brake_req',t) or fault('both_channels_lost',t) or (fault('intermittent_req',t) and int(t*1000)%200<80))) or
            (fr.arbitration_id==eb.CAN_ID_BRAKE_STATUS and fault('drop_feedback',t)))
    bus.drop_filter=drops
    if backup is not None:
        backup.drop_filter=lambda fr:fault('both_channels_lost',fr.timestamp_ms/1000) or fault('backup_lost',fr.timestamp_ms/1000)

    security_context=None
    if security is not None:
        from .security_gateway import SecurityContext,SecureBus,CapacityBus
        security_context=SecurityContext(security)
        primary=CapacityBus(sc.network_delay_ms,sc.network_duplicate)
        primary.drop_filter=bus.drop_filter
        bus=SecureBus(primary,security_context,'primary')
        if backup is not None:
            secondary=CapacityBus(20)
            secondary.drop_filter=backup.drop_filter
            backup=SecureBus(secondary,security_context,'backup')
    study_config=None
    if assurance.get('brake_cap_mps2') is not None:
        cap=float(assurance['brake_cap_mps2'])
        if not math.isfinite(cap) or not 0<cap<=9:raise ValueError('invalid study brake cap')
        study_config=eb.lib().aegis_adas_default_config()
        study_config.max_brake_decel_mps2=cap
        study_config.min_brake_decel_mps2=min(study_config.min_brake_decel_mps2,cap)
        study_config.emergency_decel_mps2=min(study_config.emergency_decel_mps2,cap)
        study_config.planning_decel_mps2=min(study_config.planning_decel_mps2,cap)
    adas, brake, body = eb.AdasEcu(study_config), eb.BrakeEcu(), eb.BodyEcu()
    ego = Vehicle(0.0, sc.ego_speed_kph * KPH)
    lead = Vehicle(sc.gap0_m, sc.lead_speed_kph * KPH)
    driver = InattentiveDriver(target_speed_mps=ego.v_mps)
    res = RunResult(sc.id, seed)
    rows = []
    step_times = []
    n_steps = int(round(sc.duration_s / sc.dt_s))
    if abs(n_steps*sc.dt_s-sc.duration_s)>1e-9:
        raise ValueError("duration_s must be a whole number of simulation steps")
    aeb_engaged = False
    cpu_times=[]
    achieved=0.0

    for k in range(n_steps + 1):
        t_ms = k * dt_ms
        t_s = t_ms / 1000.0
        if isinstance(bus,ScheduledBus): bus.advance(t_ms)
        else: bus.advance()
        if backup is not None: backup.advance(t_ms)
        gap = lead.x_m - ego.x_m
        rel_v = lead.v_mps - ego.v_mps
        sensor_gap=gap if sc.target_present else math.inf
        rm = radar.update(t_ms, sensor_gap, rel_v)
        cm = camera.update(t_ms, sensor_gap, rel_v)
        if rm is not None:
            rm=replace(rm,range_m=rm.range_m+sc.radar_bias_m if rm.object_present else 0.)
            if sc.radar_false_positive: rm=replace(rm,object_present=True,range_m=12.,range_rate_mps=-15.)
        if fault('radar_ghost',t_s) and rm is not None:
            rm=replace(rm,object_present=True,range_m=12.,range_rate_mps=-15.)
        if fault('radar_unavailable',t_s) or fault('both_unavailable',t_s): rm=None
        if fault('camera_unavailable',t_s) or fault('both_unavailable',t_s): cm=None
        if fault('correlated_bias',t_s):
            if rm is not None: rm=replace(rm,range_m=rm.range_m+30.)
            if cm is not None: cm=replace(cm,range_m=cm.range_m+30.)
        if security_context is not None:
            rm=security_context.sensor(rm,'radar',t_ms)
            cm=security_context.sensor(cm,'camera',t_ms)
        if sc.perception=='radar':
            m=rm; mode='RADAR_ONLY' if fusion.valid(m,t_ms) else 'UNAVAILABLE'
            rh,ch=fusion.valid(rm,t_ms),False
            disagree=False
        else:
            fused=fusion.update(t_ms,rm if sc.perception=='combined' else None,cm)
            m=fused.measurement;mode=fused.mode;rh,ch=fused.radar_healthy,fused.camera_healthy
            disagree=fused.disagreement
        if confirmation is not None and sc.perception!='radar':
            filtered=confirmation.update(fused,rm,cm,t_ms)
            if m.sensor_ok and m.object_present and (not filtered.sensor_ok or filtered.confidence<.65):
                res.confirmation_suppressed_cycles+=1;mode='CONFIRMING'
            m=filtered
        if not res.perception_modes or res.perception_modes[-1]!=mode: res.perception_modes.append(mode)
        if mode in ('CAMERA_ONLY','RADAR_ONLY') and sc.perception=='combined' and t_ms>150:res.degraded_perception_cycles+=1
        if disagree:res.disagreement_cycles+=1
        if ((sc.perception=='combined' and not (rh and ch)) or mode=='UNAVAILABLE') and t_ms>150:
            if res.first_sensor_loss_s is None:res.first_sensor_loss_s=t_s
        if sc.target_present and 0<=gap<=120 and (mode in ('UNAVAILABLE','DISAGREEMENT') or m is None or not m.sensor_ok or not m.object_present):
            res.missed_detection_cycles+=1

        ai = eb.AdasInput()
        ai.now_ms, ai.function_enabled = t_ms, 1
        ai.ego_speed_valid, ai.ego_speed_mps, ai.ego_speed_ts_ms = 1, ego.v_mps, t_ms
        if m is not None:
            ai.sensor_ok, ai.object_present = int(m.sensor_ok), int(m.object_present)
            ai.range_m, ai.range_rate_mps, ai.meas_ts_ms = m.range_m, m.range_rate_mps, m.ts_ms
        else:
            ai.sensor_ok = 0
        ai.feedback_monitor_enabled = 1
        feedback = bus.receive(eb.CAN_ID_BRAKE_STATUS,receiver=1) if security_context is not None else bus.receive(eb.CAN_ID_BRAKE_STATUS)
        if feedback is not None:
            ai.brake_status_present, ai.brake_status_dlc = 1, len(feedback.data)
            for i, b in enumerate(feedback.data[:8]):
                ai.brake_status_frame[i] = b
        ai.achieved_monitor_enabled=int(sc.imu_monitor)
        ai.achieved_valid=1
        ai.achieved_decel_mps2=achieved
        ai.achieved_ts_ms=max(0,t_ms-dt_ms)
        ai.security_event=int(security_context is not None and security_context.mode!='A' and
                              security_context.first_event_s is not None)
        cpu0=time.process_time_ns()
        t0 = time.perf_counter_ns()
        ao = adas.step(ai)
        cpu_times.append((time.process_time_ns()-cpu0)/1000.)
        step_times.append((time.perf_counter_ns() - t0) / 1000.0)
        command=CanFrame(eb.CAN_ID_BRAKE_REQ, eb.frame_bytes(ao.brake_req_frame), t_ms, "ADAS")
        bus.send(command)
        if backup is not None:backup.send(command)
        bus.send(CanFrame(eb.CAN_ID_ADAS_STATUS, eb.frame_bytes(ao.adas_status_frame), t_ms, "ADAS"))

        bi = eb.BrakeInput()
        bi.now_ms, bi.dt_s, bi.driver_brake_mps2 = t_ms, sc.dt_s, 0.0
        rf = bus.receive(eb.CAN_ID_BRAKE_REQ)
        if backup is not None:
            bf=backup.receive(eb.CAN_ID_BRAKE_REQ)
            if bf is not None:
                res.backup_received_cycles+=1
                bi.backup_present,bi.backup_dlc=1,len(bf.data)
                for i,b in enumerate(bf.data[:8]):bi.backup_frame[i]=b
        if assurance.get('prefer_latest_authenticated') and backup is not None:
            from .assurance import select_authenticated_primary
            chosen=select_authenticated_primary(rf,bf)
            if rf is not None and chosen is None:res.authenticated_backup_preferred_cycles+=1
            rf=chosen
        if rf is not None:
            bi.frame_present, bi.can_id, bi.frame_dlc = 1, rf.arbitration_id, len(rf.data)
            for i,b in enumerate(rf.data[:8]):bi.frame[i]=b
        software_failed=fault('brake_software_failure',t_s)
        if not software_failed or k==0:bo=brake.step(bi)
        if security_context is not None and backup is None and bi.frame_present and security_context.command_attack_delivery.get('primary')==(t_ms,True):
            security_context.counts['native_attack_offered_primary_only']+=1
            if bo.frame_accepted:security_context.counts['native_attack_accepted_primary_only']+=1
        if not software_failed:
            bus.send(CanFrame(eb.CAN_ID_BRAKE_STATUS, eb.frame_bytes(bo.status_frame), t_ms, "BRAKE"))

        yi = eb.BodyInput()
        yi.now_ms = t_ms
        bsf = bus.receive(eb.CAN_ID_BRAKE_STATUS)
        asf = bus.receive(eb.CAN_ID_ADAS_STATUS)
        if bsf is not None:
            yi.brake_status_present, yi.brake_status_dlc = 1, len(bsf.data)
            for i, b in enumerate(bsf.data[:8]):
                yi.brake_status_frame[i] = b
        if asf is not None:
            yi.adas_status_present, yi.adas_status_dlc = 1, len(asf.data)
            for i, b in enumerate(asf.data[:8]):
                yi.adas_status_frame[i] = b
        yo = body.step(yi)

        state = eb.ADAS_STATES[ao.state]
        if not res.states_visited or res.states_visited[-1] != state:
            res.states_visited.append(state)
        if ao.function_unavailable and k<n_steps:res.unavailable_duration_s+=sc.dt_s
        if ao.dtc_flags & (1<<9) and res.first_achieved_fault_s is None:res.first_achieved_fault_s=t_s
        if ao.dtc_flags & (1<<10) and res.first_security_dtc_s is None:res.first_security_dtc_s=t_s
        res.dtc_flags_union |= ao.dtc_flags
        if ao.dtc_flags & (1 << 8) and res.first_feedback_fault_s is None:
            res.first_feedback_fault_s = t_s
        if ao.warning_active and res.first_warning_s is None:
            res.first_warning_s = t_s
        if ao.brake_request_active:
            aeb_engaged = True
            if res.first_brake_request_s is None:
                res.first_brake_request_s = t_s
                res.ttc_at_brake_request_s = ao.ttc_s if math.isfinite(ao.ttc_s) else None
        if state == "DEGRADED" and res.first_degraded_s is None:
            res.first_degraded_s = t_s
        if bo.brake_active and res.first_brake_active_s is None:
            res.first_brake_active_s = t_s
        if yo.brake_lamp and res.first_brake_lamp_s is None:
            res.first_brake_lamp_s = t_s
        res.hazard_activated |= bool(yo.hazard_lamps)
        res.illegal_transitions = ao.illegal_transition_count
        if bo.status == 2 and res.first_brake_timeout_s is None:
            res.first_brake_timeout_s = t_s
        res.brake_timeout_seen |= bo.status == 2
        if rf is not None:
            res.last_brake_req_delivered_s = t_s
        res.unavailable_indicated |= bool(yo.aeb_unavailable_indicator) and t_ms > 100
        res.max_requested_decel_mps2 = max(res.max_requested_decel_mps2, ao.decel_request_mps2)

        # ---- plant ----
        brake_decel = friction_limited_decel(bo.actual_decel_mps2, sc.mu)
        if software_failed or fault('actuator_failure',t_s):brake_decel=0.
        if brake_decel>=.3 and res.first_achieved_brake_s is None:res.first_achieved_brake_s=t_s
        if aeb_engaged and ego.v_mps <= 0.05:
            driver.target_speed_mps = 0.0  # DRV-A-02
        ego_a = -brake_decel if bo.actual_decel_mps2 > 0.01 else driver.accel(ego.v_mps)
        achieved=max(-ego_a,0.)
        lead_a = lead_accel(sc, t_s)
        if lead_a < 0:
            lead_a = -friction_limited_decel(-lead_a, sc.mu)
        res.max_actual_decel_mps2 = max(res.max_actual_decel_mps2, max(-ego_a, 0.0))

        rows.append({
            "t_s": t_s, "ego_x_m": ego.x_m, "lead_x_m": lead.x_m, "gap_m": gap, "ego_v_mps": ego.v_mps,
            "lead_v_mps": lead.v_mps, "meas_range_m": ai.range_m, "meas_range_rate_mps": ai.range_rate_mps,
            "meas_age_ms": t_ms - ai.meas_ts_ms if ai.sensor_ok else -1, "ttc_s": ao.ttc_s if math.isfinite(ao.ttc_s) else "",
            "adas_state": state, "decel_request_mps2": ao.decel_request_mps2,
            "brake_target_mps2": bo.target_decel_mps2, "brake_actual_mps2": bo.actual_decel_mps2,
            "ego_accel_mps2": ego_a, "brake_status": bo.status, "brake_lamp": yo.brake_lamp,
            "warning": yo.warning_indicator, "hazard": yo.hazard_lamps, "unavailable": yo.aeb_unavailable_indicator,
            "dtc_flags": ao.dtc_flags, "perception_mode":mode,
            "radar_healthy":rh,"camera_healthy":ch,"achieved_decel_mps2":achieved,
            "backup_enabled":int(backup is not None),
        })
        if event_sink is not None:
            event_sink(dict(rows[-1],request_active=bool(ao.brake_request_active),
                request_delivered=rf is not None,request_issued_ms=rf.timestamp_ms if rf is not None else None,
                backup_present=bool(bi.backup_present),brake_frame_accepted=bool(bo.frame_accepted),
                brake_aeb_target=bo.aeb_target_decel_mps2,
                security_events=[e for e in security_context.events if e['now_ms']==t_ms] if security_context else []))
        res.min_gap_m = min(res.min_gap_m, gap)
        if gap <= 0.0:
            res.collision, res.collision_time_s = True, t_s
            res.impact_speed_mps = max(ego.v_mps - lead.v_mps, 0.0)
            break
        if k == n_steps: break  # report the horizon without integrating beyond it
        contact, step_gap = pair_step(ego, lead, sc.dt_s, ego_a, lead_a)
        res.min_gap_m = min(res.min_gap_m, step_gap)
        if contact is not None:
            if ao.function_unavailable:res.unavailable_duration_s-=sc.dt_s-contact
            res.collision, res.collision_time_s = True, t_s + contact
            res.impact_speed_mps = max(ego.v_mps - lead.v_mps, 0.0)
            break

    res.steps = len(rows)
    res.final_ego_speed_mps = ego.v_mps
    res.final_adas_state = eb.ADAS_STATES[adas.state]
    res.brake_rejected_frames = bo.rejected_frames
    res.body_rejected_frames = yo.rejected_frames
    if res.first_brake_active_s is not None and res.first_brake_lamp_s is not None:
        res.brake_lamp_latency_ms = round((res.first_brake_lamp_s - res.first_brake_active_s) * 1000.0, 3)
    res.unnecessary_braking=bool(not sc.target_present and res.first_achieved_brake_s is not None)
    res.false_intervention=bool(not sc.target_present and res.first_brake_request_s is not None)
    if cpu_times:
        res.adas_cpu_mean_us=float(np.mean(cpu_times));res.adas_cpu_max_us=float(max(cpu_times))
    if step_times:
        res.adas_step_mean_us = float(np.mean(step_times))
        res.adas_step_max_us = float(np.max(step_times))
    if trace_path is not None:
        Path(trace_path).parent.mkdir(parents=True, exist_ok=True)
        with open(trace_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    if security_context is not None:
        res.security_stats=security_context.summary()
        res.security_stats['brake_ecu_accepted_frames']=bo.accepted_frames
        res.security_stats['brake_ecu_rejected_frames']=bo.rejected_frames
        res.security_stats['primary_queue_drops']=bus.bus.queue_drops
        res.security_stats['primary_max_backlog']=bus.bus.max_backlog
        res.security_stats['backup_queue_drops']=backup.bus.queue_drops if backup is not None else 0
    for h in (adas, brake, body):
        h.close()
    return res
