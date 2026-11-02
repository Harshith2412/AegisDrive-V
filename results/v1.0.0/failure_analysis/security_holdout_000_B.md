# security_holdout_000_B



Case A06, policy B, seed 1818814175; config {'attack': 'A06', 'start_s': 2.51, 'paths': ['primary', 'backup'], 'delay_ms': 200, 'mode': 'B'}.

Initial ego 70.201 km/h; lead 0.000 km/h; gap 48.243 m; mu 0.568.

Evidence-backed primary group: **counter_gap**. Additional observed classifications: ['freshness_counter_desynchronization', 'native_command_timeout'].

Matched A collision: False. First request 0.0 s; first achieved brake 0.03 s; first rejection 2.53 s; native timeout 2.67 s.

Contact 4.287950 s; relative impact 8.3873 m/s. Verifier decision counts: {'ACCEPT': 2375, 'GAP': 348}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-003, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
