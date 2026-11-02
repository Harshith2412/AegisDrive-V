#pragma once
#include <cstring>
#include "aegis/adas_ecu.hpp"
#include "aegis/aegis_types.h"

namespace aegis::test {
// A fresh, plausible, in-ODD input at time now_ms with an object at range/rate.
inline AegisAdasInput nominal(std::uint64_t now_ms, double ego_mps, bool object, double range_m = 100.0,
                              double range_rate_mps = 0.0) {
    AegisAdasInput in{};
    in.now_ms = now_ms;
    in.function_enabled = 1;
    in.ego_speed_valid = 1;
    in.sensor_ok = 1;
    in.object_present = object ? 1 : 0;
    in.ego_speed_mps = ego_mps;
    in.ego_speed_ts_ms = now_ms;
    in.range_m = range_m;
    in.range_rate_mps = range_rate_mps;
    in.meas_ts_ms = now_ms;
    return in;
}
}  // namespace aegis::test
