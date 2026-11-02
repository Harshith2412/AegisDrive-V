# security_holdout_013_B



Case A10, policy B, seed 2035860197; config {'attack': 'A10', 'start_s': 1.45, 'paths': ['primary'], 'delay_ms': 60, 'mode': 'B'}.

Initial ego 61.307 km/h; lead 0.000 km/h; gap 63.036 m; mu 0.465.

Evidence-backed primary group: **rollback_or_replay**. Additional observed classifications: ['restart_or_replay_freshness_rejected', 'native_command_timeout'].

Matched A collision: False. First request 1.09 s; first achieved brake 1.12 s; first rejection 1.47 s; native timeout 1.57 s.

Contact 4.180464 s; relative impact 9.8839 m/s. Verifier decision counts: {'REPLAY': 290, 'ACCEPT': 2208}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-UT-003, REV-PBT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
