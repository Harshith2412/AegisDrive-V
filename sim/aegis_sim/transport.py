"""Scheduled transport: delays/duplicates are delivered causally on a stepped clock."""
from .can_bus import InProcessCanBus
class ScheduledBus(InProcessCanBus):
    def __init__(self, delay_ms=0, duplicate=False):
        super().__init__(); self.delay_ms=delay_ms; self.duplicate=duplicate; self.queued=[];self.now_ms=0
        if delay_ms<0:raise ValueError('negative delay')
    def send(self,frame):
        self.log.append(frame)
        if self.drop_filter and self.drop_filter(frame):return
        self.queued.append((frame.timestamp_ms+self.delay_ms,frame))
        if self.duplicate:self.queued.append((frame.timestamp_ms+self.delay_ms+10,frame))
    def advance(self,now_ms=None):
        self.now_ms=self.now_ms+10 if now_ms is None else now_ms
        # At least one simulation step. Frames generated at now cannot arrive now.
        self._deliverable=[f for due,f in self.queued if due<=self.now_ms and f.timestamp_ms<self.now_ms]
        self.queued=[(due,f) for due,f in self.queued if due>self.now_ms or f.timestamp_ms>=self.now_ms]
    def receive(self,identifier):
        frames=[f for f in self._deliverable if f.arbitration_id==identifier]
        return max(frames,key=lambda f:f.timestamp_ms) if frames else None
