# Three-minute recorded-demo script (script only; no recording claimed)

0:00–0:25 — Open README and executive summary. Say: “This is a reproducible educational
longitudinal AEB case study, not a certified or production ECU system. The research release
retains known unsafe outcomes rather than using zero collisions as a gate.”

0:25–0:50 — Show architecture and the 64-byte CAN FD security envelope. Explain that native
C++ controls remain behind Python SiL authentication adapters, with public test keys and
trusted clock/FFI assumptions. Backup communication shares physical actuation and security dependencies.

0:50–1:20 — Open results/v1.0.0/failure_analysis/review.md and one JSON timeline. Follow sensor
acquisition, ADAS request, authenticated issued time, rejection reason, native timeout,
achieved deceleration and contact. State the six stale-delivery collisions cannot be rescued
by accepting old messages without weakening the stated policy.

1:20–1:45 — Run `scripts/reviewer.sh reference`; show its generated evidence. If reference
collision/false braking appears, present it as the selected case's measured result, not a demo failure.
Explain same-step newest-authenticated-backup selection and separate diagnostic recovery.

1:45–2:15 — Show evaluation.md: compare only common supported scenarios, then separate protocol
cases that v0.3 cannot execute. Discuss 47/108 candidate collisions, persistent ghosts and
true-obstacle failures from aggressive confirmation. Do not call a stratified count traffic risk.

2:15–2:40 — Show test XML/JSON, scoped coverage, lifecycle_trace.md and model validation.
Explain linked-test PASS vs objective closure, SysML validity vs behavioral correctness,
UBSan pass vs ASan runtime timeout, and partial MC/DC.

2:40–3:00 — Finish on assurance case and open issues. Say: “The contribution is evidence-backed
engineering tradeoff analysis and reviewability, not a claim that authentication solves safety.
Hardware independence, target execution timing, durable keys/state and broader scene validation
remain future work.”
