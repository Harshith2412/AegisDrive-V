// AegisDrive-V — Body Control Module: brake lamps, warning telltales, hazard policy.
#pragma once
#include <cstdint>
#include "aegis/aegis_types.h"
#include "aegis/e2e.hpp"

namespace aegis {

AegisBodyConfig default_body_config();

class BodyEcu {
public:
    explicit BodyEcu(const AegisBodyConfig& cfg);
    AegisBodyOutput step(const AegisBodyInput& in);
private:
    AegisBodyConfig cfg_;
    e2e::Receiver brake_rx_{2};
    e2e::Receiver adas_rx_{2};
    bool have_brake_ = false;
    bool have_adas_ = false;
    std::uint64_t last_brake_ms_ = 0;
    std::uint64_t last_adas_ms_ = 0;
    bool brake_active_ = false;
    bool adas_warning_ = false;
    bool adas_unavailable_ = false;
    bool adas_emergency_braking_ = false;
    std::uint64_t hazard_until_ms_ = 0;
    std::uint32_t rejected_ = 0;
};

}  // namespace aegis
