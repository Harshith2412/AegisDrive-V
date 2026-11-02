#include <cmath>
#include <limits>
#include "gtest/gtest.h"
#include "aegis/adas_ecu.hpp"
#include "aegis/codec.hpp"
#include "aegis/e2e.hpp"
#include "test_helpers.hpp"

using namespace aegis;
using aegis::test::nominal;

namespace {
constexpr double kV = 13.9;  // ~50 km/h, inside the activation window
AdasEcu monitoring_ecu(std::uint64_t& t) {
    AdasEcu ecu(default_adas_config());
    ecu.step(nominal(t, kV, false));
    t += 10;
    return ecu;
}
}  // namespace

// TEST-ID: UT-ADAS-001 | VERIFIES: ADAS-REQ-001
TEST(AdasTtc, TimeToCollisionComputation) {
    EXPECT_NEAR(compute_ttc(20.0, -10.0, 0.5), 2.0, 1e-12);
    EXPECT_NEAR(compute_ttc(0.0, -10.0, 0.5), 0.0, 1e-12);
    EXPECT_TRUE(std::isinf(compute_ttc(20.0, -0.5, 0.5)));  // boundary: not strictly above threshold
    EXPECT_TRUE(std::isinf(compute_ttc(20.0, 3.0, 0.5)));   // opening gap
    EXPECT_NEAR(compute_ttc(20.0, -0.51, 0.5), 20.0 / 0.51, 1e-9);
}

// TEST-ID: UT-ADAS-002 | VERIFIES: ADAS-REQ-003
TEST(AdasTtc, RequiredDecelerationComputation) {
    EXPECT_NEAR(compute_required_decel(22.0, -10.0, 2.0), 2.5, 1e-12);
    EXPECT_NEAR(compute_required_decel(2.0, -1.0, 2.0), 1.0 / 0.2, 1e-12);  // floor of 0.1 m
    EXPECT_NEAR(compute_required_decel(30.0, 1.0, 2.0), 0.0, 1e-12);
}

// TEST-ID: UT-ADAS-003 | VERIFIES: ADAS-REQ-004, ADAS-REQ-007
TEST(AdasStateMachine, EnableDisableAndActivation) {
    AdasEcu ecu(default_adas_config());
    AegisAdasInput in = nominal(0, kV, false);
    in.function_enabled = 0;
    EXPECT_EQ(ecu.step(in).state, AEGIS_ADAS_DISABLED);
    in.function_enabled = 1;
    in.ego_speed_mps = 1.0;  // below window
    EXPECT_EQ(ecu.step(in).state, AEGIS_ADAS_STANDBY);
    in.ego_speed_mps = kV;
    EXPECT_EQ(ecu.step(in).state, AEGIS_ADAS_MONITORING);
    in.function_enabled = 0;
    EXPECT_EQ(ecu.step(in).state, AEGIS_ADAS_DISABLED);
}

// TEST-ID: UT-ADAS-004 | VERIFIES: ADAS-REQ-002
TEST(AdasDecision, WarningThresholdBoundaryAndHysteresis) {
    std::uint64_t t = 0;
    auto cfg = default_adas_config();
    cfg.planning_decel_mps2 = 0.0; // isolate legacy TTC boundaries
    AdasEcu ecu(cfg);
    ecu.step(nominal(0, kV, false));
    t = 10;
    EXPECT_EQ(ecu.step(nominal(t, kV, true, 26.1, -10.0)).state, AEGIS_ADAS_MONITORING);  // TTC 2.61
    t += 10;
    auto out = ecu.step(nominal(t, kV, true, 26.0, -10.0));  // TTC 2.60 exactly
    EXPECT_EQ(out.state, AEGIS_ADAS_WARNING);
    EXPECT_EQ(out.warning_active, 1);
    EXPECT_EQ(out.brake_request_active, 0);
    t += 10;
    EXPECT_EQ(ecu.step(nominal(t, kV, true, 28.5, -10.0)).state, AEGIS_ADAS_WARNING);  // 2.85 < 2.9
    t += 10;
    EXPECT_EQ(ecu.step(nominal(t, kV, true, 29.5, -10.0)).state, AEGIS_ADAS_MONITORING);  // 2.95 > 2.9
}

// TEST-ID: UT-ADAS-005 | VERIFIES: ADAS-REQ-003
TEST(AdasDecision, BrakingThresholdAndDecelClamp) {
    std::uint64_t t = 0;
    auto cfg = default_adas_config();
    cfg.planning_decel_mps2 = 0.0; // isolate legacy TTC boundaries
    AdasEcu ecu(cfg);
    ecu.step(nominal(0, kV, false));
    t = 10;
    EXPECT_EQ(ecu.step(nominal(t, kV, true, 16.1, -10.0)).state, AEGIS_ADAS_WARNING);  // TTC 1.61
    t += 10;
    auto out = ecu.step(nominal(t, kV, true, 16.0, -10.0));  // TTC 1.60
    EXPECT_EQ(out.state, AEGIS_ADAS_BRAKING);
    EXPECT_EQ(out.brake_request_active, 1);
    EXPECT_NEAR(out.decel_request_mps2, 1.2 * 100.0 / (2.0 * 14.0), 1e-9);
    t += 10;
    out = ecu.step(nominal(t, kV, true, 3.0, -2.0));  // a_req*1.2 = 2.4 -> clamped to 4.0
    EXPECT_NEAR(out.decel_request_mps2, 4.0, 1e-12);
    t += 10;
    out = ecu.step(nominal(t, kV, true, 10.0, -15.0));  // a_req*1.2 = 16.9 -> clamped to 9.0
    EXPECT_NEAR(out.decel_request_mps2, 9.0, 1e-12);
    EXPECT_EQ(out.emergency, 1);
}

// TEST-ID: UT-ADAS-006 | VERIFIES: ADAS-REQ-004
TEST(AdasDecision, NoInterventionOutsideSpeedWindow) {
    for (double v : {2.0, 25.0}) {
        AdasEcu ecu(default_adas_config());
        auto out = ecu.step(nominal(0, v, true, 5.0, -10.0));  // TTC 0.5 s
        EXPECT_EQ(out.state, AEGIS_ADAS_STANDBY);
        EXPECT_EQ(out.brake_request_active, 0);
        EXPECT_EQ(out.warning_active, 0);
    }
}

// TEST-ID: UT-ADAS-007 | VERIFIES: ADAS-REQ-004, ADAS-REQ-005
TEST(AdasDecision, BrakeToStandstillThenHoldAndRelease) {
    std::uint64_t t = 0;
    AdasEcu ecu = monitoring_ecu(t);
    EXPECT_EQ(ecu.step(nominal(t, kV, true, 10.0, -10.0)).state, AEGIS_ADAS_BRAKING);
    t += 10;
    // Below activation window but still moving: braking must continue.
    EXPECT_EQ(ecu.step(nominal(t, 1.0, true, 3.0, -1.0)).state, AEGIS_ADAS_BRAKING);
    t += 10;
    const std::uint64_t t_stop = t;
    AegisAdasOutput out{};
    while (t < t_stop + 1990) {
        out = ecu.step(nominal(t, 0.0, true, 2.5, 0.0));
        EXPECT_EQ(out.state, AEGIS_ADAS_BRAKING);
        EXPECT_EQ(out.standstill, 1);
        t += 10;
    }
    out = ecu.step(nominal(t, 0.0, true, 2.5, 0.0));  // 1990 ms
    EXPECT_EQ(out.state, AEGIS_ADAS_BRAKING);
    t += 10;
    out = ecu.step(nominal(t, 0.0, true, 2.5, 0.0));  // 2000 ms hold elapsed
    EXPECT_EQ(out.state, AEGIS_ADAS_STANDBY);
    EXPECT_EQ(out.brake_request_active, 0);
    EXPECT_NEAR(out.decel_request_mps2, 0.0, 0.0);
}

// TEST-ID: UT-ADAS-008 | VERIFIES: ADAS-REQ-006
TEST(AdasDecision, AbortBrakingWhenThreatClears) {
    std::uint64_t t = 0;
    AdasEcu ecu = monitoring_ecu(t);
    EXPECT_EQ(ecu.step(nominal(t, kV, true, 10.0, -10.0)).state, AEGIS_ADAS_BRAKING);
    t += 10;
    const std::uint64_t t0 = t;
    while (t < t0 + 500) {
        EXPECT_EQ(ecu.step(nominal(t, 8.0, true, 12.0, 1.0)).state, AEGIS_ADAS_BRAKING);
        t += 10;
    }
    EXPECT_EQ(ecu.step(nominal(t, 8.0, true, 12.0, 1.0)).state, AEGIS_ADAS_MONITORING);
}

// TEST-ID: UT-ADAS-009 | VERIFIES: FSR-001, TSR-001
TEST(AdasSafety, StaleMeasurementBoundary) {
    std::uint64_t t = 1000;
    AdasEcu ecu = monitoring_ecu(t);
    AegisAdasInput in = nominal(t, kV, true, 50.0, -1.0);
    in.meas_ts_ms = t - 150;  // exactly at the limit: still fresh
    EXPECT_EQ(ecu.step(in).state, AEGIS_ADAS_MONITORING);
    t += 10;
    in = nominal(t, kV, true, 50.0, -1.0);
    in.meas_ts_ms = t - 151;
    auto out = ecu.step(in);
    EXPECT_EQ(out.state, AEGIS_ADAS_DEGRADED);
    EXPECT_EQ(out.function_unavailable, 1);
    EXPECT_TRUE((out.dtc_flags & AEGIS_DTC_STALE_INPUT) != 0);
}

// TEST-ID: UT-ADAS-010 | VERIFIES: FSR-001, TSR-001
TEST(AdasSafety, FrozenDataDuringBrakingReleasesRequest) {
    std::uint64_t t = 1000;
    AdasEcu ecu = monitoring_ecu(t);
    EXPECT_EQ(ecu.step(nominal(t, kV, true, 10.0, -10.0)).state, AEGIS_ADAS_BRAKING);
    const std::uint64_t frozen_ts = t;
    AegisAdasOutput out{};
    for (int k = 1; k <= 16; ++k) {
        AegisAdasInput in = nominal(t + 10u * static_cast<std::uint64_t>(k), kV, true, 10.0, -10.0);
        in.meas_ts_ms = frozen_ts;  // sensor timestamp no longer advances
        out = ecu.step(in);
        if (k <= 15) EXPECT_EQ(out.state, AEGIS_ADAS_BRAKING);  // age <= 150 ms
    }
    EXPECT_EQ(out.state, AEGIS_ADAS_DEGRADED);  // age 160 ms
    EXPECT_EQ(out.brake_request_active, 0);
    codec::BrakeRequest r;
    EXPECT_EQ(codec::decode_brake_request(out.brake_req_frame, 10.0, r), AEGIS_REJ_NONE);
    EXPECT_FALSE(r.active);
}

// TEST-ID: UT-ADAS-011 | VERIFIES: ADAS-REQ-009
TEST(AdasSafety, ImplausibleAndNonFiniteInputs) {
    struct Case { double range, rate, ego; std::uint32_t flag; };
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const Case cases[] = {{-1.0, -1.0, kV, AEGIS_DTC_IMPLAUSIBLE_INPUT}, {201.0, -1.0, kV, AEGIS_DTC_IMPLAUSIBLE_INPUT},
                          {50.0, -81.0, kV, AEGIS_DTC_IMPLAUSIBLE_INPUT}, {50.0, -1.0, 71.0, AEGIS_DTC_IMPLAUSIBLE_INPUT},
                          {nan, -1.0, kV, AEGIS_DTC_NONFINITE_INPUT}, {50.0, -1.0, nan, AEGIS_DTC_NONFINITE_INPUT}};
    for (const Case& c : cases) {
        std::uint64_t t = 0;
        AdasEcu ecu = monitoring_ecu(t);
        auto out = ecu.step(nominal(t, c.ego, true, c.range, c.rate));
        EXPECT_EQ(out.state, AEGIS_ADAS_DEGRADED);
        EXPECT_TRUE((out.dtc_flags & c.flag) != 0);
    }
    std::uint64_t t = 0;
    AdasEcu ecu = monitoring_ecu(t);
    AegisAdasInput in = nominal(t, kV, false);
    in.sensor_ok = 0;
    EXPECT_EQ(ecu.step(in).state, AEGIS_ADAS_DEGRADED);
    in = nominal(t + 10, kV, false);
    in.meas_ts_ms = t + 20;  // timestamp from the future
    EXPECT_TRUE((ecu.step(in).dtc_flags & AEGIS_DTC_IMPLAUSIBLE_INPUT) != 0);
}

// TEST-ID: UT-ADAS-012 | VERIFIES: ADAS-REQ-010
TEST(AdasSafety, PersistentDegradationLeadsToFaultUntilReinit) {
    std::uint64_t t = 0;
    AdasEcu ecu = monitoring_ecu(t);
    AegisAdasInput bad = nominal(t, kV, false);
    bad.sensor_ok = 0;
    const std::uint64_t t0 = t;
    AegisAdasOutput out{};
    for (; t < t0 + 1000; t += 10) { bad.now_ms = bad.ego_speed_ts_ms = bad.meas_ts_ms = t; out = ecu.step(bad); }
    EXPECT_EQ(out.state, AEGIS_ADAS_DEGRADED);
    bad.now_ms = bad.ego_speed_ts_ms = bad.meas_ts_ms = t;
    out = ecu.step(bad);
    EXPECT_EQ(out.state, AEGIS_ADAS_FAULT);
    EXPECT_TRUE((out.dtc_flags & AEGIS_DTC_PERSISTENT_DEGRADED) != 0);
    for (int k = 0; k < 50; ++k) { t += 10; out = ecu.step(nominal(t, kV, false)); }
    EXPECT_EQ(out.state, AEGIS_ADAS_FAULT);  // good inputs do not clear FAULT
    AegisAdasInput off = nominal(t, kV, false);
    off.function_enabled = 0;
    EXPECT_EQ(ecu.step(off).state, AEGIS_ADAS_DISABLED);
    EXPECT_EQ(ecu.step(nominal(t + 10, kV, false)).state, AEGIS_ADAS_MONITORING);
}

// TEST-ID: UT-ADAS-013 | VERIFIES: ADAS-REQ-011
TEST(AdasSafety, RecoveryRequiresConsecutiveValidCycles) {
    std::uint64_t t = 0;
    AdasEcu ecu = monitoring_ecu(t);
    AegisAdasInput bad = nominal(t, kV, false);
    bad.sensor_ok = 0;
    EXPECT_EQ(ecu.step(bad).state, AEGIS_ADAS_DEGRADED);
    for (int k = 1; k <= 9; ++k) EXPECT_EQ(ecu.step(nominal(t + 10u * static_cast<std::uint64_t>(k), kV, false)).state, AEGIS_ADAS_DEGRADED);
    // 10th consecutive valid cycle: leaves DEGRADED via STANDBY and re-activates in the same cycle.
    EXPECT_EQ(ecu.step(nominal(t + 100, kV, false)).state, AEGIS_ADAS_MONITORING);
}

// TEST-ID: UT-ADAS-014 | VERIFIES: ADAS-REQ-007
TEST(AdasStateMachine, TransitionTableAndIllegalTransitions) {
    // Expected table, independently written from docs/05_vertical_slice_design.md
    const char* expected[7] = {"0100000", "1010011", "1101111", "1110111", "1110011", "1100001", "1000000"};
    int allowed = 0;
    for (int f = 0; f < 7; ++f)
        for (int to = 0; to < 7; ++to) {
            const bool a = AdasEcu::transition_allowed(static_cast<AdasState>(f), static_cast<AdasState>(to));
            EXPECT_EQ(a, expected[f][to] == '1');
            allowed += a ? 1 : 0;
        }
    EXPECT_EQ(allowed, 26);
    AdasEcu ecu(default_adas_config());
    EXPECT_FALSE(ecu.request_transition(AdasState::Braking));  // DISABLED -> BRAKING
    EXPECT_TRUE(ecu.request_transition(AdasState::Standby));
    EXPECT_FALSE(ecu.request_transition(AdasState::Braking));  // STANDBY -> BRAKING
    EXPECT_FALSE(ecu.request_transition(AdasState::Warning));  // STANDBY -> WARNING
    EXPECT_EQ(ecu.state(), AdasState::Standby);
    auto out = ecu.step(nominal(0, 1.0, false));
    EXPECT_EQ(out.illegal_transition_count, 3u);
    EXPECT_TRUE((out.dtc_flags & AEGIS_DTC_ILLEGAL_TRANSITION) != 0);
}

// TEST-ID: UT-ADAS-015 | VERIFIES: ADAS-REQ-012
TEST(AdasSafety, InvalidConfigurationForcesPermanentFault) {
    AegisAdasConfig cfg = default_adas_config();
    cfg.ttc_brake_s = 3.0;  // brake threshold above warning threshold: invalid
    EXPECT_FALSE(adas_config_valid(cfg));
    AdasEcu ecu(cfg);
    auto out = ecu.step(nominal(0, kV, true, 5.0, -10.0));
    EXPECT_EQ(out.state, AEGIS_ADAS_FAULT);
    EXPECT_EQ(out.brake_request_active, 0);
    EXPECT_TRUE((out.dtc_flags & AEGIS_DTC_INVALID_CONFIG) != 0);
    AegisAdasInput off = nominal(10, kV, false);
    off.function_enabled = 0;
    EXPECT_EQ(ecu.step(off).state, AEGIS_ADAS_FAULT);
    EXPECT_TRUE(adas_config_valid(default_adas_config()));
}

// TEST-ID: UT-ADAS-016 | VERIFIES: ADAS-REQ-008
TEST(AdasComms, FramesEncodeOutputsWithIncrementingCounters) {
    AdasEcu ecu(default_adas_config());
    std::uint8_t last = 0xFF;
    for (int k = 0; k < 20; ++k) {
        auto out = ecu.step(nominal(static_cast<std::uint64_t>(k) * 10u, kV, false));
        const std::uint8_t c = out.brake_req_frame[1] & 0x0F;
        if (last != 0xFF) EXPECT_EQ(c, static_cast<std::uint8_t>((last + 1) & 0x0F));
        last = c;
        EXPECT_EQ(e2e::frame_crc(AEGIS_CAN_ID_BRAKE_REQ, out.brake_req_frame), out.brake_req_frame[0]);
        EXPECT_EQ(e2e::frame_crc(AEGIS_CAN_ID_ADAS_STATUS, out.adas_status_frame), out.adas_status_frame[0]);
        codec::AdasStatus st;
        EXPECT_TRUE(codec::decode_adas_status(out.adas_status_frame, st));
        EXPECT_EQ(st.state, out.state);
    }
}

// TEST-ID: UT-ADAS-017 | VERIFIES: ADAS-REQ-009, TSR-001
TEST(AdasSafety, EgoSpeedValidityAndFreshness) {
    // Added in v0.1.0 after gcov showed these supervisor branches were never executed.
    struct Case { std::uint8_t valid; std::int64_t ts_offset_ms; std::uint32_t flag; AdasState expect; };
    const Case cases[] = {
        {0, 0, AEGIS_DTC_EGO_SPEED_INVALID, AdasState::Degraded},
        {1, +10, AEGIS_DTC_IMPLAUSIBLE_INPUT, AdasState::Degraded},   // timestamp from the future
        {1, -151, AEGIS_DTC_STALE_INPUT, AdasState::Degraded},
        {1, -150, 0u, AdasState::Monitoring},                         // boundary: still fresh
    };
    for (const Case& c : cases) {
        std::uint64_t t = 1000;
        AdasEcu ecu = monitoring_ecu(t);
        AegisAdasInput in = nominal(t, kV, false);
        in.ego_speed_valid = c.valid;
        in.ego_speed_ts_ms = static_cast<std::uint64_t>(static_cast<std::int64_t>(t) + c.ts_offset_ms);
        auto out = ecu.step(in);
        EXPECT_EQ(out.state, static_cast<std::uint8_t>(c.expect));
        if (c.flag != 0u) EXPECT_TRUE((out.dtc_flags & c.flag) != 0);
        else EXPECT_EQ(out.dtc_flags, 0u);
    }
}

// TEST-ID: UT-V2-001 | VERIFIES: TSR-201, FSR-201
TEST(AdasAssurance, StoppingEnvelopeAndConfiguration) {
    AdasEcu ecu(default_adas_config());
    auto out = ecu.step(nominal(0, 20.0, true, 57.0, -20.0));
    EXPECT_EQ(out.state, AEGIS_ADAS_BRAKING); // TTC 2.85, envelope 59 m
    AdasEcu clear(default_adas_config());
    EXPECT_EQ(clear.step(nominal(0, 20.0, true, 60.0, -20.0)).state, AEGIS_ADAS_MONITORING);
    auto cfg = default_adas_config();
    for (double invalid : {-1.0, 11.0, std::numeric_limits<double>::infinity()}) {
        cfg.planning_decel_mps2 = invalid;
        EXPECT_FALSE(adas_config_valid(cfg));
    }
}

// TEST-ID: UT-V2-002 | VERIFIES: TSR-202, FSR-202
TEST(AdasAssurance, OpeningInsideStoppingEnvelopeDoesNotRelease) {
    AdasEcu ecu(default_adas_config());
    ecu.step(nominal(0, 15.0, true, 10.0, -10.0));
    for (std::uint64_t t = 10; t <= 1000; t += 10) {
        EXPECT_EQ(ecu.step(nominal(t, 15.0, true, 5.0, 1.0)).state, AEGIS_ADAS_BRAKING);
    }
}

// TEST-ID: UT-V2-003 | VERIFIES: TSR-203, FSR-203
TEST(AdasAssurance, MissingFeedbackBoundaryAndDisableReset) {
    AdasEcu ecu(default_adas_config());
    auto in = nominal(0, kV, false);
    in.feedback_monitor_enabled = 1;
    EXPECT_EQ(ecu.step(in).dtc_flags & AEGIS_DTC_BRAKE_FEEDBACK, 0u);
    in.now_ms = in.meas_ts_ms = in.ego_speed_ts_ms = 100;
    EXPECT_EQ(ecu.step(in).dtc_flags & AEGIS_DTC_BRAKE_FEEDBACK, 0u);
    in.now_ms = in.meas_ts_ms = in.ego_speed_ts_ms = 101;
    auto out = ecu.step(in);
    EXPECT_TRUE((out.dtc_flags & AEGIS_DTC_BRAKE_FEEDBACK) != 0);
    EXPECT_EQ(out.function_unavailable, 1);
    EXPECT_EQ(out.brake_request_active, 0); // no blind intervention
    in.function_enabled = 0;
    EXPECT_EQ(ecu.step(in).dtc_flags & AEGIS_DTC_BRAKE_FEEDBACK, 0u);
}

// TEST-ID: UT-V2-004 | VERIFIES: TSR-203, FSR-203
TEST(AdasAssurance, FrozenAcknowledgmentAndCorruptionCannotMaskFault) {
    for (bool corrupt : {false, true}) {
        AdasEcu ecu(default_adas_config());
        AegisAdasOutput out{};
        for (std::uint64_t t = 0; t <= 200; t += 10) {
            auto in = nominal(t, kV, false);
            in.feedback_monitor_enabled = in.brake_status_present = 1;
            in.brake_status_dlc = 8;
            codec::BrakeStatus st; st.ack_valid = true; st.ack_counter = 1;
            codec::encode_brake_status(st, static_cast<std::uint8_t>((t/10)%16), in.brake_status_frame);
            if (corrupt) in.brake_status_frame[0] ^= 1;
            out = ecu.step(in);
        }
        EXPECT_TRUE((out.dtc_flags & AEGIS_DTC_BRAKE_FEEDBACK) != 0);
    }
}

// TEST-ID: UT-V2-005 | VERIFIES: TSR-203, FSR-203
TEST(AdasAssurance, ActuationMismatchAndNormalAcknowledgment) {
    for (bool active : {false, true}) {
        AdasEcu ecu(default_adas_config());
        AegisAdasOutput out{};
        for (std::uint64_t t = 0; t <= 400; t += 10) {
            auto in = nominal(t, kV, true, 10.0, -10.0);
            in.feedback_monitor_enabled = in.brake_status_present = 1;
            in.brake_status_dlc = 8;
            codec::BrakeStatus st; st.ack_valid = true;
            st.ack_counter = static_cast<std::uint8_t>((t/10)%16);
            st.active = active; st.actual_decel_mps2 = active ? 4.0 : 0.0;
            codec::encode_brake_status(st, st.ack_counter, in.brake_status_frame);
            out = ecu.step(in);
        }
        EXPECT_EQ((out.dtc_flags & AEGIS_DTC_BRAKE_FEEDBACK) != 0, !active);
        EXPECT_EQ(out.brake_request_active, 1); // valid threat still commands despite feedback failure
    }
}

// TEST-ID: UT-V3-003 | VERIFIES: ADAS-REQ-004
TEST(AdasAssurance, WarningCannotInitiateBrakingOutsideWindow) {
    for (double outside : {2.0, 23.0}) {
        AdasEcu ecu(default_adas_config());
        auto in = nominal(0, 13.9, true, 30.0, -12.0);
        // Isolate warning with safe stopping envelope.
        in.range_m = 35.0; in.range_rate_mps = -14.0;
        auto cfg = default_adas_config(); cfg.planning_decel_mps2 = 0;
        AdasEcu isolated(cfg);
        EXPECT_EQ(isolated.step(in).state, AEGIS_ADAS_WARNING);
        EXPECT_EQ(isolated.step(nominal(10, outside, true, 5.0, -10.0)).state, AEGIS_ADAS_STANDBY);
    }
}

// TEST-ID: UT-V3-007 | VERIFIES: DIA-301
TEST(AdasAssurance, AchievedDecelCannotBeReplacedByAcknowledgment) {
    for (bool adequate : {false, true}) {
        AdasEcu ecu(default_adas_config());
        AegisAdasOutput out{};
        for (std::uint64_t t=0;t<=800;t+=10) {
            auto in=nominal(t,13.9,true,10,-10);
            in.achieved_monitor_enabled=1; in.achieved_valid=1;
            in.achieved_ts_ms=t; in.achieved_decel_mps2=adequate?4.0:0.0;
            out=ecu.step(in);
        }
        EXPECT_EQ((out.dtc_flags & AEGIS_DTC_ACHIEVED_DECEL)!=0,!adequate);
        EXPECT_EQ(out.dtc_flags & AEGIS_DTC_BRAKE_FEEDBACK,0u); // independent monitor enable
        EXPECT_EQ(out.brake_request_active,1);
    }
}

// TEST-ID: UT-V3-008 | VERIFIES: DIA-301
TEST(AdasAssurance, AchievedInputValidationIndependentConditions) {
    struct Case {std::uint8_t valid; double decel; std::uint64_t ts;};
    const Case cases[]={{0,4.,1000},{1,-1.,1000},{1,16.,1000},
      {1,std::numeric_limits<double>::quiet_NaN(),1000},{1,4.,1001},{1,4.,899},{1,4.,900}};
    for (unsigned i=0;i<7;++i) {
        AdasEcu ecu(default_adas_config());auto in=nominal(1000,13.9,false);
        in.achieved_monitor_enabled=1;in.achieved_valid=cases[i].valid;
        in.achieved_decel_mps2=cases[i].decel;in.achieved_ts_ms=cases[i].ts;
        EXPECT_EQ((ecu.step(in).dtc_flags&AEGIS_DTC_ACHIEVED_DECEL)!=0,i<6);
    }
}

// TEST-ID: UT-V3-010 | VERIFIES: ADAS-REQ-012
TEST(AdasAssurance, ConfigurationIndependentInvalidParameters) {
    // Every case changes one safety parameter from the valid default.
    using Member=double AegisAdasConfig::*;
    const Member finite_positive[]={&AegisAdasConfig::min_closing_speed_mps,
      &AegisAdasConfig::decel_gain,&AegisAdasConfig::min_brake_decel_mps2,
      &AegisAdasConfig::emergency_decel_mps2,&AegisAdasConfig::max_range_m,
      &AegisAdasConfig::max_abs_range_rate_mps,&AegisAdasConfig::max_ego_speed_mps};
    for(auto member:finite_positive) for(double invalid:{0.,-1.,std::numeric_limits<double>::infinity()}) {
        auto cfg=default_adas_config();cfg.*member=invalid;
        EXPECT_FALSE(adas_config_valid(cfg));
    }
    for(auto member:{&AegisAdasConfig::ttc_warning_s,&AegisAdasConfig::ttc_brake_s,
       &AegisAdasConfig::ttc_hysteresis_s,&AegisAdasConfig::stop_margin_m,
       &AegisAdasConfig::min_active_speed_mps,&AegisAdasConfig::standstill_speed_mps,
       &AegisAdasConfig::max_active_speed_mps,&AegisAdasConfig::max_brake_decel_mps2}) {
        auto cfg=default_adas_config();cfg.*member=std::numeric_limits<double>::quiet_NaN();
        EXPECT_FALSE(adas_config_valid(cfg));
    }
    for (unsigned i=0;i<12;++i) {
        auto cfg=default_adas_config();
        switch(i) {
            case 0:cfg.ttc_hysteresis_s=-1;break;
            case 1:cfg.stop_margin_m=-1;break;
            case 2:cfg.min_brake_decel_mps2=9.5;break;
            case 3:cfg.emergency_decel_mps2=9.5;break;
            case 4:cfg.min_active_speed_mps=-1;break;
            case 5:cfg.min_active_speed_mps=cfg.max_active_speed_mps;break;
            case 6:cfg.max_active_speed_mps=71;break;
            case 7:cfg.standstill_speed_mps=-1;break;
            case 8:cfg.standstill_speed_mps=cfg.min_active_speed_mps;break;
            case 9:cfg.stale_timeout_ms=0;break;
            case 10:cfg.recovery_cycles=0;break;
            default:cfg.degraded_to_fault_ms=0;break;
        }
        EXPECT_FALSE(adas_config_valid(cfg));
    }
}

// TEST-ID: SEC-CPP-001 | VERIFIES: SEC-404
TEST(AdasAssurance, SecurityDiagnosticDoesNotInitiateBlindBrake) {
    AdasEcu ecu(default_adas_config());auto in=nominal(0,13.9,false);
    in.security_event=1;
    auto out=ecu.step(in);
    EXPECT_TRUE((out.dtc_flags&AEGIS_DTC_SECURITY_EVENT)!=0);
    EXPECT_EQ(out.brake_request_active,0);
    EXPECT_EQ(out.function_unavailable,0); // alert is not a declaration of lost actuation
    in.security_event=0;in.now_ms=in.meas_ts_ms=in.ego_speed_ts_ms=10;
    EXPECT_TRUE((ecu.step(in).dtc_flags&AEGIS_DTC_SECURITY_EVENT)!=0);
    in.function_enabled=0;
    EXPECT_EQ(ecu.step(in).dtc_flags&AEGIS_DTC_SECURITY_EVENT,0u);
}
