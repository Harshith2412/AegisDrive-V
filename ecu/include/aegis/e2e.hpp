// AegisDrive-V — End-to-end (E2E) style message protection for the vertical slice.
//
// Purpose: detect *random/systematic communication faults* (corruption, repetition,
// loss, out-of-order) on safety-relevant frames. This is a FUNCTIONAL SAFETY
// mechanism, modelled loosely on the CRC + alive-counter idea used in automotive
// E2E protection. It is NOT a security mechanism: CRC-8 provides no protection
// against an intentional attacker (see Phase 7, not yet started).
//
// Not claimed to conform to any AUTOSAR E2E profile.
//
// Frame layout convention (all protected frames, DLC = 8):
//   byte 0      : CRC-8 (SAE J1850 polynomial 0x1D, init 0xFF, xorout 0xFF)
//                 computed over DataID (low byte, high byte) followed by bytes 1..7
//   byte 1[3:0] : alive counter, modulo 16
//   byte 1[7:4] : reserved, must be 0
//   bytes 2..7  : message-specific payload
#pragma once
#include <cstddef>
#include <cstdint>

namespace aegis::e2e {

std::uint8_t crc8_j1850(const std::uint8_t* data, std::size_t len);
std::uint8_t frame_crc(std::uint16_t data_id, const std::uint8_t* frame8);
void protect(std::uint16_t data_id, std::uint8_t counter, std::uint8_t* frame8);

enum class Check : std::uint8_t {
    Ok = 0,
    InitialSync,    // first valid frame: used to synchronise, not acted upon
    CrcError,
    Repeated,       // counter delta == 0 (frozen/repeated sender)
    WrongSequence,  // counter delta > max_delta (receiver re-synchronises)
};

class Receiver {
public:
    explicit Receiver(std::uint8_t max_delta) : max_delta_(max_delta) {}
    Check check(std::uint16_t data_id, const std::uint8_t* frame8);
    void reset() { synced_ = false; last_counter_ = 0; }
private:
    std::uint8_t max_delta_;
    bool synced_ = false;
    std::uint8_t last_counter_ = 0;
};

}  // namespace aegis::e2e
