# security_holdout_007_B



Case A10, policy B, seed 507086606; config {'attack': 'A10', 'start_s': 1.34, 'paths': ['primary'], 'delay_ms': 200, 'mode': 'B'}.

Initial ego 68.054 km/h; lead 0.000 km/h; gap 72.967 m; mu 0.385.

Evidence-backed primary group: **rollback_or_replay**. Additional observed classifications: ['restart_or_replay_freshness_rejected', 'native_command_timeout'].

Matched A collision: False. First request 1.05 s; first achieved brake 1.12 s; first rejection 1.4 s; native timeout 1.5 s.

Contact 4.333757 s; relative impact 11.6315 m/s. Verifier decision counts: {'REPLAY': 268, 'ACCEPT': 2304}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-UT-003, REV-PBT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
