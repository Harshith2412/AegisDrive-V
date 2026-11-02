#include <cmath>
#include <cstring>
#include <limits>
#include "gtest/gtest.h"
#include "aegis/brake_ecu.hpp"
#include "aegis/codec.hpp"
#include "aegis/e2e.hpp"

using namespace aegis;

namespace {
struct Tx {
    std::uint8_t counter = 0;
    AegisBrakeInput frame(std::uint64_t now, bool active, double decel) {
        AegisBrakeInput in{};
        in.now_ms = now;
        in.dt_s = 0.01;
        in.can_id = AEGIS_CAN_ID_BRAKE_REQ;
        in.frame_present = 1;
        in.frame_dlc = 8;
        codec::encode_brake_request({active, decel >= 6.0, decel}, counter, in.frame);
        counter = static_cast<std::uint8_t>((counter + 1) & 0x0F);
        return in;
    }
};
AegisBrakeInput none(std::uint64_t now) {
    AegisBrakeInput in{};
    in.now_ms = now;
    in.dt_s = 0.01;
    return in;
}
}  // namespace

// TEST-ID: UT-BRK-001 | VERIFIES: BRK-REQ-001
TEST(BrakeEcu, InitialSyncFrameIsNotActedUpon) {
    BrakeEcu ecu(default_brake_config());
    Tx tx;
    auto out = ecu.step(tx.frame(0, true, 5.0));
    EXPECT_EQ(out.frame_accepted, 0);
    EXPECT_NEAR(out.aeb_target_decel_mps2, 0.0, 0.0);
    EXPECT_EQ(out.status, AEGIS_BRK_STATUS_NO_SYNC);
    out = ecu.step(tx.frame(10, true, 5.0));
    EXPECT_EQ(out.frame_accepted, 1);
    EXPECT_NEAR(out.aeb_target_decel_mps2, 5.0, 1e-9);
    EXPECT_EQ(out.status, AEGIS_BRK_STATUS_OK);
}

// TEST-ID: UT-BRK-002 | VERIFIES: BRK-REQ-001
TEST(BrakeEcu, RejectsInvalidCommandFrames) {
    BrakeEcu ecu(default_brake_config());
    Tx tx;
    ecu.step(tx.frame(0, false, 0.0));
    ecu.step(tx.frame(10, true, 3.0));
    std::uint64_t t = 20;
    // wrong id
    AegisBrakeInput in = tx.frame(t, true, 9.0);
    in.can_id = 0x121;
    auto out = ecu.step(in);
    EXPECT_EQ(out.last_reject_reason, AEGIS_REJ_WRONG_ID);
    // Frames rejected before the E2E check do not advance the receiver's counter
    // state, so the test sender re-uses the counter value (see CHANGELOG 0.1.0).
    tx.counter = static_cast<std::uint8_t>((tx.counter + 15) & 0x0F);
    // bad dlc
    in = tx.frame(t += 10, true, 9.0);
    in.frame_dlc = 7;
    EXPECT_EQ(ecu.step(in).last_reject_reason, AEGIS_REJ_BAD_DLC);
    tx.counter = static_cast<std::uint8_t>((tx.counter + 15) & 0x0F);
    // corrupted payload
    in = tx.frame(t += 10, true, 9.0);
    in.frame[3] ^= 0x01;
    EXPECT_EQ(ecu.step(in).last_reject_reason, AEGIS_REJ_CRC);
    tx.counter = static_cast<std::uint8_t>((tx.counter + 15) & 0x0F);
    // out-of-range (valid CRC + counter, decel 10.5 m/s^2)
    in = tx.frame(t += 10, true, 10.5);
    EXPECT_EQ(ecu.step(in).last_reject_reason, AEGIS_REJ_RANGE);
    // repeated frame (same counter as previous accepted-by-E2E frame)
    AegisBrakeInput rep = in;
    rep.now_ms = (t += 10);
    EXPECT_EQ(ecu.step(rep).last_reject_reason, AEGIS_REJ_REPEATED);
    out = ecu.step(none(t += 10));
    EXPECT_NEAR(out.aeb_target_decel_mps2, 3.0, 1e-9);  // last valid command still applies
    EXPECT_EQ(out.rejected_frames, 5u);
    EXPECT_EQ(out.accepted_frames, 1u);
}

// TEST-ID: UT-BRK-003 | VERIFIES: BRK-REQ-002, TSR-003
TEST(BrakeEcu, CommandTimeoutReleasesAebDemand) {
    BrakeEcu ecu(default_brake_config());
    Tx tx;
    ecu.step(tx.frame(0, true, 6.0));
    ecu.step(tx.frame(10, true, 6.0));  // last valid at 10 ms
    auto out = ecu.step(none(110));     // 100 ms since last valid
    EXPECT_NEAR(out.aeb_target_decel_mps2, 6.0, 1e-9);
    out = ecu.step(none(111));
    EXPECT_NEAR(out.aeb_target_decel_mps2, 0.0, 0.0);
    EXPECT_EQ(out.status, AEGIS_BRK_STATUS_TIMEOUT);
}

// TEST-ID: UT-BRK-004 | VERIFIES: BRK-REQ-003
TEST(BrakeEcu, ArbitrationSelectsHighestDemand) {
    BrakeEcu ecu(default_brake_config());
    Tx tx;
    ecu.step(tx.frame(0, true, 4.0));
    AegisBrakeInput in = tx.frame(10, true, 4.0);
    in.driver_brake_mps2 = 6.5;
    EXPECT_NEAR(ecu.step(in).target_decel_mps2, 6.5, 1e-12);
    in = tx.frame(20, true, 4.0);
    in.driver_brake_mps2 = 2.0;
    EXPECT_NEAR(ecu.step(in).target_decel_mps2, 4.0, 1e-9);
    in = none(30);
    in.driver_brake_mps2 = std::numeric_limits<double>::quiet_NaN();
    EXPECT_NEAR(ecu.step(in).target_decel_mps2, 4.0, 1e-9);  // NaN pedal ignored
}

// TEST-ID: UT-BRK-005 | VERIFIES: BRK-REQ-004
TEST(BrakeEcu, ActuatorFirstOrderResponse) {
    BrakeEcu ecu(default_brake_config());
    Tx tx;
    ecu.step(tx.frame(0, false, 0.0));
    AegisBrakeOutput out{};
    for (int k = 1; k <= 15; ++k) out = ecu.step(tx.frame(static_cast<std::uint64_t>(k) * 10u, true, 5.0));
    // 15 steps * 10 ms = tau = 0.15 s -> 63.2 % of the step
    EXPECT_NEAR(out.actual_decel_mps2, 5.0 * (1.0 - std::exp(-1.0)), 1e-9);
    AegisBrakeInput bad = none(160);
    bad.dt_s = std::numeric_limits<double>::quiet_NaN();
    EXPECT_NEAR(ecu.step(bad).actual_decel_mps2, out.actual_decel_mps2, 0.0);  // invalid dt: hold
}

// TEST-ID: UT-BRK-006 | VERIFIES: BRK-REQ-005
TEST(BrakeEcu, StatusFrameReportsActiveBrake) {
    BrakeEcu ecu(default_brake_config());
    Tx tx;
    ecu.step(tx.frame(0, false, 0.0));
    auto out = ecu.step(tx.frame(10, true, 9.0));
    EXPECT_EQ(out.brake_active, 1);  // 9*(1-exp(-1/15)) = 0.58 >= 0.3
    codec::BrakeStatus st;
    EXPECT_TRUE(codec::decode_brake_status(out.status_frame, st));
    EXPECT_TRUE(st.active);
    EXPECT_NEAR(st.actual_decel_mps2, out.actual_decel_mps2, 0.006);
    EXPECT_EQ(e2e::frame_crc(AEGIS_CAN_ID_BRAKE_STATUS, out.status_frame), out.status_frame[0]);
}

// TEST-ID: UT-BRK-007 | VERIFIES: BRK-REQ-001
TEST(BrakeEcu, ToleratesOneLostFrameButNotMore) {
    BrakeEcu ecu(default_brake_config());
    Tx tx;
    ecu.step(tx.frame(0, true, 4.0));
    ecu.step(tx.frame(10, true, 4.0));
    tx.counter = static_cast<std::uint8_t>((tx.counter + 1) & 0x0F);  // one frame lost
    EXPECT_EQ(ecu.step(tx.frame(20, true, 5.0)).frame_accepted, 1);
    tx.counter = static_cast<std::uint8_t>((tx.counter + 2) & 0x0F);  // two frames lost
    auto out = ecu.step(tx.frame(30, true, 7.0));
    EXPECT_EQ(out.frame_accepted, 0);
    EXPECT_EQ(out.last_reject_reason, AEGIS_REJ_SEQUENCE);
    EXPECT_NEAR(out.aeb_target_decel_mps2, 5.0, 1e-9);
    EXPECT_EQ(ecu.step(tx.frame(40, true, 7.0)).frame_accepted, 1);  // re-synchronised
}

// TEST-ID: UT-V3-009 | VERIFIES: BRK-301
TEST(BrakeEcu, BackupChannelValidatesAndPreservesPrimaryPriority) {
    BrakeEcu ecu(default_brake_config());
    AegisBrakeOutput out{};
    for (std::uint64_t k=0;k<5;++k) {
        AegisBrakeInput in{};in.now_ms=k*10;in.dt_s=.01;
        in.can_id=AEGIS_CAN_ID_BRAKE_REQ;in.frame_present=1;in.frame_dlc=8;
        in.backup_present=1;in.backup_dlc=8;
        codec::encode_brake_request({true,false,4.0},static_cast<std::uint8_t>(k),in.frame);
        codec::encode_brake_request({true,true,8.0},static_cast<std::uint8_t>(k),in.backup_frame);
        if(k>=3)in.frame_present=0;
        out=ecu.step(in);
        if(k==2)EXPECT_NEAR(out.aeb_target_decel_mps2,4.,1e-12);
        if(k>=3)EXPECT_NEAR(out.aeb_target_decel_mps2,8.,1e-12);
    }
    EXPECT_EQ(out.status,AEGIS_BRK_STATUS_OK);
}

// TEST-ID: UT-V3-011 | VERIFIES: BRK-301
TEST(BrakeEcu, BackupCorruptionSequenceAndRangeCannotRefreshDemand) {
    for(unsigned kind=0;kind<4;++kind) {
        BrakeEcu ecu(default_brake_config());
        AegisBrakeInput in{};in.dt_s=.01;in.backup_present=1;in.backup_dlc=8;
        codec::encode_brake_request({true,false,4.0},0,in.backup_frame);
        ecu.step(in);in.now_ms=10;
        codec::encode_brake_request({true,false,4.0},1,in.backup_frame);
        EXPECT_EQ(ecu.step(in).frame_accepted,1);
        in.now_ms=20;
        codec::encode_brake_request({true,false,4.0},2,in.backup_frame);
        if(kind==0)in.backup_frame[0]^=1;
        if(kind==1)in.backup_dlc=7;
        if(kind==2)codec::encode_brake_request({true,true,11.0},2,in.backup_frame);
        if(kind==3)codec::encode_brake_request({true,false,4.0},1,in.backup_frame);
        auto out=ecu.step(in);
        EXPECT_EQ(out.frame_accepted,0);EXPECT_EQ(out.rejected_frames,1u);
        EXPECT_NEAR(out.aeb_target_decel_mps2,4.,1e-12);
        in.backup_present=0;in.now_ms=111;
        EXPECT_NEAR(ecu.step(in).aeb_target_decel_mps2,0.,1e-12);
    }
}
