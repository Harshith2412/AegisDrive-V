# security_holdout_002_B



Case A02, policy B, seed 480645093; config {'attack': 'A02', 'start_s': 1.45, 'paths': ['primary'], 'delay_ms': 60, 'mode': 'B'}.

Initial ego 61.543 km/h; lead 0.000 km/h; gap 72.181 m; mu 0.518.

Evidence-backed primary group: **stale_authenticated_delivery**. Additional observed classifications: ['authenticated_delivery_deadline_exceeded', 'native_command_timeout'].

Matched A collision: False. First request 1.62 s; first achieved brake None s; first rejection 1.47 s; native timeout 1.57 s.

Contact 4.222246 s; relative impact 17.0954 m/s. Verifier decision counts: {'ACCEPT': 2246, 'STALE': 276}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-005, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
