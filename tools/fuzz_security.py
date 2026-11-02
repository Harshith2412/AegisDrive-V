#!/usr/bin/env python3
"""Bounded reproducible Python mutation fuzzing, not coverage-guided native fuzzing."""
import sys,random,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'sim'))
from aegis_sim.security import Sender,Verifier,ADAS,BRAKE
rng=random.Random(440031);accepted=0
base=Sender().seal(bytes(8),ADAS,BRAKE,0x120,0)
for i in range(20000):
    if i%2:
        raw=bytearray(base);pos=rng.randrange(64);raw[pos]^=1<<rng.randrange(8);raw=bytes(raw)
    else:raw=rng.randbytes(rng.randrange(0,100))
    rx=Verifier(BRAKE);result=rx.verify(raw,0x120,10)
    if result is not None:accepted+=1
    assert not rx.store.values
out=dict(engine='seeded Python mutation/random parser fuzzing',seed=440031,executions=20000,unexpected_acceptances=accepted,
         native_libfuzzer='Build attempted, unavailable AppleClang libclang_rt.fuzzer_osx.a; see fuzz-build.log',
         limitation='No crash in finite inputs is not proof of parser safety; not coverage-guided fuzzing')
(ROOT/'results/v0.4.0/fuzz-python.json').write_text(json.dumps(out,indent=2));print(out)
