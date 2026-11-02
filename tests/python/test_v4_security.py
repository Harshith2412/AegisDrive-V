import _paths
import hmac
import pytest
from hypothesis import given,settings,strategies as st
from aegis_sim.security import *

def command(tx=None,**kw):
    return (tx or Sender()).seal(b'12345678',ADAS,BRAKE,0x120,100,**kw)

# TEST-ID: SEC-UT-001 | VERIFIES: SEC-401
def test_authentication_format_identity_and_integrity():
    p=command();assert len(p)==64
    assert Verifier(BRAKE).verify(p,0x120,110)==b'12345678'
    for idx in (0,1,2,3,4,10,20,30,48,63):
        bad=bytearray(p);bad[idx]^=1
        assert Verifier(BRAKE).verify(bytes(bad),0x120,110) is None
    assert Verifier(BODY).verify(p,0x120,110) is None
    assert Verifier(BRAKE,'backup').verify(p,0x120,110) is None
    wrong_path=Sender('backup').seal(bytes(8),BRAKE,0,0x220,100)
    assert Verifier(ADAS,'backup').verify(wrong_path,0x220,110) is None
    q=Sender().seal(b'12345678',UNTRUSTED,BRAKE,0x120,100,key_id=7)
    rx=Verifier(BRAKE);assert rx.verify(q,0x120,110) is None and rx.counts['UNAUTHORIZED']==1
    # Published RFC 4231 test vector exercises the actual established HMAC provider.
    assert hmac.digest(bytes([0x0b])*20,b'Hi There','sha256').hex()=='b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'

# TEST-ID: SEC-UT-002 | VERIFIES: SEC-402
def test_replay_age_gap_and_authenticated_resynchronization():
    tx=Sender();p=command(tx);r=Verifier(BRAKE)
    assert r.verify(p,0x120,200) is not None # 100 ms inclusive
    assert r.verify(p,0x120,200) is None and r.counts['REPLAY']==1
    assert Verifier(BRAKE).verify(p,0x120,201) is None
    assert Verifier(BRAKE).verify(p,0x120,99) is None
    jump=command(counter=1000)
    assert Verifier(BRAKE).verify(jump,0x120,110) is None
    c=Verifier(BRAKE,policy='C');assert c.verify(jump,0x120,110) is not None and c.counts['RESYNC']==1
    assert c.verify(command(counter=999),0x120,110) is None
    assert c.verify(command(counter=1001),0x120,110) is not None
    assert Verifier(BRAKE,policy='C').verify(command(counter=4096),0x120,110) is None

# TEST-ID: SEC-UT-003 | VERIFIES: SEC-402
def test_restart_retained_state_rollback_and_counter_exhaustion():
    store=FreshnessStore();tx=Sender();p=command(tx)
    assert Verifier(BRAKE,store=store).verify(p,0x120,110)
    assert Verifier(BRAKE,store=store).verify(p,0x120,110) is None # receiver restart keeps NVM
    assert Verifier(BRAKE).verify(p,0x120,110) is not None # total retained-state loss remains vulnerable
    tx.restart();p2=command(tx)
    assert Verifier(BRAKE,policy='B',store=store).verify(p2,0x120,110) is None
    assert Verifier(BRAKE,policy='C',store=store).verify(p2,0x120,110)
    assert Verifier(BRAKE,policy='C',store=store).verify(p,0x120,110) is None
    tx.counters[(ADAS,BRAKE,0x120,1)]=2**64-1
    assert len(command(tx))==64
    with pytest.raises(OverflowError):command(tx)
    tx.epoch=0xffffffff
    with pytest.raises(OverflowError):tx.restart()
    from aegis_sim.security_gateway import SecureBus,CapacityBus,SecurityContext
    from aegis_sim.can_bus import CanFrame
    gateway=SecureBus(CapacityBus(),SecurityContext(dict(mode='C',attack='A10',start_s=2)),'primary')
    gateway.send(CanFrame(0x120,bytes(8),2000,'ADAS'))
    gateway.send(CanFrame(0x120,bytes(8),2200,'ADAS'))
    assert gateway.senders[ADAS].epoch==2 and gateway.senders[BRAKE].epoch==1

# TEST-ID: SEC-PBT-001 | VERIFIES: SEC-401
@settings(max_examples=100,derandomize=True,database=None)
@given(payload=st.binary(max_size=21),index=st.integers(0,63))
def test_any_single_bit_mutation_is_rejected(payload,index):
    p=Sender().seal(payload,ADAS,BRAKE,0x120,0)
    assert Verifier(BRAKE).verify(p,0x120,0)==payload
    q=bytearray(p);q[index]^=1
    assert Verifier(BRAKE).verify(bytes(q),0x120,0) is None

# TEST-ID: SEC-PBT-002 | VERIFIES: SEC-401
@settings(max_examples=100,derandomize=True,database=None)
@given(raw=st.binary(min_size=0,max_size=100))
def test_malformed_untrusted_messages_do_not_raise_or_advance_state(raw):
    store=FreshnessStore();v=Verifier(BRAKE,store=store)
    assert v.verify(raw,0x120,10) is None
    assert not store.values

# TEST-ID: SEC-UT-004 | VERIFIES: SEC-401, SEC-402, SEC-405
def test_provisioning_padding_reordering_and_bounded_diagnostics():
    p=command();v=Verifier(BRAKE,keys={})
    assert v.verify(p,0x120,110) is None and v.counts['KEY']==1
    with pytest.raises(ValueError):Sender().seal(bytes(22),ADAS,BRAKE,0x120,0)
    with pytest.raises(ValueError):Sender().seal(b'',ADAS,BRAKE,0x800,0)
    q=bytearray(p);q[40]=1
    q[48:]=hmac.digest(TEST_KEYS[1],domain('primary')+q[:48],'sha256')[:16]
    rx=Verifier(BRAKE);assert rx.verify(bytes(q),0x120,110) is None and rx.counts['PADDING']==1
    v=Verifier(BRAKE)
    assert v.verify(command(counter=31),0x120,110)
    assert v.verify(command(counter=30),0x120,110) is None
    assert Verifier(BRAKE,policy='C').verify(command(epoch=3),0x120,110) is None
    for _ in range(300):v.verify(b'bad',0x120,110)
    assert len(v.events)==128 and v.counts['LENGTH']==300
