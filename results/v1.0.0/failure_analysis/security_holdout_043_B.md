# security_holdout_043_B



Case A06, policy B, seed 986101374; config {'attack': 'A06', 'start_s': 1.9, 'paths': ['primary'], 'delay_ms': 60, 'mode': 'B'}.

Initial ego 56.995 km/h; lead 0.000 km/h; gap 55.421 m; mu 0.714.

Evidence-backed primary group: **counter_gap**. Additional observed classifications: ['freshness_counter_desynchronization', 'native_command_timeout'].

Matched A collision: False. First request 1.06 s; first achieved brake 1.09 s; first rejection 1.92 s; native timeout 2.02 s.

Contact 4.033273 s; relative impact 13.5115 m/s. Verifier decision counts: {'ACCEPT': 2196, 'GAP': 212}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-003, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
