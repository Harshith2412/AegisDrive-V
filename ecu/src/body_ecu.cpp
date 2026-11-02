#include "aegis/body_ecu.hpp"

#include "aegis/codec.hpp"

namespace aegis {

AegisBodyConfig default_body_config() {
    AegisBodyConfig c{};
    c.timeout_ms = 100;
    c.hazard_hold_ms = 3000;
    return c;
}

BodyEcu::BodyEcu(const AegisBodyConfig& cfg) : cfg_(cfg) {}

AegisBodyOutput BodyEcu::step(const AegisBodyInput& in) {
    AegisBodyOutput out{};

    if (in.brake_status_present) {
        codec::BrakeStatus bs;
        const e2e::Check c = in.brake_status_dlc == AEGIS_CAN_DLC
                                 ? brake_rx_.check(AEGIS_CAN_ID_BRAKE_STATUS, in.brake_status_frame)
                                 : e2e::Check::CrcError;
        if (c == e2e::Check::Ok && codec::decode_brake_status(in.brake_status_frame, bs)) {
            brake_active_ = bs.active;
            have_brake_ = true;
            last_brake_ms_ = in.now_ms;
        } else if (c != e2e::Check::InitialSync) {
            ++rejected_;
        }
    }
    if (in.adas_status_present) {
        codec::AdasStatus as;
        const e2e::Check c = in.adas_status_dlc == AEGIS_CAN_DLC
                                 ? adas_rx_.check(AEGIS_CAN_ID_ADAS_STATUS, in.adas_status_frame)
                                 : e2e::Check::CrcError;
        if (c == e2e::Check::Ok && codec::decode_adas_status(in.adas_status_frame, as)) {
            adas_warning_ = as.warning;
            adas_unavailable_ = as.unavailable;
            adas_emergency_braking_ = as.emergency && as.state == AEGIS_ADAS_BRAKING;
            have_adas_ = true;
            last_adas_ms_ = in.now_ms;
        } else if (c != e2e::Check::InitialSync) {
            ++rejected_;
        }
    }

    const bool brake_to = !have_brake_ || in.now_ms < last_brake_ms_ || in.now_ms - last_brake_ms_ > cfg_.timeout_ms;
    const bool adas_to = !have_adas_ || in.now_ms < last_adas_ms_ || in.now_ms - last_adas_ms_ > cfg_.timeout_ms;

    // Brake lamp follows the last valid brake status (retained on timeout; fault flagged).
    out.brake_lamp = brake_active_ ? 1 : 0;
    out.warning_indicator = (!adas_to && adas_warning_) ? 1 : 0;
    out.aeb_unavailable_indicator = (adas_to || adas_unavailable_) ? 1 : 0;

    if (!adas_to && adas_emergency_braking_) hazard_until_ms_ = in.now_ms + cfg_.hazard_hold_ms;
    out.hazard_lamps = in.now_ms < hazard_until_ms_ ? 1 : 0;

    out.fault_brake_status_timeout = brake_to ? 1 : 0;
    out.fault_adas_status_timeout = adas_to ? 1 : 0;
    out.rejected_frames = rejected_;
    return out;
}

}  // namespace aegis
