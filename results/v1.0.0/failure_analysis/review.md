# Independent security-collision review

18 individual reports; groups: {'B:counter_gap': 4, 'B:stale_authenticated_delivery': 6, 'C:stale_authenticated_delivery': 6, 'B:rollback_or_replay': 2}.

All matched A runs avoid collision; these are withholding/rejection/timeout interactions, not simulated CPU delays or unrelated baseline collisions.

| Failure | Primary cause | Mechanism tests |
|---|---|---|
| [security_holdout_000_B](security_holdout_000_B.md) | counter_gap | SEC-ST-003, SEC-UT-002 |
| [security_holdout_002_B](security_holdout_002_B.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_002_C](security_holdout_002_C.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_005_B](security_holdout_005_B.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_005_C](security_holdout_005_C.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_007_B](security_holdout_007_B.md) | rollback_or_replay | SEC-UT-003, REV-PBT-002 |
| [security_holdout_009_B](security_holdout_009_B.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_009_C](security_holdout_009_C.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_013_B](security_holdout_013_B.md) | rollback_or_replay | SEC-UT-003, REV-PBT-002 |
| [security_holdout_015_B](security_holdout_015_B.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_015_C](security_holdout_015_C.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_018_B](security_holdout_018_B.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_018_C](security_holdout_018_C.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_025_B](security_holdout_025_B.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_025_C](security_holdout_025_C.md) | stale_authenticated_delivery | SEC-ST-005, SEC-UT-002 |
| [security_holdout_027_B](security_holdout_027_B.md) | counter_gap | SEC-ST-003, SEC-UT-002 |
| [security_holdout_043_B](security_holdout_043_B.md) | counter_gap | SEC-ST-003, SEC-UT-002 |
| [security_holdout_045_B](security_holdout_045_B.md) | counter_gap | SEC-ST-003, SEC-UT-002 |
