"""Single-target camera and fusion research models, not qualified perception.

No truth enters fusion. It aligns delayed ranges using measured range-rate only.
Camera and radar share scene truth; independent RNGs do not establish physical independence.
"""
from collections import deque
from dataclasses import dataclass
import math
from .sensors import RadarMeasurement

@dataclass
class Observation:
    ts_ms: int
    object_present: bool
    range_m: float
    range_rate_mps: float
    sensor_ok: bool = True
    confidence: float = .9

class CameraModel:
    def __init__(self, rng, period_ms=50, latency_ms=80, range_sigma_m=.4,
                 rate_sigma_mps=.2, detection_probability=.98, max_range_m=120.,
                 half_fov_deg=30., confidence=.85, unavailable_at_ms=None,
                 freeze_at_ms=None, visibility=1., occlusion=0., bias_m=0.,
                 false_positive=False, lateral_offset_m=0.):
        vals=(range_sigma_m,rate_sigma_mps,detection_probability,max_range_m,half_fov_deg,confidence,visibility,occlusion,bias_m,lateral_offset_m)
        if (not all(math.isfinite(x) for x in vals) or period_ms<=0 or latency_ms<0 or
            min(range_sigma_m,rate_sigma_mps)<0 or not 0<=detection_probability<=1 or
            not 0<=visibility<=1 or not 0<=occlusion<=1 or not 0<=confidence<=1 or
            max_range_m<=0 or not 0<half_fov_deg<90): raise ValueError('invalid camera configuration')
        self.rng=rng; self.period=period_ms; self.latency=latency_ms
        self.sr=range_sigma_m; self.srr=rate_sigma_mps; self.p=detection_probability
        self.range=max_range_m; self.fov=half_fov_deg; self.conf=confidence
        self.unavailable=unavailable_at_ms; self.freeze=freeze_at_ms
        self.visibility=visibility; self.occlusion=occlusion; self.bias=bias_m
        self.ghost=false_positive; self.lateral=lateral_offset_m
        self.pending=deque(); self.latest=None

    def update(self, now, gap, rel_speed):
        if self.unavailable is not None and now>=self.unavailable:
            return Observation(now,False,0,0,False,0)
        if self.freeze is None or now<self.freeze:
            if now%self.period==0:
                in_view=(0<=gap<=self.range and abs(math.degrees(math.atan2(self.lateral,max(gap,1e-9))))<=self.fov)
                probability=self.p*self.visibility*(1-self.occlusion)
                present=(in_view and self.rng.random()<probability) or self.ghost
                r=(12. if self.ghost else max(0.,gap+self.bias+self.rng.normal(0,self.sr))) if present else 0.
                rr=(-15. if self.ghost else rel_speed+self.rng.normal(0,self.srr)) if present else 0.
                # Confidence is an assumed scene-quality score, not a calibrated posterior.
                conf=self.conf*self.visibility*(1-self.occlusion)
                self.pending.append((now+self.latency,Observation(now,present,r,rr,True,conf)))
        while self.pending and self.pending[0][0]<=now:self.latest=self.pending.popleft()[1]
        return self.latest

@dataclass
class FusionResult:
    measurement: Observation
    mode: str
    radar_healthy: bool
    camera_healthy: bool
    disagreement: bool=False

class Fusion:
    def __init__(self, max_age_ms=150, min_confidence=.65, range_gate_m=3., rate_gate_mps=2.):
        self.age=max_age_ms; self.conf=min_confidence; self.rgate=range_gate_m; self.vgate=rate_gate_mps
    def valid(self,m,now):
        return (m is not None and m.sensor_ok and 0<=now-m.ts_ms<=self.age and
                all(math.isfinite(x) for x in (m.range_m,m.range_rate_mps,getattr(m,'confidence',.9))) and
                getattr(m,'confidence',.9)>=self.conf and
                (not m.object_present or (0<=m.range_m<=200 and abs(m.range_rate_mps)<=80)))
    def align(self,m,now):
        return Observation(now,m.object_present,max(0.,m.range_m+m.range_rate_mps*(now-m.ts_ms)/1000),
                           m.range_rate_mps,True,getattr(m,'confidence',.9))
    def update(self,now,radar,camera):
        rh,ch=self.valid(radar,now),self.valid(camera,now)
        unavailable=Observation(now,False,0,0,False,0)
        if not rh and not ch:return FusionResult(unavailable,'UNAVAILABLE',rh,ch)
        if rh and not ch:return FusionResult(self.align(radar,now),'RADAR_ONLY',rh,ch)
        if ch and not rh:return FusionResult(self.align(camera,now),'CAMERA_ONLY',rh,ch)
        r,c=self.align(radar,now),self.align(camera,now)
        if r.object_present and c.object_present:
            if abs(r.range_m-c.range_m)>self.rgate or abs(r.range_rate_mps-c.range_rate_mps)>self.vgate:
                return FusionResult(unavailable,'DISAGREEMENT',rh,ch,True)
            weight=r.confidence/(r.confidence+c.confidence)
            m=Observation(now,True,weight*r.range_m+(1-weight)*c.range_m,
                          weight*r.range_rate_mps+(1-weight)*c.range_rate_mps,True,min(r.confidence,c.confidence))
            return FusionResult(m,'COMBINED',rh,ch)
        # A nondetection is not independently established free-space evidence.
        return FusionResult(r if r.object_present else c,'COMBINED',rh,ch)
