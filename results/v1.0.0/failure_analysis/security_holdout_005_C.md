# security_holdout_005_C



Case A02, policy C, seed 250234273; config {'attack': 'A02', 'start_s': 2.46, 'paths': ['primary'], 'delay_ms': 120, 'mode': 'C'}.

Initial ego 23.291 km/h; lead 0.000 km/h; gap 95.941 m; mu 0.391.

Evidence-backed primary group: **stale_authenticated_delivery**. Additional observed classifications: ['authenticated_delivery_deadline_exceeded', 'native_command_timeout'].

Matched A collision: False. First request 13.23 s; first achieved brake None s; first rejection 2.48 s; native timeout 2.58 s.

Contact 14.829274 s; relative impact 6.4697 m/s. Verifier decision counts: {'ACCEPT': 7647, 'STALE': 1235}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-005, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
