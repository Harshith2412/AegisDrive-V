#include "aegis/adas_ecu.hpp"

#include <cmath>
#include <limits>

#include "aegis/codec.hpp"

namespace aegis {
namespace {
constexpr double kInf = std::numeric_limits<double>::infinity();
constexpr double kMinStoppingDistance_m = 0.1;  // avoids division by ~0

double clamp(double v, double lo, double hi) { return v < lo ? lo : (v > hi ? hi : v); }
bool finite_pos(double v) { return std::isfinite(v) && v > 0.0; }

// Allowed transitions [from][to]. Self-transitions are treated as no-ops.
// Rows/cols: DISABLED STANDBY MONITORING WARNING BRAKING DEGRADED FAULT
constexpr bool kAllowed[AEGIS_ADAS_NUM_STATES][AEGIS_ADAS_NUM_STATES] = {
    /* DISABLED   */ {false, true,  false, false, false, false, false},
    /* STANDBY    */ {true,  false, true,  false, false, true,  true },
    /* MONITORING */ {true,  true,  false, true,  true,  true,  true },
    /* WARNING    */ {true,  true,  true,  false, true,  true,  true },
    /* BRAKING    */ {true,  true,  true,  false, false, true,  true },
    /* DEGRADED   */ {true,  true,  false, false, false, false, true },
    /* FAULT      */ {true,  false, false, false, false, false, false},
};
}  // namespace

AegisAdasConfig default_adas_config() {
    AegisAdasConfig c{};
    c.ttc_warning_s = 2.6;
    c.ttc_brake_s = 1.6;
    c.ttc_hysteresis_s = 0.3;
    c.min_closing_speed_mps = 0.5;
    c.stop_margin_m = 2.0;
    c.decel_gain = 1.2;
    c.min_brake_decel_mps2 = 4.0;
    c.max_brake_decel_mps2 = 9.0;
    c.emergency_decel_mps2 = 6.0;
    c.min_active_speed_mps = 10.0 / 3.6;
    c.max_active_speed_mps = 80.0 / 3.6;
    c.standstill_speed_mps = 0.1;
    c.max_range_m = 200.0;
    c.max_abs_range_rate_mps = 80.0;
    c.max_ego_speed_mps = 70.0;
    c.stale_timeout_ms = 150;
    c.standstill_hold_ms = 2000;
    c.threat_clear_ms = 500;
    c.degraded_to_fault_ms = 1000;
    c.recovery_cycles = 10;
    c.planning_decel_mps2 = 4.0;
    return c;
}

bool adas_config_valid(const AegisAdasConfig& c) {
    const bool finite = std::isfinite(c.ttc_warning_s) && std::isfinite(c.ttc_brake_s) &&
                        std::isfinite(c.ttc_hysteresis_s) && std::isfinite(c.stop_margin_m) &&
                        std::isfinite(c.min_active_speed_mps) && std::isfinite(c.standstill_speed_mps) &&
                        std::isfinite(c.max_active_speed_mps) && std::isfinite(c.max_brake_decel_mps2);
    if (!finite || !std::isfinite(c.planning_decel_mps2) || c.planning_decel_mps2 < 0.0 ||
        c.planning_decel_mps2 > c.max_brake_decel_mps2) return false;
    return finite_pos(c.ttc_brake_s) && c.ttc_brake_s < c.ttc_warning_s &&
           c.ttc_hysteresis_s >= 0.0 && finite_pos(c.min_closing_speed_mps) &&
           c.stop_margin_m >= 0.0 && finite_pos(c.decel_gain) &&
           finite_pos(c.min_brake_decel_mps2) && c.min_brake_decel_mps2 <= c.max_brake_decel_mps2 &&
           c.max_brake_decel_mps2 <= 10.0 && finite_pos(c.emergency_decel_mps2) &&
           c.emergency_decel_mps2 <= c.max_brake_decel_mps2 && c.min_active_speed_mps >= 0.0 &&
           c.min_active_speed_mps < c.max_active_speed_mps &&
           c.max_active_speed_mps <= c.max_ego_speed_mps && c.standstill_speed_mps >= 0.0 &&
           c.standstill_speed_mps < c.min_active_speed_mps && finite_pos(c.max_range_m) &&
           finite_pos(c.max_abs_range_rate_mps) && finite_pos(c.max_ego_speed_mps) &&
           c.stale_timeout_ms > 0 && c.recovery_cycles >= 1 && c.degraded_to_fault_ms > 0;
}

double compute_ttc(double range_m, double range_rate_mps, double min_closing_speed_mps) {
    const double closing = -range_rate_mps;
    if (!(closing > min_closing_speed_mps)) return kInf;
    return range_m / closing;
}

double compute_required_decel(double range_m, double range_rate_mps, double stop_margin_m) {
    const double closing = -range_rate_mps;
    if (!(closing > 0.0)) return 0.0;
    double d = range_m - stop_margin_m;
    if (d < kMinStoppingDistance_m) d = kMinStoppingDistance_m;
    return closing * closing / (2.0 * d);
}

AdasEcu::AdasEcu(const AegisAdasConfig& cfg)
    : cfg_(cfg), config_ok_(adas_config_valid(cfg)), state_(AdasState::Disabled) {
    if (!config_ok_) {
        state_ = AdasState::Fault;  // initial state assignment, not a transition
        latched_flags_ |= AEGIS_DTC_INVALID_CONFIG;
    }
}

bool AdasEcu::transition_allowed(AdasState from, AdasState to) {
    const auto f = static_cast<std::uint8_t>(from);
    const auto t = static_cast<std::uint8_t>(to);
    if (f >= AEGIS_ADAS_NUM_STATES || t >= AEGIS_ADAS_NUM_STATES) return false;
    return kAllowed[f][t];
}

bool AdasEcu::request_transition(AdasState to) {
    if (to == state_) return true;
    if (!config_ok_ || !transition_allowed(state_, to)) {
        ++illegal_transitions_;
        latched_flags_ |= AEGIS_DTC_ILLEGAL_TRANSITION;
        return false;
    }
    state_ = to;
    standstill_timing_ = false;
    clear_timing_ = false;
    return true;
}

bool AdasEcu::fresh(std::uint64_t now, std::uint64_t ts) const {
    return ts <= now && (now - ts) <= cfg_.stale_timeout_ms;
}

AdasEcu::InputCheck AdasEcu::check_inputs(const AegisAdasInput& in) const {
    std::uint32_t f = 0;
    const bool finite = std::isfinite(in.ego_speed_mps) &&
                        (!in.object_present || (std::isfinite(in.range_m) && std::isfinite(in.range_rate_mps)));
    if (!finite) return {false, AEGIS_DTC_NONFINITE_INPUT};

    if (!in.ego_speed_valid) {
        f |= AEGIS_DTC_EGO_SPEED_INVALID;
    } else if (in.ego_speed_ts_ms > in.now_ms) {
        f |= AEGIS_DTC_IMPLAUSIBLE_INPUT;  // timestamp from the future
    } else if (!fresh(in.now_ms, in.ego_speed_ts_ms)) {
        f |= AEGIS_DTC_STALE_INPUT;
    }
    if (in.ego_speed_mps < 0.0 || in.ego_speed_mps > cfg_.max_ego_speed_mps) f |= AEGIS_DTC_IMPLAUSIBLE_INPUT;

    if (!in.sensor_ok) {
        f |= AEGIS_DTC_SENSOR_NOT_OK;
    } else if (in.meas_ts_ms > in.now_ms) {
        f |= AEGIS_DTC_IMPLAUSIBLE_INPUT;
    } else if (!fresh(in.now_ms, in.meas_ts_ms)) {
        f |= AEGIS_DTC_STALE_INPUT;
    }
    if (in.object_present) {
        if (in.range_m < 0.0 || in.range_m > cfg_.max_range_m) f |= AEGIS_DTC_IMPLAUSIBLE_INPUT;
        if (std::fabs(in.range_rate_mps) > cfg_.max_abs_range_rate_mps) f |= AEGIS_DTC_IMPLAUSIBLE_INPUT;
    }
    return {f == 0, f};
}

void AdasEcu::evaluate_threat_states(const AegisAdasInput& in, double ttc, double closing) {
    const double v = in.ego_speed_mps;
    const bool in_window = v >= cfg_.min_active_speed_mps && v <= cfg_.max_active_speed_mps;
    const bool standstill = v <= cfg_.standstill_speed_mps;
    // Engineering envelope: ego response allowance 0.35 s, assumed lead max decel 8.
    // Planning decel is an assumption, not an estimate of available road friction.
    const double lead_v = clamp(v + in.range_rate_mps, 0.0, cfg_.max_ego_speed_mps);
    const double envelope = cfg_.planning_decel_mps2 > 0.0
        ? cfg_.stop_margin_m + 0.35 * v + v*v/(2.0*cfg_.planning_decel_mps2) - lead_v*lead_v/16.0
        : 0.0;
    if (in.object_present && (!have_lead_speed_ || in.meas_ts_ms != previous_meas_ms_)) {
        if (have_lead_speed_ && in.meas_ts_ms > previous_meas_ms_ &&
            in.meas_ts_ms - previous_meas_ms_ <= cfg_.stale_timeout_ms) {
            const double dt = static_cast<double>(in.meas_ts_ms - previous_meas_ms_) / 1000.0;
            lead_accel_ = 0.8 * lead_accel_ + 0.2 * (lead_v - previous_lead_speed_) / dt;
        } else { lead_accel_ = 0.0; }
        have_lead_speed_ = true;
        previous_lead_speed_ = lead_v;
        previous_meas_ms_ = in.meas_ts_ms;
    }
    if (!in.object_present) { have_lead_speed_ = false; lead_accel_ = 0.0; }
    const bool envelope_threat = in.object_present && closing > cfg_.min_closing_speed_mps &&
                                 in.range_m <= envelope;

    if (state_ == AdasState::Standby && in_window) request_transition(AdasState::Monitoring);

    switch (state_) {
        case AdasState::Monitoring:
            if (!in_window) request_transition(AdasState::Standby);
            else if (ttc <= cfg_.ttc_brake_s || envelope_threat) request_transition(AdasState::Braking);
            else if (ttc <= cfg_.ttc_warning_s) request_transition(AdasState::Warning);
            break;
        case AdasState::Warning:
            if (!in_window) request_transition(AdasState::Standby);
            else if (ttc <= cfg_.ttc_brake_s || envelope_threat) request_transition(AdasState::Braking);
            else if (ttc > cfg_.ttc_warning_s + cfg_.ttc_hysteresis_s) request_transition(AdasState::Monitoring);
            break;
        case AdasState::Braking: {
            if (standstill) {
                if (!standstill_timing_) {
                    standstill_timing_ = true;
                    standstill_since_ms_ = in.now_ms;
                } else if (in.now_ms - standstill_since_ms_ >= cfg_.standstill_hold_ms) {
                    request_transition(AdasState::Standby);
                    break;
                }
            } else {
                standstill_timing_ = false;
            }
            // Do not release solely because ego braking temporarily reverses closing speed.
            const bool closing_now = in.object_present &&
                (closing >= -0.5 || in.range_m <= envelope + cfg_.stop_margin_m || lead_accel_ < -0.3);
            if (!closing_now && !standstill) {
                if (!clear_timing_) {
                    clear_timing_ = true;
                    clear_since_ms_ = in.now_ms;
                } else if (in.now_ms - clear_since_ms_ >= cfg_.threat_clear_ms) {
                    request_transition(AdasState::Monitoring);
                }
            } else {
                clear_timing_ = false;
            }
            break;
        }
        default:
            break;
    }

    if (state_ == AdasState::Braking) {
        const double areq = in.object_present
                                ? compute_required_decel(in.range_m, in.range_rate_mps, cfg_.stop_margin_m)
                                : 0.0;
        decel_request_ = clamp(cfg_.decel_gain * areq, cfg_.min_brake_decel_mps2, cfg_.max_brake_decel_mps2);
    } else {
        decel_request_ = 0.0;
    }
}

AegisAdasOutput AdasEcu::step(const AegisAdasInput& in) {
    AegisAdasOutput out{};
    out.ttc_s = kInf;
    out.required_decel_mps2 = 0.0;
    std::uint32_t flags = 0;

    if (!config_ok_) {
        decel_request_ = 0.0;
        finalize(in, out, flags);
        return out;
    }
    if (!in.function_enabled) {
        request_transition(AdasState::Disabled);
        feedback_started_ = have_ack_ = feedback_fault_ = demand_timing_ = false;
        feedback_rx_.reset();
        achieved_fault_ = achieved_mismatch_ = false;
        latched_flags_ &= ~AEGIS_DTC_SECURITY_EVENT;
        have_lead_speed_ = false;
        lead_accel_ = 0.0;
        valid_cycles_ = 0;
        decel_request_ = 0.0;
        finalize(in, out, flags);
        return out;
    }
    if (in.security_event) latched_flags_ |= AEGIS_DTC_SECURITY_EVENT;
    monitor_feedback(in);
    if (state_ == AdasState::Disabled) request_transition(AdasState::Standby);
    if (state_ == AdasState::Fault) {
        decel_request_ = 0.0;
        finalize(in, out, flags);
        return out;
    }

    const InputCheck chk = check_inputs(in);
    flags |= chk.flags;
    if (!chk.ok) {
        have_lead_speed_ = false;
        lead_accel_ = 0.0;
        valid_cycles_ = 0;
        if (state_ != AdasState::Degraded) {
            request_transition(AdasState::Degraded);
            degraded_since_ms_ = in.now_ms;
        } else if (in.now_ms - degraded_since_ms_ >= cfg_.degraded_to_fault_ms) {
            latched_flags_ |= AEGIS_DTC_PERSISTENT_DEGRADED;
            request_transition(AdasState::Fault);
        }
        decel_request_ = 0.0;
        finalize(in, out, flags);
        return out;
    }

    if (state_ == AdasState::Degraded) {
        ++valid_cycles_;
        if (valid_cycles_ < cfg_.recovery_cycles) {
            decel_request_ = 0.0;
            finalize(in, out, flags);
            return out;
        }
        valid_cycles_ = 0;
        request_transition(AdasState::Standby);
    }

    const double closing = in.object_present ? -in.range_rate_mps : 0.0;
    const double ttc = in.object_present ? compute_ttc(in.range_m, in.range_rate_mps, cfg_.min_closing_speed_mps) : kInf;
    out.ttc_s = ttc;
    out.required_decel_mps2 =
        in.object_present ? compute_required_decel(in.range_m, in.range_rate_mps, cfg_.stop_margin_m) : 0.0;
    evaluate_threat_states(in, ttc, closing);
    finalize(in, out, flags);
    return out;
}

void AdasEcu::monitor_feedback(const AegisAdasInput& in) {
    if (in.achieved_monitor_enabled) {
        const bool valid = in.achieved_valid && std::isfinite(in.achieved_decel_mps2) &&
            in.achieved_decel_mps2 >= 0.0 && in.achieved_decel_mps2 <= 15.0 &&
            in.achieved_ts_ms <= in.now_ms && in.now_ms - in.achieved_ts_ms <= 100;
        if (!valid) achieved_fault_ = true;
        const double minimum = decel_request_ * 0.5 < 2.0 ? decel_request_ * 0.5 : 2.0;
        const bool mismatch = valid && state_ == AdasState::Braking &&
            in.ego_speed_mps > cfg_.standstill_speed_mps && demand_timing_ &&
            in.now_ms >= demand_since_ms_ && in.now_ms - demand_since_ms_ > 300 &&
            in.achieved_decel_mps2 < minimum;
        if (mismatch) {
            if (!achieved_mismatch_) { achieved_mismatch_ = true; mismatch_since_ms_ = in.now_ms; }
            else if (in.now_ms - mismatch_since_ms_ >= 200) achieved_fault_ = true;
        } else { achieved_mismatch_ = false; }
    }
    if (!in.feedback_monitor_enabled) {
        if (in.achieved_monitor_enabled && state_ == AdasState::Braking) {
            if (!demand_timing_) { demand_timing_ = true; demand_since_ms_ = in.now_ms; }
        } else { demand_timing_ = false; }
        return;
    }
    if (!feedback_started_) {
        feedback_started_ = true;
        last_feedback_ms_ = last_ack_ms_ = in.now_ms;
    }
    if (in.brake_status_present && in.brake_status_dlc == AEGIS_CAN_DLC) {
        codec::BrakeStatus st;
        if (feedback_rx_.check(AEGIS_CAN_ID_BRAKE_STATUS, in.brake_status_frame) == e2e::Check::Ok &&
            codec::decode_brake_status(in.brake_status_frame, st) && st.actual_decel_mps2 <= 15.0) {
            last_feedback_ms_ = in.now_ms;
            if (st.ack_valid && (!have_ack_ || st.ack_counter != last_ack_)) {
                have_ack_ = true;
                last_ack_ = st.ack_counter;
                last_ack_ms_ = in.now_ms;
            }
            if (st.timeout || st.rejecting) feedback_fault_ = true;
            if (demand_timing_ && in.now_ms >= demand_since_ms_ &&
                in.now_ms - demand_since_ms_ > 300 && !st.active) feedback_fault_ = true;
        }
    }
    if (state_ == AdasState::Braking) {
        if (!demand_timing_) { demand_timing_ = true; demand_since_ms_ = in.now_ms; }
    } else { demand_timing_ = false; }
    if (in.now_ms < last_feedback_ms_ || in.now_ms < last_ack_ms_ ||
        in.now_ms - last_feedback_ms_ > 100 || in.now_ms - last_ack_ms_ > 100)
        feedback_fault_ = true;
}

void AdasEcu::finalize(const AegisAdasInput& in, AegisAdasOutput& out, std::uint32_t flags) {
    out.state = static_cast<std::uint8_t>(state_);
    out.warning_active = (state_ == AdasState::Warning || state_ == AdasState::Braking) ? 1 : 0;
    out.brake_request_active = (state_ == AdasState::Braking) ? 1 : 0;
    out.function_unavailable = (state_ == AdasState::Degraded || state_ == AdasState::Fault) ? 1 : 0;
    out.decel_request_mps2 = out.brake_request_active ? decel_request_ : 0.0;
    out.emergency = (out.brake_request_active && out.decel_request_mps2 >= cfg_.emergency_decel_mps2) ? 1 : 0;
    out.standstill = (in.ego_speed_valid && std::isfinite(in.ego_speed_mps) &&
                      in.ego_speed_mps <= cfg_.standstill_speed_mps) ? 1 : 0;
    if (achieved_fault_) { out.function_unavailable = 1; flags |= AEGIS_DTC_ACHIEVED_DECEL; }
    if (feedback_fault_) {
        out.function_unavailable = 1;
        flags |= AEGIS_DTC_BRAKE_FEEDBACK;
    }
    out.dtc_flags = flags | latched_flags_;
    out.illegal_transition_count = illegal_transitions_;

    codec::BrakeRequest req;
    req.active = out.brake_request_active != 0;
    req.emergency = out.emergency != 0;
    req.decel_mps2 = out.decel_request_mps2;
    codec::encode_brake_request(req, brake_req_counter_, out.brake_req_frame);
    brake_req_counter_ = static_cast<std::uint8_t>((brake_req_counter_ + 1u) & 0x0Fu);

    codec::AdasStatus st;
    st.state = out.state;
    st.warning = out.warning_active != 0;
    st.unavailable = out.function_unavailable != 0;
    st.emergency = out.emergency != 0;
    st.standstill = out.standstill != 0;
    codec::encode_adas_status(st, status_counter_, out.adas_status_frame);
    status_counter_ = static_cast<std::uint8_t>((status_counter_ + 1u) & 0x0Fu);
}

}  // namespace aegis
