import _paths
import math
from aegis_sim.vehicle import Vehicle, pair_step, friction_limited_decel

# TEST-ID: UT-V3-001 | VERIFIES: SIM-301
def test_contact_inside_step_and_stopping_segments():
    e,l=Vehicle(0,10),Vehicle(.05,0)
    t,gap=pair_step(e,l,.01,0,0)
    assert abs(t-.005)<1e-12 and gap==0
    assert abs(e.x_m-l.x_m)<1e-12
    # Endpoints positive, interior quadratic minimum negative (tunneling).
    e,l=Vehicle(0,2),Vehicle(.001,0)
    t,gap=pair_step(e,l,.1,-200,200)
    assert t is not None and t < .01 and gap==0
    e,l=Vehicle(0,1),Vehicle(10,0)
    t,gap=pair_step(e,l,1,-2,0)
    assert t is None and abs(e.x_m-.25)<1e-12 and e.v_mps==0
    from aegis_sim.scenario import Scenario
    from aegis_sim.runner import run_scenario
    import tempfile,csv
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        sc=Scenario('horizon','Horizon braking',duration_s=.02,gap0_m=5)
        path=Path(tmp)/'trace.csv'
        result=run_scenario(sc,0,trace_path=path)
        rows=list(csv.DictReader(path.open()))
        assert result.steps==3 and float(rows[-1]['t_s'])==.02
        assert result.final_ego_speed_mps==float(rows[-1]['ego_v_mps'])
    try:run_scenario(Scenario('invalid','Invalid horizon',duration_s=.025),0)
    except ValueError:pass
    else:raise AssertionError('nonintegral horizon accepted')

# TEST-ID: UT-V3-002 | VERIFIES: SIM-301
def test_friction_and_stopping_distance_parameter_properties():
    # Deterministic parameter grid: independent physics identity, not seed repetition.
    for mu in (.1,.3,.5,.9,1.):
        for v in (1.,5.,15.,25.):
            a=friction_limited_decel(15.,mu)
            assert 0<=a<=mu*9.81
            e=Vehicle(0,v)
            e.step(v/a+1,-a)
            assert math.isclose(e.x_m,v*v/(2*a),rel_tol=1e-12)
            assert e.v_mps==0
