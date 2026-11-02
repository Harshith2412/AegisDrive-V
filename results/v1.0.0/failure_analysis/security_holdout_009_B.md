# security_holdout_009_B



Case A02, policy B, seed 155865093; config {'attack': 'A02', 'start_s': 1.87, 'paths': ['primary', 'backup'], 'delay_ms': 200, 'mode': 'B'}.

Initial ego 24.023 km/h; lead 0.000 km/h; gap 35.457 m; mu 0.610.

Evidence-backed primary group: **stale_authenticated_delivery**. Additional observed classifications: ['authenticated_delivery_deadline_exceeded', 'native_command_timeout'].

Matched A collision: False. First request 3.71 s; first achieved brake None s; first rejection 1.88 s; native timeout 1.98 s.

Contact 5.313521 s; relative impact 6.6730 m/s. Verifier decision counts: {'ACCEPT': 2836, 'STALE': 344}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-005, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
