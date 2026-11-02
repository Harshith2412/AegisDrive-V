// AegisDrive-V — ADAS ECU: Automatic Emergency Braking (AEB) function.
// Deterministic, step-based, no dynamic allocation, no exceptions.
// SIMULATION ONLY — not production software.
#pragma once
#include <cstdint>
#include "aegis/e2e.hpp"
#include "aegis/aegis_types.h"

namespace aegis {

enum class AdasState : std::uint8_t {
    Disabled = AEGIS_ADAS_DISABLED,
    Standby = AEGIS_ADAS_STANDBY,
    Monitoring = AEGIS_ADAS_MONITORING,
    Warning = AEGIS_ADAS_WARNING,
    Braking = AEGIS_ADAS_BRAKING,
    Degraded = AEGIS_ADAS_DEGRADED,
    Fault = AEGIS_ADAS_FAULT,
};

AegisAdasConfig default_adas_config();
bool adas_config_valid(const AegisAdasConfig& cfg);

// Time-to-collision [s]; +inf if not closing faster than min_closing_speed_mps.
double compute_ttc(double range_m, double range_rate_mps, double min_closing_speed_mps);
// Constant deceleration needed to cancel the closing speed before range shrinks
// to stop_margin_m, assuming the object keeps its current speed. 0 if not closing.
double compute_required_decel(double range_m, double range_rate_mps, double stop_margin_m);

class AdasEcu {
public:
    explicit AdasEcu(const AegisAdasConfig& cfg);
    AegisAdasOutput step(const AegisAdasInput& in);
    AdasState state() const { return state_; }

    static bool transition_allowed(AdasState from, AdasState to);
    // Single entry point for every state change. Illegal requests are rejected,
    // counted and latched as a diagnostic. Public for verification purposes.
    bool request_transition(AdasState to);

private:
    void monitor_feedback(const AegisAdasInput& in);
    e2e::Receiver feedback_rx_{2};
    bool feedback_started_ = false;
    bool have_ack_ = false;
    bool feedback_fault_ = false;
    std::uint8_t last_ack_ = 0;
    std::uint64_t last_feedback_ms_ = 0;
    std::uint64_t last_ack_ms_ = 0;
    bool achieved_fault_ = false;
    bool achieved_mismatch_ = false;
    std::uint64_t mismatch_since_ms_ = 0;
    bool demand_timing_ = false;
    std::uint64_t demand_since_ms_ = 0;
    struct InputCheck { bool ok; std::uint32_t flags; };
    InputCheck check_inputs(const AegisAdasInput& in) const;
    bool fresh(std::uint64_t now, std::uint64_t ts) const;
    void evaluate_threat_states(const AegisAdasInput& in, double ttc, double closing);
    void finalize(const AegisAdasInput& in, AegisAdasOutput& out, std::uint32_t flags);

    AegisAdasConfig cfg_;
    bool config_ok_;
    AdasState state_;
    std::uint32_t latched_flags_ = 0;
    std::uint32_t illegal_transitions_ = 0;
    std::uint64_t degraded_since_ms_ = 0;
    std::uint32_t valid_cycles_ = 0;
    bool standstill_timing_ = false;
    std::uint64_t standstill_since_ms_ = 0;
    bool clear_timing_ = false;
    std::uint64_t clear_since_ms_ = 0;
    bool have_lead_speed_ = false;
    double previous_lead_speed_ = 0.0;
    double lead_accel_ = 0.0;
    std::uint64_t previous_meas_ms_ = 0;
    double decel_request_ = 0.0;
    std::uint8_t brake_req_counter_ = 0;
    std::uint8_t status_counter_ = 0;
};

}  // namespace aegis
