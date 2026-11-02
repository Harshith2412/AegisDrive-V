// AegisDrive-V — Brake ECU: request validation, timeout, arbitration, actuator model.
// SIMULATION ONLY — the actuator is a first-order lag, not a hydraulic model.
#pragma once
#include <cstdint>
#include "aegis/aegis_types.h"
#include "aegis/e2e.hpp"

namespace aegis {

AegisBrakeConfig default_brake_config();
bool brake_config_valid(const AegisBrakeConfig& cfg);

class BrakeEcu {
public:
    explicit BrakeEcu(const AegisBrakeConfig& cfg);
    AegisBrakeOutput step(const AegisBrakeInput& in);
    bool config_ok() const { return config_ok_; }
private:
    std::uint8_t ack_counter_ = 0;
    std::uint8_t validate(const AegisBrakeInput& in, bool& act_on_frame, e2e::Receiver& receiver);

    AegisBrakeConfig cfg_;
    bool config_ok_;
    e2e::Receiver rx_;
    e2e::Receiver backup_rx_;
    bool have_valid_ = false;
    std::uint64_t last_valid_ms_ = 0;
    bool cmd_active_ = false;
    double cmd_decel_ = 0.0;
    double actual_decel_ = 0.0;
    std::uint32_t accepted_ = 0;
    std::uint32_t rejected_ = 0;
    std::uint8_t last_reject_ = AEGIS_REJ_NONE;
    std::uint8_t tx_counter_ = 0;
};

}  // namespace aegis
