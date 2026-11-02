#include "gtest/gtest.h"
#include "aegis/body_ecu.hpp"
#include "aegis/codec.hpp"

using namespace aegis;

namespace {
struct Bus {
    std::uint8_t bc = 0, ac = 0;
    AegisBodyInput make(std::uint64_t now, bool brake_active, std::uint8_t adas_state, bool warning,
                        bool emergency = false, bool unavailable = false) {
        AegisBodyInput in{};
        in.now_ms = now;
        in.brake_status_present = 1;
        in.brake_status_dlc = 8;
        codec::encode_brake_status({brake_active, false, false, brake_active ? 5.0 : 0.0}, bc, in.brake_status_frame);
        in.adas_status_present = 1;
        in.adas_status_dlc = 8;
        codec::encode_adas_status({adas_state, warning, unavailable, emergency, false}, ac, in.adas_status_frame);
        bc = static_cast<std::uint8_t>((bc + 1) & 0x0F);
        ac = static_cast<std::uint8_t>((ac + 1) & 0x0F);
        return in;
    }
};
}  // namespace

// TEST-ID: UT-BCM-001 | VERIFIES: BCM-REQ-001
TEST(BodyEcu, BrakeLampSameCycleAsValidStatus) {
    BodyEcu ecu(default_body_config());
    Bus bus;
    EXPECT_EQ(ecu.step(bus.make(0, false, AEGIS_ADAS_MONITORING, false)).brake_lamp, 0);  // sync
    EXPECT_EQ(ecu.step(bus.make(10, false, AEGIS_ADAS_MONITORING, false)).brake_lamp, 0);
    EXPECT_EQ(ecu.step(bus.make(20, true, AEGIS_ADAS_BRAKING, true)).brake_lamp, 1);
    EXPECT_EQ(ecu.step(bus.make(30, false, AEGIS_ADAS_MONITORING, false)).brake_lamp, 0);
}

// TEST-ID: UT-BCM-002 | VERIFIES: BCM-REQ-002
TEST(BodyEcu, WarningIndicatorFollowsAdasWarning) {
    BodyEcu ecu(default_body_config());
    Bus bus;
    ecu.step(bus.make(0, false, AEGIS_ADAS_MONITORING, false));
    EXPECT_EQ(ecu.step(bus.make(10, false, AEGIS_ADAS_WARNING, true)).warning_indicator, 1);
    EXPECT_EQ(ecu.step(bus.make(20, false, AEGIS_ADAS_MONITORING, false)).warning_indicator, 0);
    auto out = ecu.step(bus.make(30, false, AEGIS_ADAS_DEGRADED, false, false, true));
    EXPECT_EQ(out.aeb_unavailable_indicator, 1);
}

// TEST-ID: UT-BCM-003 | VERIFIES: BCM-REQ-003
TEST(BodyEcu, HazardPolicyForEmergencyBraking) {
    BodyEcu ecu(default_body_config());
    Bus bus;
    ecu.step(bus.make(0, false, AEGIS_ADAS_MONITORING, false));
    EXPECT_EQ(ecu.step(bus.make(10, true, AEGIS_ADAS_BRAKING, true, false)).hazard_lamps, 0);  // non-emergency
    EXPECT_EQ(ecu.step(bus.make(20, true, AEGIS_ADAS_BRAKING, true, true)).hazard_lamps, 1);
    EXPECT_EQ(ecu.step(bus.make(30, false, AEGIS_ADAS_STANDBY, false)).hazard_lamps, 1);
    EXPECT_EQ(ecu.step(bus.make(3010, false, AEGIS_ADAS_STANDBY, false)).hazard_lamps, 1);  // 2990 ms after
    EXPECT_EQ(ecu.step(bus.make(3020, false, AEGIS_ADAS_STANDBY, false)).hazard_lamps, 0);
}

// TEST-ID: UT-BCM-004 | VERIFIES: BCM-REQ-004
TEST(BodyEcu, InputTimeoutsAreReported) {
    BodyEcu ecu(default_body_config());
    Bus bus;
    auto out = ecu.step(AegisBodyInput{});
    EXPECT_EQ(out.fault_brake_status_timeout, 1);
    EXPECT_EQ(out.aeb_unavailable_indicator, 1);
    ecu.step(bus.make(0, true, AEGIS_ADAS_BRAKING, true));
    ecu.step(bus.make(10, true, AEGIS_ADAS_BRAKING, true));
    AegisBodyInput silent{};
    silent.now_ms = 110;
    out = ecu.step(silent);
    EXPECT_EQ(out.fault_brake_status_timeout, 0);
    silent.now_ms = 111;
    out = ecu.step(silent);
    EXPECT_EQ(out.fault_brake_status_timeout, 1);
    EXPECT_EQ(out.fault_adas_status_timeout, 1);
    EXPECT_EQ(out.brake_lamp, 1);  // retained last valid state (documented, provisional policy)
    EXPECT_EQ(out.warning_indicator, 0);
    EXPECT_EQ(out.aeb_unavailable_indicator, 1);
}

// TEST-ID: UT-BCM-005 | VERIFIES: BCM-REQ-004
TEST(BodyEcu, CorruptedFramesAreRejected) {
    BodyEcu ecu(default_body_config());
    Bus bus;
    ecu.step(bus.make(0, false, AEGIS_ADAS_MONITORING, false));
    ecu.step(bus.make(10, false, AEGIS_ADAS_MONITORING, false));
    AegisBodyInput in = bus.make(20, true, AEGIS_ADAS_MONITORING, false);
    in.brake_status_frame[2] ^= 0x01;  // flip "active" bit without fixing CRC
    auto out = ecu.step(in);
    EXPECT_EQ(out.brake_lamp, 0);
    EXPECT_EQ(out.rejected_frames, 1u);
    in = bus.make(30, false, AEGIS_ADAS_WARNING, true);
    in.adas_status_frame[3] ^= 0x01;  // corrupt ADAS_STATUS warning flag
    out = ecu.step(in);
    EXPECT_EQ(out.warning_indicator, 0);
    EXPECT_EQ(out.rejected_frames, 2u);
}
