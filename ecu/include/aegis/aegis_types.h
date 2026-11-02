/*
 * AegisDrive-V — C-compatible ECU interface types.
 *
 * These plain-old-data structs are the single definition of the ECU I/O
 * contract. They are used directly by the C++ ECU core and exported through the
 * restricted C ABI (aegis_c_api.h) so that the Python simulation calls the real
 * compiled algorithms (no duplicated Python implementation of ECU logic).
 *
 * Conventions:
 *   - Units are encoded in field names (_m, _mps, _mps2, _s, _ms).
 *   - Booleans are uint8_t (0 = false, 1 = true) for a stable C ABI.
 *   - Deceleration values are POSITIVE magnitudes (m/s^2).
 *   - range_rate_mps is d(range)/dt: NEGATIVE when the gap is closing.
 *
 * SIMULATION ONLY — not production automotive software.
 */
#ifndef AEGIS_TYPES_H
#define AEGIS_TYPES_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define AEGIS_ABI_VERSION 4u
#define AEGIS_CAN_DLC 8u

/* ---- CAN identifiers (11-bit, classic CAN in the vertical slice) ---- */
#define AEGIS_CAN_ID_BRAKE_REQ    0x120u /* ADAS ECU  -> Brake ECU  */
#define AEGIS_CAN_ID_ADAS_STATUS  0x130u /* ADAS ECU  -> Body ECU   */
#define AEGIS_CAN_ID_BRAKE_STATUS 0x220u /* Brake ECU -> Body ECU   */

/* ---- ADAS states ---- */
#define AEGIS_ADAS_DISABLED   0u
#define AEGIS_ADAS_STANDBY    1u
#define AEGIS_ADAS_MONITORING 2u
#define AEGIS_ADAS_WARNING    3u
#define AEGIS_ADAS_BRAKING    4u
#define AEGIS_ADAS_DEGRADED   5u
#define AEGIS_ADAS_FAULT      6u
#define AEGIS_ADAS_NUM_STATES 7u

/* ---- ADAS diagnostic flags (dtc_flags bitfield) ---- */
#define AEGIS_DTC_STALE_INPUT          (1u << 0)
#define AEGIS_DTC_IMPLAUSIBLE_INPUT    (1u << 1)
#define AEGIS_DTC_SENSOR_NOT_OK        (1u << 2)
#define AEGIS_DTC_EGO_SPEED_INVALID    (1u << 3)
#define AEGIS_DTC_ILLEGAL_TRANSITION   (1u << 4) /* latched */
#define AEGIS_DTC_PERSISTENT_DEGRADED  (1u << 5) /* latched */
#define AEGIS_DTC_NONFINITE_INPUT      (1u << 6)
#define AEGIS_DTC_INVALID_CONFIG       (1u << 7) /* latched */

#define AEGIS_DTC_SECURITY_EVENT (1u << 10) /* latched diagnostic, not a braking decision */
#define AEGIS_DTC_ACHIEVED_DECEL (1u << 9)
#define AEGIS_DTC_BRAKE_FEEDBACK (1u << 8) /* latched until disable */

/* ---- Brake ECU status ---- */
#define AEGIS_BRK_STATUS_NO_SYNC 0u /* no valid request received yet */
#define AEGIS_BRK_STATUS_OK      1u
#define AEGIS_BRK_STATUS_TIMEOUT 2u

/* ---- Brake ECU frame rejection reasons ---- */
#define AEGIS_REJ_NONE           0u
#define AEGIS_REJ_WRONG_ID       1u
#define AEGIS_REJ_BAD_DLC        2u
#define AEGIS_REJ_CRC            3u
#define AEGIS_REJ_REPEATED       4u
#define AEGIS_REJ_SEQUENCE       5u
#define AEGIS_REJ_RANGE          6u
#define AEGIS_REJ_RESERVED_BITS  7u
#define AEGIS_REJ_INCONSISTENT   8u

typedef struct {
    double   ttc_warning_s;               /* enter WARNING when TTC <= this */
    double   ttc_brake_s;                 /* enter BRAKING when TTC <= this */
    double   ttc_hysteresis_s;            /* WARNING -> MONITORING when TTC > warn + hyst */
    double   min_closing_speed_mps;       /* below this, TTC is treated as infinite */
    double   stop_margin_m;               /* desired residual gap for required-decel calc */
    double   decel_gain;                  /* multiplier on required deceleration */
    double   min_brake_decel_mps2;        /* lower clamp of AEB deceleration request */
    double   max_brake_decel_mps2;        /* upper clamp of AEB deceleration request */
    double   emergency_decel_mps2;        /* request >= this sets the emergency flag */
    double   min_active_speed_mps;        /* lower edge of activation speed window */
    double   max_active_speed_mps;        /* upper edge of activation speed window */
    double   standstill_speed_mps;        /* ego speed considered standstill */
    double   max_range_m;                 /* plausibility: max object range */
    double   max_abs_range_rate_mps;      /* plausibility: max |range rate| */
    double   max_ego_speed_mps;           /* plausibility: max ego speed */
    uint32_t stale_timeout_ms;            /* input age above this is stale */
    uint32_t standstill_hold_ms;          /* hold brake at standstill before release */
    uint32_t threat_clear_ms;             /* non-closing duration to abort braking */
    uint32_t degraded_to_fault_ms;        /* continuous DEGRADED time before FAULT */
    uint32_t recovery_cycles;             /* consecutive valid cycles to leave DEGRADED */
    double planning_decel_mps2; /* stopping envelope; 0 disables for TTC isolation */
} AegisAdasConfig;

typedef struct {
    uint64_t now_ms;              /* ECU local time at this execution step */
    uint8_t  function_enabled;    /* driver/HMI AEB enable switch */
    uint8_t  ego_speed_valid;
    uint8_t  sensor_ok;           /* perception reports itself healthy */
    uint8_t  object_present;      /* a relevant in-path object is reported */
    uint8_t  reserved0[4];
    double   ego_speed_mps;
    uint64_t ego_speed_ts_ms;     /* timestamp of ego-speed sample */
    double   range_m;             /* bumper-to-bumper gap to in-path object */
    double   range_rate_mps;      /* d(range)/dt, negative when closing */
    uint64_t meas_ts_ms;          /* timestamp of perception measurement */
    uint8_t feedback_monitor_enabled; /* installation enables closed-loop supervision */
    uint8_t brake_status_present;
    uint8_t brake_status_dlc;
    uint8_t brake_status_frame[AEGIS_CAN_DLC];
    uint8_t achieved_monitor_enabled;
    uint8_t achieved_valid;
    double achieved_decel_mps2;
    uint64_t achieved_ts_ms;
    uint8_t security_event; /* local verified gateway diagnostic indication */
} AegisAdasInput;

typedef struct {
    uint8_t  state;                  /* AEGIS_ADAS_* */
    uint8_t  warning_active;
    uint8_t  brake_request_active;
    uint8_t  function_unavailable;
    uint8_t  emergency;              /* current decel request >= emergency threshold */
    uint8_t  standstill;
    uint8_t  reserved0[2];
    uint32_t dtc_flags;              /* AEGIS_DTC_* (current + latched) */
    uint32_t illegal_transition_count;
    double   ttc_s;                  /* +inf when not closing */
    double   required_decel_mps2;    /* kinematic decel to stop with margin */
    double   decel_request_mps2;     /* AEB deceleration request (0 if inactive) */
    uint8_t  brake_req_frame[AEGIS_CAN_DLC];   /* encoded CAN 0x120 payload */
    uint8_t  adas_status_frame[AEGIS_CAN_DLC]; /* encoded CAN 0x130 payload */
} AegisAdasOutput;

typedef struct {
    uint32_t timeout_ms;            /* release AEB request if no valid frame */
    uint32_t max_counter_delta;     /* E2E-style tolerated counter jump (lost frames) */
    double   max_decel_mps2;        /* accepted command range upper bound */
    double   actuator_tau_s;        /* first-order brake build-up time constant */
    double   active_threshold_mps2; /* actual decel above this => brake active */
} AegisBrakeConfig;

typedef struct {
    uint64_t now_ms;
    double   dt_s;                  /* time since previous step */
    double   driver_brake_mps2;     /* driver pedal demand (decel magnitude) */
    uint32_t can_id;
    uint8_t  frame_present;
    uint8_t  frame_dlc;
    uint8_t  frame[AEGIS_CAN_DLC];
    uint8_t  reserved0[2];
    uint8_t backup_present;
    uint8_t backup_dlc;
    uint8_t backup_frame[AEGIS_CAN_DLC];
} AegisBrakeInput;

typedef struct {
    double   aeb_target_decel_mps2;  /* AEB demand after validation/timeout */
    double   target_decel_mps2;      /* after driver/AEB arbitration */
    double   actual_decel_mps2;      /* simulated actuator output */
    uint8_t  brake_active;
    uint8_t  status;                 /* AEGIS_BRK_STATUS_* */
    uint8_t  last_reject_reason;     /* AEGIS_REJ_* */
    uint8_t  frame_accepted;         /* this step accepted a command frame */
    uint32_t accepted_frames;
    uint32_t rejected_frames;
    uint8_t  reserved0[4];
    uint8_t  status_frame[AEGIS_CAN_DLC];      /* encoded CAN 0x220 payload */
} AegisBrakeOutput;

typedef struct {
    uint32_t timeout_ms;            /* input frame timeout */
    uint32_t hazard_hold_ms;        /* hazard lamps hold after emergency braking */
} AegisBodyConfig;

typedef struct {
    uint64_t now_ms;
    uint8_t  brake_status_present;
    uint8_t  brake_status_dlc;
    uint8_t  adas_status_present;
    uint8_t  adas_status_dlc;
    uint8_t  brake_status_frame[AEGIS_CAN_DLC];
    uint8_t  adas_status_frame[AEGIS_CAN_DLC];
    uint8_t  reserved0[4];
} AegisBodyInput;

typedef struct {
    uint8_t  brake_lamp;
    uint8_t  warning_indicator;          /* forward collision warning telltale */
    uint8_t  aeb_unavailable_indicator;  /* function unavailable / comms lost */
    uint8_t  hazard_lamps;
    uint8_t  fault_brake_status_timeout;
    uint8_t  fault_adas_status_timeout;
    uint8_t  reserved0[2];
    uint32_t rejected_frames;
} AegisBodyOutput;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* AEGIS_TYPES_H */
