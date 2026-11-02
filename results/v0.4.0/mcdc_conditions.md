# Measured MC/DC condition inventory

LLVM flags identify independent-condition coverage in tool order. False flags are uncovered.
Trivial decisions and tool-excluded constructs are not inferred covered. Tests exercise safety behavior, not rewritten expressions.

| File / line | Covered / conditions | Coverage flags | Decision source |
|---|---|---|---|
| ecu/src/adas_ecu.cpp:56 | 8 / 8 | [True, True, True, True, True, True, True, True] |     const bool finite = std::isfinite(c.ttc_warning_s) && std::isfinite(c.ttc_brake_s) &&                         std::isfinite(c.ttc_hysteresis_s) && std::isfinite(c.stop_margin_m) &&                         std::isfinite(c.min_active_speed_mps) && std::isfinite(c.standstill_speed_mps) &&                         std::isfinite(c.max_active_speed_mps) && std::isfinite(c.max_brake_decel_mps2); |
| ecu/src/adas_ecu.cpp:60 | 4 / 4 | [True, True, True, True] |     if (!finite &#124;&#124; !std::isfinite(c.planning_decel_mps2) &#124;&#124; c.planning_decel_mps2 < 0.0 &#124;&#124;         c.planning_decel_mps2 > c.max_brake_decel_mps2) return false; |
| ecu/src/adas_ecu.cpp:62 | 20 / 22 | [False, True, True, True, True, True, True, True, False, True, True, True, True, True, True, True, True, True, True, True, True, True] |     return finite_pos(c.ttc_brake_s) && c.ttc_brake_s < c.ttc_warning_s &&            c.ttc_hysteresis_s >= 0.0 && finite_pos(c.min_closing_speed_mps) &&            c.stop_margin_m >= 0.0 && finite_pos(c.decel_gain) &&            finite_pos(c.min_brake_decel_mps2) && c.min_brake_decel_mps2 <= c.max_brake_decel_mps2 &&            c.max_brake_decel_mps2 <= 10.0 && finite_pos(c.emergency_decel_mps2) &&            c.emergency_decel_mps2 <= c.max_brake_decel_mps2 && c.min_active_speed_mps >= 0.0 &&            c.min_active_speed_mps < c.max_active_speed_mps &&            c.max_active_speed_mps <= c.max_ego_speed_mps && c.standstill_speed_mps >= 0.0 &&            c.standstill_speed_mps < c.min_active_speed_mps && finite_pos(c.max_range_m) &&            finite_pos(c.max_abs_range_rate_mps) && finite_pos(c.max_ego_speed_mps) &&            c.stale_timeout_ms > 0 && c.recovery_cycles >= 1 && c.degraded_to_fault_ms > 0; |
| ecu/src/adas_ecu.cpp:100 | 0 / 2 | [False, False] |     if (f >= AEGIS_ADAS_NUM_STATES &#124;&#124; t >= AEGIS_ADAS_NUM_STATES) return false; |
| ecu/src/adas_ecu.cpp:106 | 1 / 2 | [False, True] |     if (!config_ok_ &#124;&#124; !transition_allowed(state_, to)) { |
| ecu/src/adas_ecu.cpp:118 | 1 / 2 | [False, True] |     return ts <= now && (now - ts) <= cfg_.stale_timeout_ms; |
| ecu/src/adas_ecu.cpp:123 | 3 / 4 | [True, True, True, False] |     const bool finite = std::isfinite(in.ego_speed_mps) &&                         (!in.object_present &#124;&#124; (std::isfinite(in.range_m) && std::isfinite(in.range_rate_mps))); |
| ecu/src/adas_ecu.cpp:134 | 1 / 2 | [False, True] |     if (in.ego_speed_mps < 0.0 &#124;&#124; in.ego_speed_mps > cfg_.max_ego_speed_mps) f &#124;= AEGIS_DTC_IMPLAUSIBLE_INPUT; |
| ecu/src/adas_ecu.cpp:144 | 2 / 2 | [True, True] |         if (in.range_m < 0.0 &#124;&#124; in.range_m > cfg_.max_range_m) f &#124;= AEGIS_DTC_IMPLAUSIBLE_INPUT; |
| ecu/src/adas_ecu.cpp:152 | 2 / 2 | [True, True] |     const bool in_window = v >= cfg_.min_active_speed_mps && v <= cfg_.max_active_speed_mps; |
| ecu/src/adas_ecu.cpp:160 | 3 / 3 | [True, True, True] |     if (in.object_present && (!have_lead_speed_ &#124;&#124; in.meas_ts_ms != previous_meas_ms_)) { |
| ecu/src/adas_ecu.cpp:161 | 1 / 3 | [True, False, False] |         if (have_lead_speed_ && in.meas_ts_ms > previous_meas_ms_ &&             in.meas_ts_ms - previous_meas_ms_ <= cfg_.stale_timeout_ms) { |
| ecu/src/adas_ecu.cpp:171 | 3 / 3 | [True, True, True] |     const bool envelope_threat = in.object_present && closing > cfg_.min_closing_speed_mps &&                                  in.range_m <= envelope; |
| ecu/src/adas_ecu.cpp:174 | 2 / 2 | [True, True] |     if (state_ == AdasState::Standby && in_window) request_transition(AdasState::Monitoring); |
| ecu/src/adas_ecu.cpp:179 | 2 / 2 | [True, True] |             else if (ttc <= cfg_.ttc_brake_s &#124;&#124; envelope_threat) request_transition(AdasState::Braking); |
| ecu/src/adas_ecu.cpp:184 | 2 / 2 | [True, True] |             else if (ttc <= cfg_.ttc_brake_s &#124;&#124; envelope_threat) request_transition(AdasState::Braking); |
| ecu/src/adas_ecu.cpp:200 | 4 / 4 | [True, True, True, True] |             const bool closing_now = in.object_present &&                 (closing >= -0.5 &#124;&#124; in.range_m <= envelope + cfg_.stop_margin_m &#124;&#124; lead_accel_ < -0.3); |
| ecu/src/adas_ecu.cpp:202 | 2 / 2 | [True, True] |             if (!closing_now && !standstill) { |
| ecu/src/adas_ecu.cpp:302 | 6 / 6 | [True, True, True, True, True, True] |         const bool valid = in.achieved_valid && std::isfinite(in.achieved_decel_mps2) &&             in.achieved_decel_mps2 >= 0.0 && in.achieved_decel_mps2 <= 15.0 &&             in.achieved_ts_ms <= in.now_ms && in.now_ms - in.achieved_ts_ms <= 100; |
| ecu/src/adas_ecu.cpp:307 | 6 / 7 | [True, True, True, True, False, True, True] |         const bool mismatch = valid && state_ == AdasState::Braking &&             in.ego_speed_mps > cfg_.standstill_speed_mps && demand_timing_ &&             in.now_ms >= demand_since_ms_ && in.now_ms - demand_since_ms_ > 300 &&             in.achieved_decel_mps2 < minimum; |
| ecu/src/adas_ecu.cpp:317 | 2 / 2 | [True, True] |         if (in.achieved_monitor_enabled && state_ == AdasState::Braking) { |
| ecu/src/adas_ecu.cpp:326 | 1 / 2 | [True, False] |     if (in.brake_status_present && in.brake_status_dlc == AEGIS_CAN_DLC) { |
| ecu/src/adas_ecu.cpp:328 | 1 / 3 | [True, False, False] |         if (feedback_rx_.check(AEGIS_CAN_ID_BRAKE_STATUS, in.brake_status_frame) == e2e::Check::Ok &&             codec::decode_brake_status(in.brake_status_frame, st) && st.actual_decel_mps2 <= 15.0) { |
| ecu/src/adas_ecu.cpp:331 | 3 / 3 | [True, True, True] |             if (st.ack_valid && (!have_ack_ &#124;&#124; st.ack_counter != last_ack_)) { |
| ecu/src/adas_ecu.cpp:336 | 2 / 2 | [True, True] |             if (st.timeout &#124;&#124; st.rejecting) feedback_fault_ = true; |
| ecu/src/adas_ecu.cpp:337 | 3 / 4 | [True, False, True, True] |             if (demand_timing_ && in.now_ms >= demand_since_ms_ &&                 in.now_ms - demand_since_ms_ > 300 && !st.active) feedback_fault_ = true; |
| ecu/src/adas_ecu.cpp:344 | 2 / 4 | [False, False, True, True] |     if (in.now_ms < last_feedback_ms_ &#124;&#124; in.now_ms < last_ack_ms_ &#124;&#124;         in.now_ms - last_feedback_ms_ > 100 &#124;&#124; in.now_ms - last_ack_ms_ > 100) |
| ecu/src/adas_ecu.cpp:351 | 2 / 2 | [True, True] |     out.warning_active = (state_ == AdasState::Warning &#124;&#124; state_ == AdasState::Braking) ? 1 : 0; |
| ecu/src/adas_ecu.cpp:353 | 2 / 2 | [True, True] |     out.function_unavailable = (state_ == AdasState::Degraded &#124;&#124; state_ == AdasState::Fault) ? 1 : 0; |
| ecu/src/adas_ecu.cpp:355 | 2 / 2 | [True, True] |     out.emergency = (out.brake_request_active && out.decel_request_mps2 >= cfg_.emergency_decel_mps2) ? 1 : 0; |
| ecu/src/adas_ecu.cpp:356 | 3 / 3 | [True, True, True] |     out.standstill = (in.ego_speed_valid && std::isfinite(in.ego_speed_mps) &&                       in.ego_speed_mps <= cfg_.standstill_speed_mps) ? 1 : 0; |
| ecu/src/adas_ecu.cpp:14 | 2 / 2 | [True, True] | bool finite_pos(double v) { return std::isfinite(v) && v > 0.0; } |
| ecu/src/aegis_c_api.cpp:39 | 0 / 2 | [False, False] |     return (cfg && aegis::adas_config_valid(*cfg)) ? 1 : 0; |
| ecu/src/aegis_c_api.cpp:47 | 0 / 3 | [False, False, False] |     if (!h &#124;&#124; !in &#124;&#124; !out) return -1; |
| ecu/src/aegis_c_api.cpp:55 | 0 / 2 | [False, False] |     if (!h &#124;&#124; to >= AEGIS_ADAS_NUM_STATES) return 0; |
| ecu/src/aegis_c_api.cpp:59 | 0 / 2 | [False, False] |     if (from >= AEGIS_ADAS_NUM_STATES &#124;&#124; to >= AEGIS_ADAS_NUM_STATES) return 0; |
| ecu/src/aegis_c_api.cpp:75 | 0 / 3 | [False, False, False] |     if (!h &#124;&#124; !in &#124;&#124; !out) return -1; |
| ecu/src/aegis_c_api.cpp:87 | 0 / 3 | [False, False, False] |     if (!h &#124;&#124; !in &#124;&#124; !out) return -1; |
| ecu/src/body_ecu.cpp:24 | 1 / 2 | [True, False] |         if (c == e2e::Check::Ok && codec::decode_brake_status(in.brake_status_frame, bs)) { |
| ecu/src/body_ecu.cpp:37 | 1 / 2 | [True, False] |         if (c == e2e::Check::Ok && codec::decode_adas_status(in.adas_status_frame, as)) { |
| ecu/src/body_ecu.cpp:40 | 1 / 2 | [True, False] |             adas_emergency_braking_ = as.emergency && as.state == AEGIS_ADAS_BRAKING; |
| ecu/src/body_ecu.cpp:48 | 2 / 3 | [True, False, True] |     const bool brake_to = !have_brake_ &#124;&#124; in.now_ms < last_brake_ms_ &#124;&#124; in.now_ms - last_brake_ms_ > cfg_.timeout_ms; |
| ecu/src/body_ecu.cpp:49 | 2 / 3 | [True, False, True] |     const bool adas_to = !have_adas_ &#124;&#124; in.now_ms < last_adas_ms_ &#124;&#124; in.now_ms - last_adas_ms_ > cfg_.timeout_ms; |
| ecu/src/body_ecu.cpp:53 | 2 / 2 | [True, True] |     out.warning_indicator = (!adas_to && adas_warning_) ? 1 : 0; |
| ecu/src/body_ecu.cpp:54 | 2 / 2 | [True, True] |     out.aeb_unavailable_indicator = (adas_to &#124;&#124; adas_unavailable_) ? 1 : 0; |
| ecu/src/body_ecu.cpp:56 | 2 / 2 | [True, True] |     if (!adas_to && adas_emergency_braking_) hazard_until_ms_ = in.now_ms + cfg_.hazard_hold_ms; |
| ecu/src/brake_ecu.cpp:20 | 0 / 10 | [False, False, False, False, False, False, False, False, False, False] |     return c.timeout_ms > 0 && c.max_counter_delta >= 1 && c.max_counter_delta <= 14 &&            std::isfinite(c.max_decel_mps2) && c.max_decel_mps2 > 0.0 && c.max_decel_mps2 <= 15.0 &&            std::isfinite(c.actuator_tau_s) && c.actuator_tau_s > 0.0 &&            std::isfinite(c.active_threshold_mps2) && c.active_threshold_mps2 > 0.0; |
| ecu/src/brake_ecu.cpp:73 | 2 / 2 | [True, True] |         if (primary_act &#124;&#124; backup_act) { |
| ecu/src/brake_ecu.cpp:82 | 2 / 3 | [True, False, True] |     const bool timed_out = !have_valid_ &#124;&#124; in.now_ms < last_valid_ms_ &#124;&#124;                            (in.now_ms - last_valid_ms_) > cfg_.timeout_ms; |
| ecu/src/brake_ecu.cpp:84 | 2 / 3 | [False, True, True] |     const double aeb = (config_ok_ && !timed_out && cmd_active_) ? cmd_decel_ : 0.0; |
| ecu/src/brake_ecu.cpp:91 | 1 / 3 | [True, False, False] |     const bool dt_ok = std::isfinite(in.dt_s) && in.dt_s > 0.0 && in.dt_s <= 0.1; |
| ecu/src/brake_ecu.cpp:92 | 1 / 2 | [True, False] |     if (dt_ok && config_ok_) { |
| ecu/src/brake_ecu.cpp:113 | 3 / 3 | [True, True, True] |     st.rejecting = in.frame_present && !out.frame_accepted && last_reject_ != AEGIS_REJ_NONE; |
| ecu/src/codec.cpp:31 | 1 / 5 | [False, False, False, True, False] |     if ((f[1] & 0xF0u) &#124;&#124; (f[2] & 0xFCu) &#124;&#124; f[5] &#124;&#124; f[6] &#124;&#124; f[7]) return AEGIS_REJ_RESERVED_BITS; |
| ecu/src/codec.cpp:37 | 2 / 3 | [True, True, False] |     if (!active && (raw != 0 &#124;&#124; emergency)) return AEGIS_REJ_INCONSISTENT; |
| ecu/src/codec.cpp:38 | 2 / 2 | [True, True] |     if (active && raw == 0) return AEGIS_REJ_INCONSISTENT; |
| ecu/src/codec.cpp:54 | 0 / 6 | [False, False, False, False, False, False] |     if ((f[1] & 0xF0u) &#124;&#124; (f[3] & 0xF0u) &#124;&#124; f[4] &#124;&#124; f[5] &#124;&#124; f[6] &#124;&#124; f[7]) return false; |
| ecu/src/codec.cpp:75 | 0 / 5 | [False, False, False, False, False] |     if ((f[1] & 0xF0u) &#124;&#124; (f[2] & 0xF8u) &#124;&#124; (f[5] & 0xFEu) &#124;&#124; (f[6] & 0xF0u) &#124;&#124; f[7]) return false; |
