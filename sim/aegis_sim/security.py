"""Educational CAN FD authentication boundary, NOT AUTOSAR SecOC conformance.

Uses Python's established hmac/hashlib (OpenSSL-backed digest fast path), no custom
cryptographic primitive. All fixture keys are PUBLIC and TEST ONLY. Each protected
PDU is exactly 64 bytes: 27-byte header + <=21-byte payload + zero padding to byte48
+ 16-byte HMAC-SHA256 tag. Header, payload, padding and channel domain are MAC-bound.
"""
from __future__ import annotations
from collections import Counter,deque
from dataclasses import dataclass,field
import hmac,struct,time

HEADER=struct.Struct('!BBBBHIQQB')
TAG_BYTES=16
MAX_PAYLOAD=21
VERSION=1
ADAS,BRAKE,BODY,RADAR,CAMERA,UNTRUSTED=1,2,3,4,5,9
RADAR_ID,CAMERA_ID=0x300,0x301
# Public deterministic fixtures, not production secrets or key derivation.
TEST_KEYS={i:bytes([i])*32 for i in range(1,9)}
ROUTES={0x120:(ADAS,BRAKE,1),0x130:(ADAS,BODY,2),0x220:(BRAKE,0,3),
        RADAR_ID:(RADAR,ADAS,4),CAMERA_ID:(CAMERA,ADAS,5)}
SENSOR=struct.Struct('!ffQfB') # 21 bytes; measured age remains in acquisition timestamp

def domain(channel):
    if channel not in ('primary','backup','sensor'):raise ValueError('unknown security domain')
    return b'AegisDrive-V/v0.4/'+channel.encode('ascii')+b'\0'

def key_for(msgid,channel):
    key=ROUTES[msgid][2]
    return 6 if channel=='backup' and msgid==0x120 else key

@dataclass
class FreshnessStore:
    """Retained NVM abstraction; not durable storage or tamper-resistant hardware."""
    values: dict=field(default_factory=dict)

class Sender:
    def __init__(self,channel='primary',keys=None):
        self.channel=channel;self.keys=TEST_KEYS if keys is None else keys
        self.counters={};self.epoch=1
    def restart(self):
        if self.epoch==0xffffffff:raise OverflowError('boot epoch exhausted; reprovision required')
        self.epoch+=1;self.counters.clear()
    def seal(self,payload,sender,receiver,msgid,now_ms,key_id=None,counter=None,epoch=None):
        if not isinstance(payload,bytes) or len(payload)>MAX_PAYLOAD:raise ValueError('payload >21 bytes or not bytes')
        if not 0<=msgid<=0x7ff:raise ValueError('11-bit message identifier required')
        if key_id is None:key_id=key_for(msgid,self.channel)
        route=(sender,receiver,msgid,key_id)
        count=self.counters.get(route,0) if counter is None else counter
        if not 0<=count<2**64:raise OverflowError('freshness counter exhausted; do not wrap')
        head=HEADER.pack(VERSION,sender,receiver,key_id,msgid,self.epoch if epoch is None else epoch,count,now_ms,len(payload))
        body=(head+payload).ljust(48,b'\0')
        tag=hmac.digest(self.keys[key_id],domain(self.channel)+body,'sha256')[:TAG_BYTES]
        self.counters[route]=count+1
        return body+tag

class Verifier:
    def __init__(self,receiver,channel='primary',policy='B',store=None,keys=None,max_age_ms=100):
        if policy not in ('B','C'):raise ValueError('policy must be B or C')
        domain(channel) # configuration fails early rather than during untrusted parsing
        self.receiver=receiver;self.channel=channel;self.policy=policy
        self.store=store if store is not None else FreshnessStore()
        self.keys=TEST_KEYS if keys is None else keys;self.age=max_age_ms
        self.counts=Counter();self.events=deque(maxlen=128);self.cpu_count=0;self.cpu_total_ns=0;self.cpu_max_ns=0
    def _event(self,reason,now,msgid,start):
        self.counts[reason]+=1;self.events.append(dict(reason=reason,now_ms=now,msgid=msgid))
        if reason!='RESYNC':
            elapsed=time.process_time_ns()-start;self.cpu_count+=1;self.cpu_total_ns+=elapsed
            self.cpu_max_ns=max(self.cpu_max_ns,elapsed)
    def verify(self,packet,expected_id,now_ms):
        start=time.process_time_ns()
        def reject(reason):self._event(reason,now_ms,expected_id,start);return None
        if not isinstance(packet,bytes) or len(packet)!=64:return reject('LENGTH')
        ver,src,dst,kid,mid,epoch,count,issued,size=HEADER.unpack_from(packet)
        if ver!=VERSION or size>MAX_PAYLOAD or mid!=expected_id:return reject('HEADER')
        allowed={'primary':(0x120,0x130,0x220),'backup':(0x120,),'sensor':(RADAR_ID,CAMERA_ID)}
        if mid not in allowed[self.channel]:return reject('POLICY')
        route=ROUTES.get(mid)
        if route is None:return reject('POLICY')
        authorized_sender,authorized_dst,_=route
        if src!=authorized_sender or dst!=authorized_dst or kid!=key_for(mid,self.channel):return reject('UNAUTHORIZED')
        if dst not in (self.receiver,0) or (mid==0x220 and self.receiver not in (ADAS,BODY)):return reject('DESTINATION')
        key=self.keys.get(kid)
        if key is None:return reject('KEY')
        calculated=hmac.digest(key,domain(self.channel)+packet[:48],'sha256')[:TAG_BYTES]
        if not hmac.compare_digest(calculated,packet[48:]):return reject('AUTH')
        if any(packet[HEADER.size+size:48]):return reject('PADDING')
        if issued>now_ms:return reject('FUTURE')
        if now_ms-issued>self.age:return reject('STALE')
        identity=(self.channel,src,dst,mid,kid)
        last_epoch,last_count=self.store.values.get(identity,(1,-1))
        if epoch<last_epoch:return reject('ROLLBACK')
        if epoch!=last_epoch:
            if self.policy!='C' or epoch!=last_epoch+1:return reject('EPOCH')
            last_count=-1
        if count<=last_count:return reject('REPLAY')
        gap=count-last_count
        if gap>(4096 if self.policy=='C' else 32):return reject('GAP')
        if epoch!=last_epoch or gap>32:self._event('RESYNC',now_ms,mid,start)
        self.store.values[identity]=(epoch,count)
        self._event('ACCEPT',now_ms,mid,start)
        return packet[HEADER.size:HEADER.size+size]

def encode_sensor(m):
    return SENSOR.pack(m.range_m,m.range_rate_mps,m.ts_ms,getattr(m,'confidence',.9),
                       (1 if m.object_present else 0)|(2 if m.sensor_ok else 0))
def decode_sensor(payload):
    from .perception import Observation
    if len(payload)!=SENSOR.size:raise ValueError('sensor payload length')
    r,rr,ts,c,flags=SENSOR.unpack(payload)
    if flags&~3:raise ValueError('sensor reserved flags')
    return Observation(ts,bool(flags&1),r,rr,bool(flags&2),c)
