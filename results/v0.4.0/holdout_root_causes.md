# Existing hold-out collision analysis

{'insufficient_distance_even_with_instant_max_braking': 15, 'outside_activation_ODD': 7, 'grip_below_planning_assumption': 5, 'remaining_controller_perception_timing_interaction': 2}

Hierarchical groups are not unique causal proofs. Physical lower bound ignores all latency and is deliberately optimistic.
No attack is present in these cases. Ideal-sensor counterfactual is offline analysis, not a controller reading ground truth.

| Case | Primary group | Contributors | Still collides with ideal sensors / zero bus delay |
|---|---|---|---|
| holdout_009 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking | True |
| holdout_012 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking | True |
| holdout_021 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking | True |
| holdout_023 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_025 | outside_activation_ODD | outside_activation_ODD, insufficient_distance_even_with_instant_max_braking | True |
| holdout_027 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_047 | outside_activation_ODD | outside_activation_ODD | True |
| holdout_048 | outside_activation_ODD | outside_activation_ODD, insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_054 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking | True |
| holdout_057 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking | True |
| holdout_060 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking | True |
| holdout_061 | grip_below_planning_assumption | grip_below_planning_assumption | True |
| holdout_063 | grip_below_planning_assumption | grip_below_planning_assumption | True |
| holdout_066 | grip_below_planning_assumption | grip_below_planning_assumption | True |
| holdout_068 | outside_activation_ODD | outside_activation_ODD | True |
| holdout_073 | grip_below_planning_assumption | grip_below_planning_assumption | True |
| holdout_075 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_079 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking | True |
| holdout_081 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_082 | outside_activation_ODD | outside_activation_ODD, insufficient_distance_even_with_instant_max_braking | True |
| holdout_084 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_087 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_100 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_101 | grip_below_planning_assumption | grip_below_planning_assumption | True |
| holdout_103 | insufficient_distance_even_with_instant_max_braking | insufficient_distance_even_with_instant_max_braking, grip_below_planning_assumption | True |
| holdout_105 | outside_activation_ODD | outside_activation_ODD, insufficient_distance_even_with_instant_max_braking | True |
| holdout_108 | outside_activation_ODD | outside_activation_ODD, insufficient_distance_even_with_instant_max_braking | True |
| holdout_110 | remaining_controller_perception_timing_interaction |  | True |
| holdout_117 | remaining_controller_perception_timing_interaction |  | True |
