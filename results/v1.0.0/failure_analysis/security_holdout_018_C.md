# security_holdout_018_C



Case A05, policy C, seed 1324359871; config {'attack': 'A05', 'start_s': 1.96, 'paths': ['primary', 'backup'], 'delay_ms': 200, 'mode': 'C'}.

Initial ego 36.003 km/h; lead 0.000 km/h; gap 40.559 m; mu 0.572.

Evidence-backed primary group: **stale_authenticated_delivery**. Additional observed classifications: ['authenticated_delivery_deadline_exceeded', 'native_command_timeout'].

Matched A collision: False. First request 2.28 s; first achieved brake None s; first rejection 2.22 s; native timeout 2.12 s.

Contact 4.055590 s; relative impact 10.0009 m/s. Verifier decision counts: {'ACCEPT': 2200, 'STALE': 184}.

Authentication VALID / freshness REJECT is inferred from the frozen verifier ordering, not from attacker labels. Raw packets, issued/admission/acquisition times and per-step controller/brake/plant state are in the adjacent JSON.

Logical crypto processing delay is zero. Do not attribute this outcome to measured host CPU overhead. All matched A runs avoid collision; withholding and rejection/timeout jointly remove usable demand.

Tests: SEC-ST-005, SEC-UT-002. Affected requirements: SEC-402, FSR-203, TSR-203, BRK-REQ-002.

Mechanism tests can pass while loss of usable commands leaves timely mitigation unachieved; no requirement satisfaction or acceptable risk is inferred.
