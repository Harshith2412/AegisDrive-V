package AegisReviewV1 {
    private import ScalarValues::*;
    private import AegisDriveV3::*;
    private import AegisSecurityV4::*;
    item def VerifiedCommand {
        attribute issued_ms : Integer;
        attribute authenticated : Boolean;
        attribute source_id : Integer;
        attribute decel_mps2 : Real;
        attribute active : Boolean;
    }
    port def VerifiedCommandPort { out item request : VerifiedCommand; }
    part def AuthenticatedRouteSelector {
        port primary : ~VerifiedCommandPort;
        port backup : ~VerifiedCommandPort;
        port selected : RequestPort;
        attribute trusted_common_clock : Boolean = true;
    }
    part def PressureMonitor {
        attribute current_backlog : Integer;
        attribute new_drops : Integer;
        attribute clear_dwell_ms : Integer = 100;
    }
    part def PerceptionStudy {
        attribute default_policy_unchanged : Boolean = true;
    }
    part def IndependentOracleReview;
    part selector : AuthenticatedRouteSelector;
    part pressureMonitor : PressureMonitor;
    part perceptionStudy : PerceptionStudy;
    part oracleReview : IndependentOracleReview;
    state def PressureLifecycle {
        entry; then normal;
        state normal;
        state pressure;
        state recovering;
        transition first normal then pressure;
        transition first pressure then recovering;
        transition first recovering then pressure;
        transition first recovering then normal;
    }
    // State graph is abstract; actual queue/100 ms guards are in code and recovery.puml.
    requirement 'REC-501' {
        subject system : AuthenticatedRouteSelector;
        doc /* Freshest authenticated transport selection. External tests: REV-UT-001, REV-ST-001. */
    }
    allocation allocate 'REC-501' to selector;
    verification 'VERIFY-REC-501' {
        subject system : AuthenticatedRouteSelector;
        objective { verify 'REC-501'; }
    }
    requirement 'REC-502' {
        subject system : PressureMonitor;
        doc /* Current pressure and bounded diagnostic recovery. External tests: REV-UT-002. */
    }
    allocation allocate 'REC-502' to pressureMonitor;
    verification 'VERIFY-REC-502' {
        subject system : PressureMonitor;
        objective { verify 'REC-502'; }
    }
    requirement 'SOT-501' {
        subject system : PerceptionStudy;
        doc /* Transparent temporal/confidence/braking tradeoff study. External tests: REV-UT-003, REV-ST-002. */
    }
    allocation allocate 'SOT-501' to perceptionStudy;
    verification 'VERIFY-SOT-501' {
        subject system : PerceptionStudy;
        objective { verify 'SOT-501'; }
    }
    requirement 'QLT-501' {
        subject system : IndependentOracleReview;
        doc /* Independent interface and physics oracles. External tests: REV-UT-004, REV-PBT-001. */
    }
    allocation allocate 'QLT-501' to oracleReview;
    verification 'VERIFY-QLT-501' {
        subject system : IndependentOracleReview;
        objective { verify 'QLT-501'; }
    }
}
