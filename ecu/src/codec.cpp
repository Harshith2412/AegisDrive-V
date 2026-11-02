#include "aegis/codec.hpp"
#include <cmath>
#include "aegis/aegis_types.h"
#include "aegis/e2e.hpp"

namespace aegis::codec {
namespace {
std::uint16_t to_raw(double decel) {
    if (!(decel > 0.0)) return 0;  // also maps NaN to 0
    const double raw = std::round(decel / kDecelResolution);
    return raw >= 65535.0 ? 65535u : static_cast<std::uint16_t>(raw);
}
void clear(std::uint8_t* f) { for (int i = 0; i < 8; ++i) f[i] = 0; }
std::uint16_t get_u16(const std::uint8_t* f, int i) {
    return static_cast<std::uint16_t>(f[i] | (f[i + 1] << 8));
}
void put_u16(std::uint8_t* f, int i, std::uint16_t v) {
    f[i] = static_cast<std::uint8_t>(v & 0xFFu);
    f[i + 1] = static_cast<std::uint8_t>(v >> 8);
}
}  // namespace

void encode_brake_request(const BrakeRequest& m, std::uint8_t counter, std::uint8_t* f) {
    clear(f);
    f[2] = static_cast<std::uint8_t>((m.active ? 0x01u : 0u) | (m.emergency ? 0x02u : 0u));
    put_u16(f, 3, m.active ? to_raw(m.decel_mps2) : 0u);
    e2e::protect(AEGIS_CAN_ID_BRAKE_REQ, counter, f);
}

std::uint8_t decode_brake_request(const std::uint8_t* f, double max_decel, BrakeRequest& out) {
    if ((f[1] & 0xF0u) || (f[2] & 0xFCu) || f[5] || f[6] || f[7]) return AEGIS_REJ_RESERVED_BITS;
    const bool active = (f[2] & 0x01u) != 0;
    const bool emergency = (f[2] & 0x02u) != 0;
    const std::uint16_t raw = get_u16(f, 3);
    const double decel = raw * kDecelResolution;
    if (decel > max_decel + 1e-9) return AEGIS_REJ_RANGE;
    if (!active && (raw != 0 || emergency)) return AEGIS_REJ_INCONSISTENT;
    if (active && raw == 0) return AEGIS_REJ_INCONSISTENT;
    out.active = active;
    out.emergency = emergency;
    out.decel_mps2 = decel;
    return AEGIS_REJ_NONE;
}

void encode_adas_status(const AdasStatus& m, std::uint8_t counter, std::uint8_t* f) {
    clear(f);
    f[2] = m.state;
    f[3] = static_cast<std::uint8_t>((m.warning ? 0x01u : 0u) | (m.unavailable ? 0x02u : 0u) |
                                     (m.emergency ? 0x04u : 0u) | (m.standstill ? 0x08u : 0u));
    e2e::protect(AEGIS_CAN_ID_ADAS_STATUS, counter, f);
}

bool decode_adas_status(const std::uint8_t* f, AdasStatus& out) {
    if ((f[1] & 0xF0u) || (f[3] & 0xF0u) || f[4] || f[5] || f[6] || f[7]) return false;
    if (f[2] >= AEGIS_ADAS_NUM_STATES) return false;
    out.state = f[2];
    out.warning = f[3] & 0x01u;
    out.unavailable = f[3] & 0x02u;
    out.emergency = f[3] & 0x04u;
    out.standstill = f[3] & 0x08u;
    return true;
}

void encode_brake_status(const BrakeStatus& m, std::uint8_t counter, std::uint8_t* f) {
    clear(f);
    f[2] = static_cast<std::uint8_t>((m.active ? 0x01u : 0u) | (m.timeout ? 0x02u : 0u) |
                                     (m.rejecting ? 0x04u : 0u));
    put_u16(f, 3, to_raw(m.actual_decel_mps2));
    f[5] = m.ack_valid ? 1u : 0u;
    f[6] = m.ack_counter;
    e2e::protect(AEGIS_CAN_ID_BRAKE_STATUS, counter, f);
}

bool decode_brake_status(const std::uint8_t* f, BrakeStatus& out) {
    if ((f[1] & 0xF0u) || (f[2] & 0xF8u) || (f[5] & 0xFEu) || (f[6] & 0xF0u) || f[7]) return false;
    out.ack_valid = (f[5] & 1u) != 0;
    out.ack_counter = f[6];
    out.active = f[2] & 0x01u;
    out.timeout = f[2] & 0x02u;
    out.rejecting = f[2] & 0x04u;
    out.actual_decel_mps2 = get_u16(f, 3) * kDecelResolution;
    return true;
}

}  // namespace aegis::codec
