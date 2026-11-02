"""Opt-in review policies: authenticated route arbitration and perception studies.

No truth labels, attack identifiers, keys or unverified timestamps select commands.
"""
from .perception import Observation


def select_authenticated_primary(primary,backup):
    """Use newest authenticated producer time; equal times retain native primary priority.

    Both inputs must already have passed the per-path MAC, role, age and replay checks.
    Returning None suppresses only an older primary; the verified backup remains available.
    """
    if primary is not None and backup is not None and backup.timestamp_ms>primary.timestamp_ms:
        return None
    return primary

class ConfirmationStudy:
    """Explicit study policy, not the default release decision algorithm.

    A single-source target needs >=2 distinct acquisition times over >=50 ms.
    Corroborated targets pass immediately. Persistent ghosts can still pass. Suppression
    is unavailable/uncertain rather than invented free space; native recovery adds delay.
    """
    def __init__(self,policy='temporal'):
        if policy not in ('temporal','corroborated','conservative'):raise ValueError('unknown perception study')
        self.policy=policy;self.source=None;self.first=None;self.last=None;self.count=0
    def update(self,result,radar,camera,now):
        m=result.measurement
        positives=[(name,s) for name,s,healthy in [('radar',radar,result.radar_healthy),('camera',camera,result.camera_healthy)]
                   if healthy and s is not None and s.object_present]
        if not m.sensor_ok or not m.object_present or len(positives)==2:
            self.source=None;self.first=self.last=None;self.count=0
            return m
        name,s=positives[0] if positives else (None,None)
        if self.policy=='conservative':
            # Confidence lowering can inhibit AEB; it is not a verified safe deceleration law.
            return Observation(m.ts_ms,m.object_present,m.range_m,m.range_rate_mps,False,min(m.confidence,.64))
        if name!=self.source:
            self.source=name;self.first=s.ts_ms if s is not None else now;self.last=None;self.count=0
        if s is not None and s.ts_ms!=self.last:
            self.last=s.ts_ms;self.count+=1
        if self.policy=='temporal' and self.count>=2 and self.last-self.first>=50:return m
        return Observation(now,False,0.,0.,False,0.)
