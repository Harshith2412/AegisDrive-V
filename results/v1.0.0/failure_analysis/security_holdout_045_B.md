# security_holdout_045_B



Case A06, policy B, seed 1488964053; config {'attack': 'A06', 'start_s': 2.22, 'paths': ['primary', 'backup'], 'delay_ms': 60, 'mode': 'B'}.

Initial ego 49.562 km/h; lead 0.000 km/h; gap 96.931 m; mu 0.680.

Evidence-backed primary group: **counter_gap**. Additional observed classifications: ['freshness_counter_desynchronization', 'native_command_timeout'].

Matched A collision: False. First request 4.84 s; first achieved brake None s; first rejection 2.23 s; native timeout 2.34 s.

Contact 7.040679 s; relative impact 13.7673 m/s. Verifier decision counts: {'ACCEPT': 3958, 'GAP': 963}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-003, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
