#include "aegis/aegis_c_api.h"

#include <new>

#include "aegis/adas_ecu.hpp"
#include "aegis/body_ecu.hpp"
#include "aegis/brake_ecu.hpp"
#include "aegis/e2e.hpp"

struct AegisAdasHandle { aegis::AdasEcu ecu; };
struct AegisBrakeHandle { aegis::BrakeEcu ecu; };
struct AegisBodyHandle { aegis::BodyEcu ecu; };

extern "C" {

uint32_t aegis_abi_version(void) { return AEGIS_ABI_VERSION; }

size_t aegis_struct_size(int which) {
    switch (which) {
        case AEGIS_STRUCT_ADAS_CONFIG: return sizeof(AegisAdasConfig);
        case AEGIS_STRUCT_ADAS_INPUT: return sizeof(AegisAdasInput);
        case AEGIS_STRUCT_ADAS_OUTPUT: return sizeof(AegisAdasOutput);
        case AEGIS_STRUCT_BRAKE_CONFIG: return sizeof(AegisBrakeConfig);
        case AEGIS_STRUCT_BRAKE_INPUT: return sizeof(AegisBrakeInput);
        case AEGIS_STRUCT_BRAKE_OUTPUT: return sizeof(AegisBrakeOutput);
        case AEGIS_STRUCT_BODY_CONFIG: return sizeof(AegisBodyConfig);
        case AEGIS_STRUCT_BODY_INPUT: return sizeof(AegisBodyInput);
        case AEGIS_STRUCT_BODY_OUTPUT: return sizeof(AegisBodyOutput);
        default: return 0;
    }
}

uint8_t aegis_crc8_j1850(const uint8_t* data, size_t len) {
    return data ? aegis::e2e::crc8_j1850(data, len) : 0;
}

AegisAdasConfig aegis_adas_default_config(void) { return aegis::default_adas_config(); }
int aegis_adas_config_valid(const AegisAdasConfig* cfg) {
    return (cfg && aegis::adas_config_valid(*cfg)) ? 1 : 0;
}
AegisAdasHandle* aegis_adas_create(const AegisAdasConfig* cfg) {
    const AegisAdasConfig c = cfg ? *cfg : aegis::default_adas_config();
    return new (std::nothrow) AegisAdasHandle{aegis::AdasEcu(c)};
}
void aegis_adas_destroy(AegisAdasHandle* h) { delete h; }
int aegis_adas_step(AegisAdasHandle* h, const AegisAdasInput* in, AegisAdasOutput* out) {
    if (!h || !in || !out) return -1;
    *out = h->ecu.step(*in);
    return 0;
}
uint8_t aegis_adas_state(const AegisAdasHandle* h) {
    return h ? static_cast<uint8_t>(h->ecu.state()) : static_cast<uint8_t>(AEGIS_ADAS_FAULT);
}
int aegis_adas_request_transition(AegisAdasHandle* h, uint8_t to) {
    if (!h || to >= AEGIS_ADAS_NUM_STATES) return 0;
    return h->ecu.request_transition(static_cast<aegis::AdasState>(to)) ? 1 : 0;
}
int aegis_adas_transition_allowed(uint8_t from, uint8_t to) {
    if (from >= AEGIS_ADAS_NUM_STATES || to >= AEGIS_ADAS_NUM_STATES) return 0;
    return aegis::AdasEcu::transition_allowed(static_cast<aegis::AdasState>(from),
                                              static_cast<aegis::AdasState>(to)) ? 1 : 0;
}
double aegis_compute_ttc(double r, double rr, double m) { return aegis::compute_ttc(r, rr, m); }
double aegis_compute_required_decel(double r, double rr, double m) {
    return aegis::compute_required_decel(r, rr, m);
}

AegisBrakeConfig aegis_brake_default_config(void) { return aegis::default_brake_config(); }
AegisBrakeHandle* aegis_brake_create(const AegisBrakeConfig* cfg) {
    const AegisBrakeConfig c = cfg ? *cfg : aegis::default_brake_config();
    return new (std::nothrow) AegisBrakeHandle{aegis::BrakeEcu(c)};
}
void aegis_brake_destroy(AegisBrakeHandle* h) { delete h; }
int aegis_brake_step(AegisBrakeHandle* h, const AegisBrakeInput* in, AegisBrakeOutput* out) {
    if (!h || !in || !out) return -1;
    *out = h->ecu.step(*in);
    return 0;
}

AegisBodyConfig aegis_body_default_config(void) { return aegis::default_body_config(); }
AegisBodyHandle* aegis_body_create(const AegisBodyConfig* cfg) {
    const AegisBodyConfig c = cfg ? *cfg : aegis::default_body_config();
    return new (std::nothrow) AegisBodyHandle{aegis::BodyEcu(c)};
}
void aegis_body_destroy(AegisBodyHandle* h) { delete h; }
int aegis_body_step(AegisBodyHandle* h, const AegisBodyInput* in, AegisBodyOutput* out) {
    if (!h || !in || !out) return -1;
    *out = h->ecu.step(*in);
    return 0;
}

}  // extern "C"
