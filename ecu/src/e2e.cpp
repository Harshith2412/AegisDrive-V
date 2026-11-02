#include "aegis/e2e.hpp"

namespace aegis::e2e {
namespace {
constexpr std::uint8_t kPoly = 0x1D;
std::uint8_t update(std::uint8_t crc, std::uint8_t byte) {
    crc ^= byte;
    for (int bit = 0; bit < 8; ++bit) {
        crc = (crc & 0x80u) ? static_cast<std::uint8_t>((crc << 1) ^ kPoly)
                            : static_cast<std::uint8_t>(crc << 1);
    }
    return crc;
}
}  // namespace

std::uint8_t crc8_j1850(const std::uint8_t* data, std::size_t len) {
    std::uint8_t crc = 0xFF;
    for (std::size_t i = 0; i < len; ++i) crc = update(crc, data[i]);
    return static_cast<std::uint8_t>(crc ^ 0xFFu);
}

std::uint8_t frame_crc(std::uint16_t data_id, const std::uint8_t* frame8) {
    std::uint8_t crc = 0xFF;
    crc = update(crc, static_cast<std::uint8_t>(data_id & 0xFFu));
    crc = update(crc, static_cast<std::uint8_t>((data_id >> 8) & 0xFFu));
    for (int i = 1; i < 8; ++i) crc = update(crc, frame8[i]);
    return static_cast<std::uint8_t>(crc ^ 0xFFu);
}

void protect(std::uint16_t data_id, std::uint8_t counter, std::uint8_t* frame8) {
    frame8[1] = static_cast<std::uint8_t>((frame8[1] & 0xF0u) | (counter & 0x0Fu));
    frame8[0] = frame_crc(data_id, frame8);
}

Check Receiver::check(std::uint16_t data_id, const std::uint8_t* frame8) {
    if (frame_crc(data_id, frame8) != frame8[0]) return Check::CrcError;
    const std::uint8_t counter = frame8[1] & 0x0Fu;
    if (!synced_) {
        synced_ = true;
        last_counter_ = counter;
        return Check::InitialSync;
    }
    const std::uint8_t delta = static_cast<std::uint8_t>((counter - last_counter_) & 0x0Fu);
    if (delta == 0) return Check::Repeated;
    last_counter_ = counter;  // re-synchronise on both OK and wrong sequence
    if (delta > max_delta_) return Check::WrongSequence;
    return Check::Ok;
}

}  // namespace aegis::e2e
