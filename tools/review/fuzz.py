#!/usr/bin/env python3
"""Finite deterministic mutation fuzzing and manually specified policy vector oracle."""
import sys,json,random,hmac
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.security import Sender,Verifier,ADAS,BRAKE,UNTRUSTED
OUT=ROOT/'results/v1.0.0';rng=random.Random(110077)
base=Sender().seal(bytes(8),ADAS,BRAKE,0x120,100)
for i in range(100000):
 if i%2:
  raw=bytearray(base);raw[rng.randrange(64)]^=1<<rng.randrange(8);raw=bytes(raw)
 else:raw=rng.randbytes(rng.randrange(0,129))
 rx=Verifier(BRAKE);assert rx.verify(raw,0x120,110) is None and not rx.store.values
vectors=[]
for policy in 'BC':
 for name,packet,now,expected in [
   ('valid',base,110,True),('age_boundary',base,200,True),('expired',base,201,False),('future',base,99,False),
   ('wrong_sender',Sender().seal(bytes(8),UNTRUSTED,BRAKE,0x120,100,key_id=7),110,False),
   ('bad_length',base[:-1],110,False),
   ('bounded_jump',Sender().seal(bytes(8),ADAS,BRAKE,0x120,100,counter=1000),110,policy=='C'),
   ('next_epoch',Sender().seal(bytes(8),ADAS,BRAKE,0x120,100,epoch=2),110,policy=='C'),
   ('skipped_epoch',Sender().seal(bytes(8),ADAS,BRAKE,0x120,100,epoch=3),110,False)]:
  actual=Verifier(BRAKE,policy=policy).verify(packet,0x120,now) is not None
  assert actual==expected
  vectors.append(dict(policy=policy,case=name,expected_admission=expected,actual_admission=actual))
 rx=Verifier(BRAKE,policy=policy);assert rx.verify(base,0x120,110) is not None
 actual=rx.verify(base,0x120,110) is not None;assert not actual
 vectors.append(dict(policy=policy,case='duplicate',expected_admission=False,actual_admission=actual))
(OUT/'quality/fuzz.json').write_text(json.dumps(dict(engine='Seeded Python mutation/random, not native coverage-guided fuzzing',seed=110077,executions=100000,unexpected_acceptance=0,exceptions=0,policy_vectors=vectors,
 caveat='Known protocol-oracle checks, not semantic safe-intent accuracy or zero attack probability. Native libFuzzer remains unavailable.'),indent=2))
print('100000 finite parser inputs; 20 known policy vectors; zero mismatches')
