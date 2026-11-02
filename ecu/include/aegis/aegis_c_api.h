/*
 * AegisDrive-V — restricted C ABI over the C++ ECU core.
 * Used by the Python simulation (ctypes) and suitable as a seed for an
 * embedded-style interface. Handles are allocated once at creation; the
 * step functions perform no allocation.
 */
#ifndef AEGIS_C_API_H
#define AEGIS_C_API_H

#include <stddef.h>
#include "aegis/aegis_types.h"

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
#define AEGIS_API __declspec(dllexport)
#else
#define AEGIS_API __attribute__((visibility("default")))
#endif

typedef struct AegisAdasHandle AegisAdasHandle;
typedef struct AegisBrakeHandle AegisBrakeHandle;
typedef struct AegisBodyHandle AegisBodyHandle;

/* Struct identifiers for ABI layout checking. */
#define AEGIS_STRUCT_ADAS_CONFIG  0
#define AEGIS_STRUCT_ADAS_INPUT   1
#define AEGIS_STRUCT_ADAS_OUTPUT  2
#define AEGIS_STRUCT_BRAKE_CONFIG 3
#define AEGIS_STRUCT_BRAKE_INPUT  4
#define AEGIS_STRUCT_BRAKE_OUTPUT 5
#define AEGIS_STRUCT_BODY_CONFIG  6
#define AEGIS_STRUCT_BODY_INPUT   7
#define AEGIS_STRUCT_BODY_OUTPUT  8

AEGIS_API uint32_t aegis_abi_version(void);
AEGIS_API size_t aegis_struct_size(int which); /* 0 for unknown id */
AEGIS_API uint8_t aegis_crc8_j1850(const uint8_t* data, size_t len);

AEGIS_API AegisAdasConfig aegis_adas_default_config(void);
AEGIS_API int aegis_adas_config_valid(const AegisAdasConfig* cfg);
AEGIS_API AegisAdasHandle* aegis_adas_create(const AegisAdasConfig* cfg);
AEGIS_API void aegis_adas_destroy(AegisAdasHandle* h);
AEGIS_API int aegis_adas_step(AegisAdasHandle* h, const AegisAdasInput* in, AegisAdasOutput* out);
AEGIS_API uint8_t aegis_adas_state(const AegisAdasHandle* h);
AEGIS_API int aegis_adas_request_transition(AegisAdasHandle* h, uint8_t to_state);
AEGIS_API int aegis_adas_transition_allowed(uint8_t from_state, uint8_t to_state);
AEGIS_API double aegis_compute_ttc(double range_m, double range_rate_mps, double min_closing_mps);
AEGIS_API double aegis_compute_required_decel(double range_m, double range_rate_mps, double margin_m);

AEGIS_API AegisBrakeConfig aegis_brake_default_config(void);
AEGIS_API AegisBrakeHandle* aegis_brake_create(const AegisBrakeConfig* cfg);
AEGIS_API void aegis_brake_destroy(AegisBrakeHandle* h);
AEGIS_API int aegis_brake_step(AegisBrakeHandle* h, const AegisBrakeInput* in, AegisBrakeOutput* out);

AEGIS_API AegisBodyConfig aegis_body_default_config(void);
AEGIS_API AegisBodyHandle* aegis_body_create(const AegisBodyConfig* cfg);
AEGIS_API void aegis_body_destroy(AegisBodyHandle* h);
AEGIS_API int aegis_body_step(AegisBodyHandle* h, const AegisBodyInput* in, AegisBodyOutput* out);

#ifdef __cplusplus
}
#endif
#endif /* AEGIS_C_API_H */
