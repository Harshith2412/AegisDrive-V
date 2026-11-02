import _paths
from dataclasses import replace
import pytest
from hypothesis import given,settings,strategies as st
from aegis_sim.assurance import select_authenticated_primary,ConfirmationStudy
from aegis_sim.can_bus import CanFrame
from aegis_sim.security_gateway import SecurityContext,CapacityBus,SecureBus
from aegis_sim.perception import FusionResult,Observation
from aegis_sim.runner import run_scenario
from aegis_sim.scenario import load_scenario
from _paths import SCENARIOS

# TEST-ID: REV-UT-001 | VERIFIES: REC-501
def test_verified_command_arbitration_time_boundary_and_missing_paths():
    p=CanFrame(0x120,bytes(8),100,'VERIFIED_LOCAL')
    assert select_authenticated_primary(p,replace(p,timestamp_ms=101)) is None
    assert select_authenticated_primary(p,replace(p,timestamp_ms=100)) is p
    assert select_authenticated_primary(p,replace(p,timestamp_ms=99)) is p
    assert select_authenticated_primary(p,None) is p
    assert select_authenticated_primary(None,p) is None
    sc=load_scenario(SCENARIOS/'S03_stationary_target.yaml')
    with pytest.raises(ValueError):run_scenario(sc,assurance={'prefer_latest_authenticated':True})
    with pytest.raises(ValueError):run_scenario(sc,security={'mode':'A'},assurance={'prefer_latest_authenticated':True})

# TEST-ID: REV-UT-002 | VERIFIES: REC-502
def test_pressure_is_current_condition_and_recovery_has_dwell():
    bus=CapacityBus();ctx=SecurityContext({'mode':'C'});secure=SecureBus(bus,ctx,'primary')
    bus.max_backlog=40;secure.advance(0)
    assert secure.pressure_state=='NORMAL' and ctx.first_event_s is None
    for i in range(40):bus.send(CanFrame(1,b'x',1,'load'))
    secure.advance(10);assert secure.pressure_state=='PRESSURE'
    for t in range(20,201,10):secure.advance(t)
    assert secure.pressure_state=='NORMAL'
    assert ctx.counts['BUS_PRESSURE']==1 and ctx.counts['BUS_RECOVERED']==1

# TEST-ID: REV-UT-003 | VERIFIES: SOT-501
def test_confirmation_uses_distinct_acquisitions_and_preserves_persistent_ghost_limit():
    r=Observation(0,True,12,-15)
    fused=FusionResult(r,'COMBINED',True,True)
    absent=Observation(0,False,0,0)
    f=ConfirmationStudy()
    assert not f.update(fused,r,absent,0).sensor_ok
    assert not f.update(fused,r,absent,40).sensor_ok # cached sample is not independent evidence
    r=replace(r,ts_ms=50)
    assert f.update(replace(fused,measurement=r),r,absent,50).sensor_ok # persistent ghost still passes
    assert not ConfirmationStudy('corroborated').update(fused,r,absent,100).sensor_ok
    low=ConfirmationStudy('conservative').update(fused,r,absent,100)
    assert low.confidence<.65 and not low.sensor_ok
    assert ConfirmationStudy().update(fused,r,r,100).sensor_ok

# TEST-ID: REV-ST-001 | VERIFIES: REC-501
def test_newer_authenticated_backup_is_selected_and_bad_backup_not_accepted():
    sc=replace(load_scenario(SCENARIOS/'S03_stationary_target.yaml'),perception='combined',backup_enabled=True,imu_monitor=True)
    r=run_scenario(sc,0,security={'mode':'C','attack':'A08','start_s':2,'delay_ms':60},assurance={'prefer_latest_authenticated':True})
    assert not r.collision and r.authenticated_backup_preferred_cycles>0
    bad=run_scenario(sc,0,security={'mode':'C','attack':'CORRUPT_LEGIT','wrong_tag':True,'paths':['backup'],'start_s':2},assurance={'prefer_latest_authenticated':True})
    assert not bad.collision and bad.security_stats['verifier_counts']['AUTH']>0

# TEST-ID: REV-UT-004 | VERIFIES: QLT-501
def test_c_abi_null_and_closed_handle_errors_are_explicit():
    from aegis_sim import ecu_bindings as eb
    lib=eb.lib()
    for name in ('aegis_adas_step','aegis_brake_step','aegis_body_step'):
        assert getattr(lib,name)(None,None,None)==-1
    assert lib.aegis_adas_state(None)==6
    assert lib.aegis_struct_size(-1)==0 and lib.aegis_struct_size(999)==0
    assert lib.aegis_adas_config_valid(None)==0
    assert not lib.aegis_adas_request_transition(None,255)
    assert not lib.aegis_adas_transition_allowed(255,1)
    assert not lib.aegis_adas_transition_allowed(1,255)
    import ctypes as C
    for cls,inp,out,name in ((eb.AdasEcu,eb.AdasInput,eb.AdasOutput,'aegis_adas_step'),(eb.BrakeEcu,eb.BrakeInput,eb.BrakeOutput,'aegis_brake_step'),(eb.BodyEcu,eb.BodyInput,eb.BodyOutput,'aegis_body_step')):
        handle=cls();output=out();input_value=inp()
        assert getattr(lib,name)(handle._h,None,C.byref(output))==-1
        assert getattr(lib,name)(handle._h,C.byref(input_value),None)==-1
        handle.close();handle.close()
        with pytest.raises(RuntimeError):handle.step(inp())

# TEST-ID: REV-PBT-001 | VERIFIES: QLT-501
@settings(max_examples=100,derandomize=True,database=None)
@given(gap=st.floats(.0001,3,allow_nan=False),closing=st.floats(.1,40,allow_nan=False))
def test_contact_matches_independent_constant_velocity_oracle(gap,closing):
    from aegis_sim.vehicle import Vehicle,pair_step
    ego,lead=Vehicle(0,closing+1),Vehicle(gap,1)
    expected=gap/closing
    contact,minimum=pair_step(ego,lead,.1,0,0)
    if expected<=.1:
        assert contact is not None and abs(contact-expected)<1e-10 and minimum==0
    else:assert contact is None and abs(minimum-(gap-.1*closing))<1e-10

# TEST-ID: REV-ST-002 | VERIFIES: SOT-501
def test_bounded_braking_study_is_explicit_and_not_a_safe_default():
    sc=replace(load_scenario(SCENARIOS/'S03_stationary_target.yaml'),gap0_m=5,perception='combined')
    r=run_scenario(sc,0,assurance={'brake_cap_mps2':3})
    assert r.max_requested_decel_mps2<=3 and r.collision # limited demand cannot fix insufficient distance
    with pytest.raises(ValueError):run_scenario(sc,assurance={'brake_cap_mps2':0})

# TEST-ID: REV-PBT-002 | VERIFIES: SEC-402
@settings(max_examples=100,derandomize=True,database=None)
@given(sequence=st.lists(st.integers(0,100),min_size=1,max_size=40))
def test_stateful_replay_contract_matches_independent_accepted_sequence(sequence):
    from aegis_sim.security import Sender,Verifier,ADAS,BRAKE
    tx=Sender();rx=Verifier(BRAKE);accepted=-1
    for counter in sequence:
        packet=tx.seal(b'x',ADAS,BRAKE,0x120,0,counter=counter)
        expected=counter>accepted and counter-accepted<=32
        assert (rx.verify(packet,0x120,0) is not None)==expected
        if expected:accepted=counter
