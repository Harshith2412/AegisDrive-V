#include "aegis/brake_ecu.hpp"

#include <cmath>

#include "aegis/codec.hpp"

namespace aegis {

AegisBrakeConfig default_brake_config() {
    AegisBrakeConfig c{};
    c.timeout_ms = 100;           // 10 missed 10 ms frames
    c.max_counter_delta = 2;      // tolerate one lost frame
    c.max_decel_mps2 = 10.0;      // command range upper bound
    c.actuator_tau_s = 0.15;      // assumed brake build-up time constant
    c.active_threshold_mps2 = 0.3;
    return c;
}

bool brake_config_valid(const AegisBrakeConfig& c) {
    return c.timeout_ms > 0 && c.max_counter_delta >= 1 && c.max_counter_delta <= 14 &&
           std::isfinite(c.max_decel_mps2) && c.max_decel_mps2 > 0.0 && c.max_decel_mps2 <= 15.0 &&
           std::isfinite(c.actuator_tau_s) && c.actuator_tau_s > 0.0 &&
           std::isfinite(c.active_threshold_mps2) && c.active_threshold_mps2 > 0.0;
}

BrakeEcu::BrakeEcu(const AegisBrakeConfig& cfg)
    : cfg_(cfg),
      config_ok_(brake_config_valid(cfg)),
      rx_(static_cast<std::uint8_t>(cfg.max_counter_delta)),
      backup_rx_(static_cast<std::uint8_t>(cfg.max_counter_delta)) {}

std::uint8_t BrakeEcu::validate(const AegisBrakeInput& in, bool& act, e2e::Receiver& receiver) {
    act = false;
    if (in.can_id != AEGIS_CAN_ID_BRAKE_REQ) return AEGIS_REJ_WRONG_ID;
    if (in.frame_dlc != AEGIS_CAN_DLC) return AEGIS_REJ_BAD_DLC;
    switch (receiver.check(AEGIS_CAN_ID_BRAKE_REQ, in.frame)) {
        case e2e::Check::CrcError: return AEGIS_REJ_CRC;
        case e2e::Check::Repeated: return AEGIS_REJ_REPEATED;
        case e2e::Check::WrongSequence: return AEGIS_REJ_SEQUENCE;
        case e2e::Check::InitialSync: return AEGIS_REJ_NONE;  // sync only, act == false
        case e2e::Check::Ok: break;
    }
    codec::BrakeRequest req;
    const std::uint8_t r = codec::decode_brake_request(in.frame, cfg_.max_decel_mps2, req);
    if (r != AEGIS_REJ_NONE) return r;
    cmd_active_ = req.active;
    cmd_decel_ = req.decel_mps2;
    act = true;
    return AEGIS_REJ_NONE;
}

AegisBrakeOutput BrakeEcu::step(const AegisBrakeInput& in) {
    AegisBrakeOutput out{};
    out.frame_accepted = 0;
    // Independent E2E state per transport. Evaluate both continuously, prefer primary.
    // Both paths terminate in this ECU and the same physical actuator.
    bool primary_act = false;
    bool backup_act = false;
    auto receive = [&](const AegisBrakeInput& input, e2e::Receiver& receiver, bool& act) {
        const auto r = validate(input, act, receiver);
        if (r != AEGIS_REJ_NONE) { ++rejected_; last_reject_ = r; }
    };
    if (config_ok_) {
        // Validate backup first, so a valid primary command wins shared command arbitration.
        if (in.backup_present) {
            AegisBrakeInput backup = in;
            backup.can_id = AEGIS_CAN_ID_BRAKE_REQ;
            backup.frame_dlc = in.backup_dlc;
            for (unsigned i=0;i<AEGIS_CAN_DLC;++i) backup.frame[i]=in.backup_frame[i];
            receive(backup, backup_rx_, backup_act);
        }
        if (in.frame_present) receive(in, rx_, primary_act);
        if (primary_act || backup_act) {
            ack_counter_ = (primary_act ? in.frame[1] : in.backup_frame[1]) & 0x0Fu;
            ++accepted_;
            have_valid_ = true;
            last_valid_ms_ = in.now_ms;
            out.frame_accepted = 1;
        }
    }

    const bool timed_out = !have_valid_ || in.now_ms < last_valid_ms_ ||
                           (in.now_ms - last_valid_ms_) > cfg_.timeout_ms;
    const double aeb = (config_ok_ && !timed_out && cmd_active_) ? cmd_decel_ : 0.0;

    double driver = std::isfinite(in.driver_brake_mps2) ? in.driver_brake_mps2 : 0.0;
    if (driver < 0.0) driver = 0.0;
    if (driver > cfg_.max_decel_mps2) driver = cfg_.max_decel_mps2;
    const double target = aeb > driver ? aeb : driver;  // arbitration: highest demand wins

    const bool dt_ok = std::isfinite(in.dt_s) && in.dt_s > 0.0 && in.dt_s <= 0.1;
    if (dt_ok && config_ok_) {
        const double alpha = 1.0 - std::exp(-in.dt_s / cfg_.actuator_tau_s);
        actual_decel_ += (target - actual_decel_) * alpha;
        if (actual_decel_ < 1e-6) actual_decel_ = 0.0;
    }

    out.aeb_target_decel_mps2 = aeb;
    out.target_decel_mps2 = target;
    out.actual_decel_mps2 = actual_decel_;
    out.brake_active = actual_decel_ >= cfg_.active_threshold_mps2 ? 1 : 0;
    out.status = !have_valid_ ? AEGIS_BRK_STATUS_NO_SYNC
                              : (timed_out ? AEGIS_BRK_STATUS_TIMEOUT : AEGIS_BRK_STATUS_OK);
    out.last_reject_reason = last_reject_;
    out.accepted_frames = accepted_;
    out.rejected_frames = rejected_;

    codec::BrakeStatus st;
    st.ack_valid = have_valid_;
    st.ack_counter = ack_counter_;
    st.active = out.brake_active != 0;
    st.timeout = out.status == AEGIS_BRK_STATUS_TIMEOUT;
    st.rejecting = in.frame_present && !out.frame_accepted && last_reject_ != AEGIS_REJ_NONE;
    st.actual_decel_mps2 = actual_decel_;
    codec::encode_brake_status(st, tx_counter_, out.status_frame);
    tx_counter_ = static_cast<std::uint8_t>((tx_counter_ + 1u) & 0x0Fu);
    return out;
}

}  // namespace aegis
