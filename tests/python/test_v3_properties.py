import _paths
import math
from hypothesis import given,settings,strategies as st
from aegis_sim.vehicle import Vehicle,pair_step,friction_limited_decel
from aegis_sim.perception import Fusion,Observation

# TEST-ID: PBT-V3-001 | VERIFIES: SIM-301
@settings(max_examples=100,derandomize=True,database=None)
@given(v=st.floats(0.1,40,allow_nan=False),mu=st.floats(.05,1,allow_nan=False),dt=st.floats(.001,.1,allow_nan=False))
def test_tire_limited_stop_never_reverses_or_exceeds_analytic_distance(v,mu,dt):
    a=friction_limited_decel(15,mu)
    e,l=Vehicle(0,v),Vehicle(100000,0)
    contact,gap=pair_step(e,l,dt,-a,0)
    assert contact is None and 0<=e.v_mps<=v
    assert e.x_m<=v*v/(2*a)+1e-9
    assert math.isclose(gap,l.x_m-e.x_m,abs_tol=1e-8)

# TEST-ID: PBT-V3-002 | VERIFIES: PER-302
@settings(max_examples=100,derandomize=True,database=None)
@given(gap=st.floats(1,150,allow_nan=False),rate=st.floats(-30,30,allow_nan=False),age=st.integers(0,150))
def test_consistent_delayed_sources_align_without_future_information(gap,rate,age):
    r=Observation(200,True,max(0,gap+rate*age/1000),rate)
    c=Observation(200-age,True,gap,rate)
    f=Fusion().update(200,r,c)
    assert f.mode=='COMBINED' and f.measurement.ts_ms==200
    assert math.isclose(f.measurement.range_m,r.range_m,abs_tol=1e-9)
