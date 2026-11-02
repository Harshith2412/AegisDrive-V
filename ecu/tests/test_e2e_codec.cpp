#include <cstring>
#include "gtest/gtest.h"
#include "aegis/aegis_types.h"
#include "aegis/codec.hpp"
#include "aegis/e2e.hpp"

using namespace aegis;

// TEST-ID: UT-E2E-001 | VERIFIES: SWR-002
TEST(E2E, Crc8J1850CheckValue) {
    const std::uint8_t msg[] = {'1', '2', '3', '4', '5', '6', '7', '8', '9'};
    EXPECT_EQ(e2e::crc8_j1850(msg, sizeof(msg)), 0x4B);  // published check value for CRC-8/SAE-J1850
}

// TEST-ID: UT-E2E-002 | VERIFIES: TSR-002
TEST(E2E, EverySingleBitFlipIsDetected) {
    std::uint8_t f[8];
    codec::encode_brake_request({true, true, 7.25}, 3, f);
    e2e::Receiver probe(2);
    int detected = 0;
    for (int byte = 0; byte < 8; ++byte) {
        for (int bit = 0; bit < 8; ++bit) {
            std::uint8_t g[8];
            std::memcpy(g, f, 8);
            g[byte] = static_cast<std::uint8_t>(g[byte] ^ (1u << bit));
            if (e2e::frame_crc(AEGIS_CAN_ID_BRAKE_REQ, g) != g[0]) ++detected;
        }
    }
    EXPECT_EQ(detected, 64);
}

// TEST-ID: UT-E2E-003 | VERIFIES: TSR-002
TEST(E2E, CounterSequenceChecks) {
    e2e::Receiver rx(2);
    std::uint8_t f[8];
    codec::encode_brake_request({}, 5, f);
    EXPECT_EQ(rx.check(AEGIS_CAN_ID_BRAKE_REQ, f), e2e::Check::InitialSync);
    EXPECT_EQ(rx.check(AEGIS_CAN_ID_BRAKE_REQ, f), e2e::Check::Repeated);
    codec::encode_brake_request({}, 6, f);
    EXPECT_EQ(rx.check(AEGIS_CAN_ID_BRAKE_REQ, f), e2e::Check::Ok);
    codec::encode_brake_request({}, 8, f);  // one frame lost: tolerated
    EXPECT_EQ(rx.check(AEGIS_CAN_ID_BRAKE_REQ, f), e2e::Check::Ok);
    codec::encode_brake_request({}, 11, f);  // delta 3
    EXPECT_EQ(rx.check(AEGIS_CAN_ID_BRAKE_REQ, f), e2e::Check::WrongSequence);
    codec::encode_brake_request({}, 12, f);  // re-synchronised
    EXPECT_EQ(rx.check(AEGIS_CAN_ID_BRAKE_REQ, f), e2e::Check::Ok);
    codec::encode_brake_request({}, 13, f);
    EXPECT_EQ(rx.check(AEGIS_CAN_ID_ADAS_STATUS, f), e2e::Check::CrcError);  // wrong DataID
}

// TEST-ID: UT-E2E-004 | VERIFIES: ADAS-REQ-008, BRK-REQ-001
TEST(Codec, BrakeRequestRoundTrip) {
    std::uint8_t f[8];
    codec::encode_brake_request({true, false, 4.286}, 1, f);
    codec::BrakeRequest r;
    EXPECT_EQ(codec::decode_brake_request(f, 10.0, r), AEGIS_REJ_NONE);
    EXPECT_TRUE(r.active);
    EXPECT_NEAR(r.decel_mps2, 4.29, 1e-9);  // 0.01 m/s^2 resolution
}

// TEST-ID: UT-E2E-005 | VERIFIES: BRK-REQ-001
TEST(Codec, BrakeRequestPayloadRejections) {
    std::uint8_t f[8];
    codec::BrakeRequest r;
    codec::encode_brake_request({true, false, 10.5}, 1, f);
    EXPECT_EQ(codec::decode_brake_request(f, 10.0, r), AEGIS_REJ_RANGE);
    codec::encode_brake_request({true, false, 5.0}, 1, f);
    f[6] = 0x01;
    EXPECT_EQ(codec::decode_brake_request(f, 10.0, r), AEGIS_REJ_RESERVED_BITS);
    codec::encode_brake_request({false, false, 0.0}, 1, f);
    f[3] = 0x10;  // inactive request with non-zero decel
    EXPECT_EQ(codec::decode_brake_request(f, 10.0, r), AEGIS_REJ_INCONSISTENT);
    codec::encode_brake_request({false, false, 0.0}, 1, f);
    f[2] = 0x01;  // active request with zero decel
    EXPECT_EQ(codec::decode_brake_request(f, 10.0, r), AEGIS_REJ_INCONSISTENT);
}
