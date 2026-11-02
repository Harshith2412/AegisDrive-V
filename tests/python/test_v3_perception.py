import _paths
import numpy as np
from aegis_sim.perception import Observation,CameraModel,Fusion

def obs(t=0,r=30,rr=-10,confidence=.9,ok=True,present=True):
    return Observation(t,present,r,rr,ok,confidence)

# TEST-ID: UT-V3-004 | VERIFIES: PER-301
def test_camera_latency_timestamp_fov_probability_and_confidence():
    c=CameraModel(np.random.default_rng(1),latency_ms=80,detection_probability=1,range_sigma_m=0,rate_sigma_mps=0)
    assert c.update(0,30,-10) is None
    assert c.update(50,29.5,-10) is None
    m=c.update(80,29.2,-10)
    assert m.ts_ms==0 and m.range_m==30 and m.range_rate_mps==-10
    for cfg in ({'detection_probability':0},{'lateral_offset_m':100},{'visibility':0},{'occlusion':1}):
        c=CameraModel(np.random.default_rng(2),latency_ms=0,**cfg)
        m=c.update(0,30,-10)
        assert not m.object_present
        if cfg.get("visibility")==0 or cfg.get("occlusion")==1:assert m.confidence==0
    c=CameraModel(np.random.default_rng(2),latency_ms=0,unavailable_at_ms=50)
    assert c.update(0,30,-10).sensor_ok
    assert not c.update(50,30,-10).sensor_ok

# TEST-ID: UT-V3-005 | VERIFIES: PER-302
def test_fusion_causal_alignment_confidence_and_disagreement():
    f=Fusion()
    m=f.update(100,obs(100,29),obs(0,30))
    assert m.mode=='COMBINED' and m.measurement.range_m==29
    assert f.update(100,obs(101),None).mode=='UNAVAILABLE' # future
    assert f.update(151,obs(0),None).mode=='UNAVAILABLE' # stale
    assert f.update(100,obs(100,confidence=.64),None).mode=='UNAVAILABLE'
    assert f.update(100,obs(100,30),obs(100,40)).mode=='DISAGREEMENT'
    assert f.update(100,obs(100,rr=-10),obs(100,rr=-2)).mode=='DISAGREEMENT'
    assert f.update(100,None,obs(100)).mode=='CAMERA_ONLY'
    assert f.update(100,obs(100),None).mode=='RADAR_ONLY'
    assert f.update(100,obs(100),obs(100,present=False)).measurement.object_present

# TEST-ID: UT-V3-006 | VERIFIES: PER-302
def test_fusion_parameter_properties_and_common_bias_limit():
    f=Fusion()
    for gap in (5.,20.,80.):
        for age in (0,50,100,150,151):
            for rate in (-20.,-5.,0.,5.):
                now=200
                a=obs(now,gap+rate*age/1000,rate)
                b=obs(now-age,gap,rate)
                r=f.update(now,a,b)
                assert r.measurement.ts_ms<=now
                if age<=150:
                    assert abs(r.measurement.range_m-max(0.,a.range_m))<1e-10
    # Consistent common-mode error is not detectable through agreement.
    r=f.update(0,obs(0,80),obs(0,80))
    assert r.mode=='COMBINED' and r.measurement.range_m==80
