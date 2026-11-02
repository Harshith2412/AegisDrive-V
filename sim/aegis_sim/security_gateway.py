"""Local SiL security adapters and isolated attack injector; no real network I/O."""
from collections import Counter,deque
from dataclasses import replace
from .can_bus import CanFrame
from .transport import ScheduledBus
from .security import *
from . import ecu_bindings as eb

class CapacityBus(ScheduledBus):
    """Bounded queue, arbitration-ID priority and fixed frames/step budget.

    Abstract scheduling only: not a CAN bit-level or CAN FD airtime simulator.
    """
    def __init__(self,delay_ms=0,duplicate=False,capacity=64,budget=4):
        super().__init__(delay_ms,duplicate);self.capacity=capacity;self.budget=budget
        self.queue_drops=0;self.max_backlog=0
    def send(self,frame):
        if len(self.queued)>=self.capacity:self.queue_drops+=1;return
        super().send(frame)
        self.max_backlog=max(self.max_backlog,len(self.queued))
    def advance(self,now_ms=None):
        self.now_ms=self.now_ms+10 if now_ms is None else now_ms
        ready=sorted([(i,due,f) for i,(due,f) in enumerate(self.queued)
                      if due<=self.now_ms and f.timestamp_ms<self.now_ms],key=lambda x:(x[2].arbitration_id,x[0]))
        selected={x[0] for x in ready[:self.budget]}
        self._deliverable=[f for i,_,f in ready if i in selected]
        self.queued=[x for i,x in enumerate(self.queued) if i not in selected]


def evil_command(payload):
    d=bytearray(payload);d[2]=3;d[3:5]=(900).to_bytes(2,'little')
    d[0]=eb.crc8(bytes([0x20,0x01])+bytes(d[1:8]))
    return bytes(d)

class SecurityContext:
    def __init__(self,config):
        self.config=config;self.mode=config.get('mode','B')
        if self.mode not in ('A','B','C'):raise ValueError('security mode A/B/C')
        self.attack=config.get('attack');self.start=int(config.get('start_s',2)*1000)
        self.end=int(config.get('end_s',1000)*1000)
        self.paths=config.get('paths',['primary'])
        self.counts=Counter();self.events=deque(maxlen=128);self.verifiers={};self.command_attack_delivery={};self.sensor_tx=Sender('sensor')
        self.first_event_s=None;self.tx_cpu_count=0;self.tx_cpu_total_ns=0
    def active(self,now):return self.start<=now<self.end
    def event(self,reason,now):
        self.events.append(dict(reason=reason,now_ms=now));self.counts[reason]+=1
        if self.first_event_s is None:self.first_event_s=now/1000
    def verifier(self,receiver,channel):
        key=(receiver,channel)
        if key not in self.verifiers:self.verifiers[key]=Verifier(receiver,channel,'B' if self.mode=='A' else self.mode)
        return self.verifiers[key]
    def sensor(self,m,which,now):
        if m is None:return None
        t0=time.process_time_ns();mid=RADAR_ID if which=='radar' else CAMERA_ID
        src=RADAR if which=='radar' else CAMERA
        active=self.active(now) and which==self.config.get('sensor_target','radar')
        attack=active and self.attack in ('A01','A11')
        if attack:
            m=replace(m,object_present=True,range_m=12. if self.attack=='A01' else 500.,range_rate_mps=-15.)
        if self.mode=='A':
            if attack:self.counts['sensor_attack_accepted']+=1
            return m
        packet=self.sensor_tx.seal(encode_sensor(m),src,ADAS,mid,now)
        if attack and self.attack=='A01':
            packet=self.sensor_tx.seal(encode_sensor(m),UNTRUSTED,ADAS,mid,now,key_id=7)
        rx=self.verifier(ADAS,'sensor');payload=rx.verify(packet,mid,now)
        if payload is None:
            self.event(rx.events[-1]['reason'],now)
            if attack:self.counts['sensor_attack_rejected']+=1
            result=None
        else:
            if attack:self.counts['sensor_attack_accepted']+=1
            result=decode_sensor(payload)
        return result
    def summary(self):
        combined=Counter();count=0;total=0;maximum=0
        for v in self.verifiers.values():
            combined.update(v.counts);count+=v.cpu_count;total+=v.cpu_total_ns;maximum=max(maximum,v.cpu_max_ns)
        return dict(mode=self.mode,attack=self.attack,counts=dict(self.counts),verifier_counts=dict(combined),
                    first_event_s=self.first_event_s,verification_calls=count,
                    verification_cpu_mean_us=total/count/1000 if count else None,
                    verification_cpu_max_us=maximum/1000 if count else None,
                    tx_cpu_mean_us=self.tx_cpu_total_ns/self.tx_cpu_count/1000 if self.tx_cpu_count else None,
                    recent_events=list(self.events))

class SecureBus:
    def __init__(self,underlying,context,channel):
        self.bus=underlying;self.context=context;self.channel=channel;self.senders={ADAS:Sender(channel),BRAKE:Sender(channel)}
        self.now_ms=-10;self.cache={};self.history=deque(maxlen=128);self.delayed=deque()
        self.jumped=False;self.restarted=False;self.recovered=False
        self.pressure_state="NORMAL";self.clear_since=None;self.last_drops=0
    def advance(self,now_ms=None):
        self.now_ms=self.now_ms+10 if now_ms is None else now_ms;self.cache.clear()
        ctx=self.context
        if ctx.attack=='A07' and ctx.active(self.now_ms) and self.channel in ctx.paths:
            # Fixed upper bound of six frames/step; queue and service budgets remain bounded.
            for _ in range(6):self.bus.send(CanFrame(1,b'FLOOD',self.now_ms,'ATTACK_FLOOD'))
            ctx.counts['flood_injected']+=6
        self.bus.advance(self.now_ms)
        pressure=len(self.bus.queued)>24 or self.bus.queue_drops>self.last_drops
        self.last_drops=self.bus.queue_drops
        if pressure:
            if self.pressure_state!='PRESSURE':ctx.event('BUS_PRESSURE',self.now_ms)
            self.pressure_state='PRESSURE';self.clear_since=None
        elif self.pressure_state=='PRESSURE':
            self.pressure_state='RECOVERING';self.clear_since=self.now_ms
            ctx.event('BUS_RECOVERING',self.now_ms)
        elif self.pressure_state=='RECOVERING' and self.now_ms-self.clear_since>=100:
            self.pressure_state='NORMAL';ctx.event('BUS_RECOVERED',self.now_ms)
    def send(self,frame):
        ctx=self.context;now=frame.timestamp_ms
        src,dst,_=ROUTES[frame.arbitration_id];tx=self.senders[src]
        if frame.arbitration_id==0x120:ctx.counts["commands_generated"]+=1
        relevant=frame.arbitration_id==eb.CAN_ID_BRAKE_REQ and self.channel in ctx.paths and ctx.active(now)
        if ctx.config.get('gateway_down') and ctx.active(now) and self.channel in ctx.paths:
            ctx.counts['gateway_withheld']+=1;ctx.counts['legitimate_withheld']+=1;return
        if relevant and ctx.attack=='A06' and not self.jumped:
            self.jumped=True
            if ctx.mode!='A':
                route=(ADAS,BRAKE,0x120,key_for(0x120,self.channel))
                tx.counters[route]=tx.counters.get(route,0)+1000
        if relevant and ctx.attack=='A10':
            if not self.restarted:tx.counters.clear();self.restarted=True
            if ctx.mode=='C' and now>=ctx.start+200 and not self.recovered:tx.restart();self.recovered=True
        payload=frame.data
        trusted_attack=relevant and (ctx.attack=='A12' or ctx.config.get('shared_key_compromise'))
        if trusted_attack:payload=evil_command(payload)
        t0=time.process_time_ns()
        packet=payload if ctx.mode=='A' else tx.seal(payload,src,dst,frame.arbitration_id,now)
        if ctx.mode!='A':ctx.tx_cpu_count+=1;ctx.tx_cpu_total_ns+=time.process_time_ns()-t0
        original_packet=packet
        attack=False;legitimate=True
        if relevant:
            if ctx.attack in ('A03','A04'):
                malicious=evil_command(payload);attack=True;legitimate=False
                if ctx.mode=='A':packet=malicious
                elif ctx.attack=='A03':packet=tx.seal(malicious,UNTRUSTED,BRAKE,0x120,now,key_id=7)
                else:
                    body=bytearray(packet);body[HEADER.size:HEADER.size+8]=malicious;packet=bytes(body)
            elif ctx.attack=='A02' and len(self.history)>=16:
                packet=self.history[-16];attack=True;legitimate=False
            elif ctx.attack in ('A05','A08'):
                delay=ctx.config.get('delay_ms',200 if ctx.attack=='A05' else 60)
                self.delayed.append((now,packet))
                if now-self.delayed[0][0]<delay:ctx.counts['legitimate_withheld']+=1;return
                packet=self.delayed.popleft()[1];attack=True;legitimate=False
            elif ctx.attack=='A09' and self.history and (now//10)%2:
                packet=self.history[-1];attack=True;legitimate=False
            elif ctx.attack in ('A06','A10'):
                attack=True # valid producer with freshness fault: count legitimate rejections separately
            elif trusted_attack:attack=True;legitimate=False
            if ctx.config.get('wrong_tag') and ctx.mode!='A':
                q=bytearray(packet);q[-1]^=1;packet=bytes(q);attack=True;legitimate=True
        if frame.arbitration_id==eb.CAN_ID_BRAKE_REQ:self.history.append(original_packet)
        # Provenance flags below are ONLY experiment instrumentation; verifier trusts no sender string.
        label=('ATTACK' if attack else 'NORMAL')+('_LEGIT' if legitimate else '')
        self.bus.send(CanFrame(frame.arbitration_id,packet,now,label,is_fd=ctx.mode!='A'))
        ctx.counts['wire_bytes']+=len(packet);ctx.counts['sent_frames']+=1
    def receive(self,mid,receiver=None):
        if receiver is None:receiver=BRAKE if mid==0x120 else BODY
        cache_key=(mid,receiver)
        if cache_key in self.cache:return self.cache[cache_key]
        fr=self.bus.receive(mid)
        if fr is None:self.cache[cache_key]=None;return None
        ctx=self.context;attack=fr.sender.startswith('ATTACK');legitimate=fr.sender.endswith('_LEGIT')
        if mid==0x120:ctx.counts['command_validation_attempts']+=1
        if attack:ctx.counts['attack_offered']+=1
        if legitimate:ctx.counts['legitimate_offered']+=1
        if ctx.mode=='A':payload=fr.data
        else:
            rx=ctx.verifier(receiver,self.channel);before=rx.counts['RESYNC'];payload=rx.verify(fr.data,mid,self.now_ms)
            if rx.counts['RESYNC']>before:ctx.event('RESYNC',self.now_ms)
            if payload is None:ctx.event(rx.events[-1]['reason'],self.now_ms)
            elif len(payload)!=8:
                ctx.event('PAYLOAD_LENGTH',self.now_ms);payload=None
        if attack:ctx.counts['attack_accepted' if payload is not None else 'attack_rejected']+=1
        if legitimate:ctx.counts['legitimate_accepted' if payload is not None else 'legitimate_rejected']+=1
        if mid==0x120 and payload is not None:
            ctx.counts['commands_gateway_delivered']+=1
            ctx.command_attack_delivery[self.channel]=(self.now_ms,attack)
        issued=HEADER.unpack_from(fr.data)[7] if payload is not None and ctx.mode!='A' else fr.timestamp_ms
        result=None if payload is None else CanFrame(mid,payload,issued,'VERIFIED_LOCAL' if ctx.mode!='A' else 'UNAUTHENTICATED')
        self.cache[cache_key]=result
        return result
