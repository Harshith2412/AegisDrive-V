// AegisDrive-V — CAN payload codecs for the vertical slice (DLC 8, classic CAN).
// See docs/05_vertical_slice_design.md for the bit-level layout.
#pragma once
#include <cstdint>

namespace aegis::codec {

constexpr double kDecelResolution = 0.01;  // m/s^2 per bit (uint16 little-endian)

struct BrakeRequest {
    bool active = false;
    bool emergency = false;
    double decel_mps2 = 0.0;
};
struct AdasStatus {
    std::uint8_t state = 0;
    bool warning = false;
    bool unavailable = false;
    bool emergency = false;
    bool standstill = false;
};
struct BrakeStatus {
    bool active = false;
    bool timeout = false;
    bool rejecting = false;
    double actual_decel_mps2 = 0.0;
    bool ack_valid = false;
    std::uint8_t ack_counter = 0;
};

void encode_brake_request(const BrakeRequest& m, std::uint8_t counter, std::uint8_t* f8);
// Payload validation after E2E checks; returns AEGIS_REJ_* code.
std::uint8_t decode_brake_request(const std::uint8_t* f8, double max_decel_mps2, BrakeRequest& out);

void encode_adas_status(const AdasStatus& m, std::uint8_t counter, std::uint8_t* f8);
bool decode_adas_status(const std::uint8_t* f8, AdasStatus& out);

void encode_brake_status(const BrakeStatus& m, std::uint8_t counter, std::uint8_t* f8);
bool decode_brake_status(const std::uint8_t* f8, BrakeStatus& out);

}  // namespace aegis::codec
