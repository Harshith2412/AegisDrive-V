# security_holdout_015_C



Case A08, policy C, seed 1924617167; config {'attack': 'A08', 'start_s': 1.96, 'paths': ['primary', 'backup'], 'delay_ms': 120, 'mode': 'C'}.

Initial ego 50.200 km/h; lead 0.000 km/h; gap 45.371 m; mu 0.801.

Evidence-backed primary group: **stale_authenticated_delivery**. Additional observed classifications: ['authenticated_delivery_deadline_exceeded', 'native_command_timeout'].

Matched A collision: False. First request 1.02 s; first achieved brake 1.05 s; first rejection 2.1 s; native timeout 2.08 s.

Contact 3.885473 s; relative impact 11.1465 m/s. Verifier decision counts: {'ACCEPT': 2323, 'STALE': 358}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-005, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
