// SOURCE models/v0.3.0/aegis.sysml
package AegisDriveV3 {
    private import ScalarValues::*;
    // Parsed and semantically checked by official pilot 0.63.1; see results/v0.3.0.
    // Units are explicit in names; library quantity typing is a future refinement.
    item def RadarMeasurement {
        attribute range_m : Real;
        attribute range_rate_mps : Real;
        attribute timestamp_ms : Integer;
        attribute healthy : Boolean;
        attribute object_present : Boolean;
    }
    item def BrakeRequest {
        attribute active : Boolean;
        attribute decel_mps2 : Real;
        attribute counter : Integer;
    }
    item def BrakeStatus {
        attribute active : Boolean;
        attribute timeout : Boolean;
        attribute actual_decel_mps2 : Real;
        attribute ack_valid : Boolean;
        attribute accepted_counter : Integer;
    }
    item def AchievedDeceleration {
        attribute decel_mps2 : Real;
        attribute timestamp_ms : Integer;
        attribute valid : Boolean;
    }
    item def AdasStatus {
        attribute adas_state : Integer;
        attribute unavailable : Boolean;
        attribute warning : Boolean;
    }
    port def AchievedPort { out item measurement : AchievedDeceleration; }
    port def AdasStatusPort { out item status : AdasStatus; }
    port def RadarPort { out item measurement : RadarMeasurement; }
    port def RequestPort { out item request : BrakeRequest; }
    port def StatusPort { out item status : BrakeStatus; }
    part def Radar { port output : RadarPort; }
    part def Camera { port output : RadarPort; }
    part def Fusion {
        port radarInput : ~RadarPort;
        port cameraInput : ~RadarPort;
        port output : RadarPort;
    }
    part def CommandTransport {
        port input : ~RequestPort;
        port output : RequestPort;
    }
    part def AchievedSensor { port output : AchievedPort; }
    part def ThreatAssessment;
    part def SafetySupervisor;
    part def AdasEcu {
        part decision : ThreatAssessment;
        part supervisor : SafetySupervisor;
        port perception : ~RadarPort;
        port achieved : ~AchievedPort;
        port status : AdasStatusPort;
        port command : RequestPort;
        port feedback : ~StatusPort;
    }
    part def BrakeEcu {
        port backup : ~RequestPort;
        port command : ~RequestPort;
        port feedback : StatusPort;
    }
    part def BodyEcu { port brakeState : ~StatusPort; port adasState : ~AdasStatusPort; }
    part def AebSystem {
        part radar : Radar;
        part camera : Camera;
        part fusion : Fusion;
        part adas : AdasEcu;
        part brake : BrakeEcu;
        part body : BodyEcu;
        part primaryNetwork : CommandTransport;
        part backupNetwork : CommandTransport;
        part achievedSensor : AchievedSensor;
        connect radar.output to fusion.radarInput;
        connect camera.output to fusion.cameraInput;
        connect fusion.output to adas.perception;
        connect adas.command to primaryNetwork.input;
        connect adas.command to backupNetwork.input;
        connect primaryNetwork.output to brake.command;
        connect backupNetwork.output to brake.backup;
        connect achievedSensor.output to adas.achieved;
        connect adas.status to body.adasState;
        connect brake.feedback to adas.feedback;
        connect brake.feedback to body.brakeState;
    }
    part vehicleAeb : AebSystem;
    requirement cameraTiming {
        doc /* PER-301: camera delivery preserves sampling timestamp and configured latency. */
        subject camera : Camera;
    }
    requirement fusionAssurance {
        doc /* PER-302: reject stale/future/low-confidence data and unresolved disagreement. */
        subject fusion : Fusion;
    }
    requirement backupCommand {
        doc /* BRK-301: backup command path is validated independently; physical actuator is shared. */
        subject brake : BrakeEcu;
    }
    allocation allocateCamera allocate cameraTiming to vehicleAeb.camera;
    allocation allocateFusion allocate fusionAssurance to vehicleAeb.fusion;
    allocation allocateBackup allocate backupCommand to vehicleAeb.brake;
    verification cameraVerification {
        subject camera : Camera;
        objective {
            verify cameraTiming;
        }
    }
    verification fusionVerification {
        subject fusion : Fusion;
        objective {
            verify fusionAssurance;
        }
    }
    state def AdasLifecycle {
        entry; then disabled;
        state disabled;
        state standby;
        state monitoring;
        state warning;
        state braking;
        state degraded;
        state fault;
        transition first disabled then standby;
        transition first standby then monitoring;
        transition first monitoring then warning;
        transition first warning then braking;
        transition first braking then standby;
        transition first monitoring then degraded;
        transition first degraded then fault;
        transition first fault then disabled;
    }
    // Lifecycle above is an abstract path, not the full guarded executable controller.

}

// SOURCE models/v0.3.0/requirements.sysml
package AegisRequirementsV3 {
    private import AegisDriveV3::*;
    requirement 'SYS-REQ-001' {
        subject system : AebSystem;
        doc /* Stationary target collision avoidance (nominal). External verification: ST-SLICE-001, ST-SLICE-002. */
    }
    allocation allocate 'SYS-REQ-001' to vehicleAeb.adas;
    verification 'VERIFY-SYS-REQ-001' {
        subject system : AebSystem;
        objective { verify 'SYS-REQ-001'; }
    }
    requirement 'SYS-REQ-002' {
        subject system : AebSystem;
        doc /* No intervention without a collision threat. External verification: ST-SLICE-003. */
    }
    allocation allocate 'SYS-REQ-002' to vehicleAeb.adas;
    verification 'VERIFY-SYS-REQ-002' {
        subject system : AebSystem;
        objective { verify 'SYS-REQ-002'; }
    }
    requirement 'SYS-REQ-003' {
        subject system : AebSystem;
        doc /* Lead-vehicle braking scenarios. External verification: ST-SLICE-004. */
    }
    allocation allocate 'SYS-REQ-003' to vehicleAeb.adas;
    verification 'VERIFY-SYS-REQ-003' {
        subject system : AebSystem;
        objective { verify 'SYS-REQ-003'; }
    }
    requirement 'ADAS-REQ-001' {
        subject system : AebSystem;
        doc /* Time-to-collision computation. External verification: UT-ADAS-001, IT-ABI-003. */
    }
    allocation allocate 'ADAS-REQ-001' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-001' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-001'; }
    }
    requirement 'ADAS-REQ-002' {
        subject system : AebSystem;
        doc /* Forward collision warning threshold. External verification: UT-ADAS-004, ST-SLICE-001, ST-SLICE-003. */
    }
    allocation allocate 'ADAS-REQ-002' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-002' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-002'; }
    }
    requirement 'ADAS-REQ-003' {
        subject system : AebSystem;
        doc /* Automatic emergency braking threshold and demand. External verification: UT-ADAS-002, UT-ADAS-005, ST-SLICE-001. */
    }
    allocation allocate 'ADAS-REQ-003' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-003' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-003'; }
    }
    requirement 'ADAS-REQ-004' {
        subject system : AebSystem;
        doc /* Activation speed window. External verification: UT-ADAS-003, UT-ADAS-006, UT-ADAS-007, UT-V3-003. */
    }
    allocation allocate 'ADAS-REQ-004' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-004' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-004'; }
    }
    requirement 'ADAS-REQ-005' {
        subject system : AebSystem;
        doc /* Standstill hold and release. External verification: UT-ADAS-007, ST-SLICE-001. */
    }
    allocation allocate 'ADAS-REQ-005' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-005' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-005'; }
    }
    requirement 'ADAS-REQ-006' {
        subject system : AebSystem;
        doc /* Abort braking when the threat clears. External verification: UT-ADAS-008. */
    }
    allocation allocate 'ADAS-REQ-006' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-006' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-006'; }
    }
    requirement 'ADAS-REQ-007' {
        subject system : AebSystem;
        doc /* State machine integrity. External verification: UT-ADAS-003, UT-ADAS-014, IT-ABI-004, ST-SLICE-006. */
    }
    allocation allocate 'ADAS-REQ-007' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-007' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-007'; }
    }
    requirement 'ADAS-REQ-008' {
        subject system : AebSystem;
        doc /* ADAS CAN transmission. External verification: UT-ADAS-016, UT-E2E-004. */
    }
    allocation allocate 'ADAS-REQ-008' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-008' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-008'; }
    }
    requirement 'ADAS-REQ-009' {
        subject system : AebSystem;
        doc /* Input plausibility. External verification: UT-ADAS-011, UT-ADAS-017. */
    }
    allocation allocate 'ADAS-REQ-009' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-009' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-009'; }
    }
    requirement 'ADAS-REQ-010' {
        subject system : AebSystem;
        doc /* Persistent degradation to FAULT. External verification: UT-ADAS-012. */
    }
    allocation allocate 'ADAS-REQ-010' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-010' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-010'; }
    }
    requirement 'ADAS-REQ-011' {
        subject system : AebSystem;
        doc /* Recovery from DEGRADED. External verification: UT-ADAS-013. */
    }
    allocation allocate 'ADAS-REQ-011' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-011' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-011'; }
    }
    requirement 'ADAS-REQ-012' {
        subject system : AebSystem;
        doc /* Configuration validation. External verification: UT-ADAS-015, UT-V3-010. */
    }
    allocation allocate 'ADAS-REQ-012' to vehicleAeb.adas;
    verification 'VERIFY-ADAS-REQ-012' {
        subject system : AebSystem;
        objective { verify 'ADAS-REQ-012'; }
    }
    requirement 'FSR-001' {
        subject system : AebSystem;
        doc /* (PROVISIONAL) Detect stale or frozen perception data. External verification: UT-ADAS-009, UT-ADAS-010, UT-SIM-004, ST-FI-001. */
    }
    allocation allocate 'FSR-001' to vehicleAeb.adas;
    verification 'VERIFY-FSR-001' {
        subject system : AebSystem;
        objective { verify 'FSR-001'; }
    }
    requirement 'TSR-001' {
        subject system : AebSystem;
        doc /* (PROVISIONAL) Timestamp freshness monitoring. External verification: UT-ADAS-009, UT-ADAS-010, UT-ADAS-017, ST-FI-001. */
    }
    allocation allocate 'TSR-001' to vehicleAeb.adas;
    verification 'VERIFY-TSR-001' {
        subject system : AebSystem;
        objective { verify 'TSR-001'; }
    }
    requirement 'TSR-002' {
        subject system : AebSystem;
        doc /* (PROVISIONAL) E2E protection of safety-relevant frames. External verification: UT-E2E-002, UT-E2E-003, ST-INV-001. */
    }
    allocation allocate 'TSR-002' to vehicleAeb.adas;
    verification 'VERIFY-TSR-002' {
        subject system : AebSystem;
        objective { verify 'TSR-002'; }
    }
    requirement 'TSR-003' {
        subject system : AebSystem;
        doc /* (PROVISIONAL) Brake command timeout. External verification: UT-BRK-003, ST-FI-002. */
    }
    allocation allocate 'TSR-003' to vehicleAeb.brake;
    verification 'VERIFY-TSR-003' {
        subject system : AebSystem;
        objective { verify 'TSR-003'; }
    }
    requirement 'BRK-REQ-001' {
        subject system : AebSystem;
        doc /* Brake command validation. External verification: UT-BRK-001, UT-BRK-002, UT-BRK-007, UT-E2E-004, UT-E2E-005, ST-INV-001. */
    }
    allocation allocate 'BRK-REQ-001' to vehicleAeb.brake;
    verification 'VERIFY-BRK-REQ-001' {
        subject system : AebSystem;
        objective { verify 'BRK-REQ-001'; }
    }
    requirement 'BRK-REQ-002' {
        subject system : AebSystem;
        doc /* Brake command timeout behaviour. External verification: UT-BRK-003, ST-FI-002. */
    }
    allocation allocate 'BRK-REQ-002' to vehicleAeb.brake;
    verification 'VERIFY-BRK-REQ-002' {
        subject system : AebSystem;
        objective { verify 'BRK-REQ-002'; }
    }
    requirement 'BRK-REQ-003' {
        subject system : AebSystem;
        doc /* Brake demand arbitration. External verification: UT-BRK-004. */
    }
    allocation allocate 'BRK-REQ-003' to vehicleAeb.brake;
    verification 'VERIFY-BRK-REQ-003' {
        subject system : AebSystem;
        objective { verify 'BRK-REQ-003'; }
    }
    requirement 'BRK-REQ-004' {
        subject system : AebSystem;
        doc /* Actuator model. External verification: UT-BRK-005. */
    }
    allocation allocate 'BRK-REQ-004' to vehicleAeb.brake;
    verification 'VERIFY-BRK-REQ-004' {
        subject system : AebSystem;
        objective { verify 'BRK-REQ-004'; }
    }
    requirement 'BRK-REQ-005' {
        subject system : AebSystem;
        doc /* Brake status reporting. External verification: UT-BRK-006, ST-SLICE-001. */
    }
    allocation allocate 'BRK-REQ-005' to vehicleAeb.brake;
    verification 'VERIFY-BRK-REQ-005' {
        subject system : AebSystem;
        objective { verify 'BRK-REQ-005'; }
    }
    requirement 'BCM-REQ-001' {
        subject system : AebSystem;
        doc /* Brake lamp activation latency. External verification: UT-BCM-001, ST-SLICE-001. */
    }
    allocation allocate 'BCM-REQ-001' to vehicleAeb.body;
    verification 'VERIFY-BCM-REQ-001' {
        subject system : AebSystem;
        objective { verify 'BCM-REQ-001'; }
    }
    requirement 'BCM-REQ-002' {
        subject system : AebSystem;
        doc /* Driver warning indicator. External verification: UT-BCM-002. */
    }
    allocation allocate 'BCM-REQ-002' to vehicleAeb.body;
    verification 'VERIFY-BCM-REQ-002' {
        subject system : AebSystem;
        objective { verify 'BCM-REQ-002'; }
    }
    requirement 'BCM-REQ-003' {
        subject system : AebSystem;
        doc /* Hazard lamp policy (project-defined). External verification: UT-BCM-003, ST-SLICE-001. */
    }
    allocation allocate 'BCM-REQ-003' to vehicleAeb.body;
    verification 'VERIFY-BCM-REQ-003' {
        subject system : AebSystem;
        objective { verify 'BCM-REQ-003'; }
    }
    requirement 'BCM-REQ-004' {
        subject system : AebSystem;
        doc /* Body ECU input supervision. External verification: UT-BCM-004, UT-BCM-005, ST-FI-001. */
    }
    allocation allocate 'BCM-REQ-004' to vehicleAeb.body;
    verification 'VERIFY-BCM-REQ-004' {
        subject system : AebSystem;
        objective { verify 'BCM-REQ-004'; }
    }
    requirement 'SWR-001' {
        subject system : AebSystem;
        doc /* ABI integrity between simulation and ECU library. External verification: IT-ABI-001, IT-ABI-002. */
    }
    allocation allocate 'SWR-001' to vehicleAeb;
    verification 'VERIFY-SWR-001' {
        subject system : AebSystem;
        objective { verify 'SWR-001'; }
    }
    requirement 'SWR-002' {
        subject system : AebSystem;
        doc /* CRC algorithm correctness. External verification: UT-E2E-001, IT-ABI-003. */
    }
    allocation allocate 'SWR-002' to vehicleAeb;
    verification 'VERIFY-SWR-002' {
        subject system : AebSystem;
        objective { verify 'SWR-002'; }
    }
    requirement 'SIM-REQ-001' {
        subject system : AebSystem;
        doc /* Vehicle model correctness. External verification: UT-SIM-001, UT-SIM-002. */
    }
    allocation allocate 'SIM-REQ-001' to vehicleAeb;
    verification 'VERIFY-SIM-REQ-001' {
        subject system : AebSystem;
        objective { verify 'SIM-REQ-001'; }
    }
    requirement 'SIM-REQ-002' {
        subject system : AebSystem;
        doc /* Deterministic, timestamped sensor simulation. External verification: UT-SIM-003, UT-SIM-004, ST-SLICE-005. */
    }
    allocation allocate 'SIM-REQ-002' to vehicleAeb;
    verification 'VERIFY-SIM-REQ-002' {
        subject system : AebSystem;
        objective { verify 'SIM-REQ-002'; }
    }
    requirement 'SIM-REQ-003' {
        subject system : AebSystem;
        doc /* Virtual CAN timing. External verification: UT-SIM-005. */
    }
    allocation allocate 'SIM-REQ-003' to vehicleAeb;
    verification 'VERIFY-SIM-REQ-003' {
        subject system : AebSystem;
        objective { verify 'SIM-REQ-003'; }
    }
    requirement 'FSR-201' {
        subject system : AebSystem;
        doc /* Stopping-distance assurance. External verification: UT-V2-001, ST-V2-001, ST-V2-002. */
    }
    allocation allocate 'FSR-201' to vehicleAeb.adas;
    verification 'VERIFY-FSR-201' {
        subject system : AebSystem;
        objective { verify 'FSR-201'; }
    }
    requirement 'TSR-201' {
        subject system : AebSystem;
        doc /* Stopping-distance assurance. External verification: UT-V2-001, ST-V2-001, ST-V2-002. */
    }
    allocation allocate 'TSR-201' to vehicleAeb.adas;
    verification 'VERIFY-TSR-201' {
        subject system : AebSystem;
        objective { verify 'TSR-201'; }
    }
    requirement 'FSR-202' {
        subject system : AebSystem;
        doc /* Sustained threat-clear assurance. External verification: UT-V2-002, ST-V2-001. */
    }
    allocation allocate 'FSR-202' to vehicleAeb.adas;
    verification 'VERIFY-FSR-202' {
        subject system : AebSystem;
        objective { verify 'FSR-202'; }
    }
    requirement 'TSR-202' {
        subject system : AebSystem;
        doc /* Sustained threat-clear assurance. External verification: UT-V2-002, ST-V2-001. */
    }
    allocation allocate 'TSR-202' to vehicleAeb.adas;
    verification 'VERIFY-TSR-202' {
        subject system : AebSystem;
        objective { verify 'TSR-202'; }
    }
    requirement 'FSR-203' {
        subject system : AebSystem;
        doc /* Brake execution assurance. External verification: UT-V2-003, UT-V2-004, UT-V2-005, ST-V2-003, ST-V2-004. */
    }
    allocation allocate 'FSR-203' to vehicleAeb.adas;
    verification 'VERIFY-FSR-203' {
        subject system : AebSystem;
        objective { verify 'FSR-203'; }
    }
    requirement 'TSR-203' {
        subject system : AebSystem;
        doc /* Brake execution assurance. External verification: UT-V2-003, UT-V2-004, UT-V2-005, ST-V2-003, ST-V2-004. */
    }
    allocation allocate 'TSR-203' to vehicleAeb.adas;
    verification 'VERIFY-TSR-203' {
        subject system : AebSystem;
        objective { verify 'TSR-203'; }
    }
    requirement 'SIM-301' {
        subject system : AebSystem;
        doc /* Physically consistent simulation contact and braking. External verification: UT-V3-001, UT-V3-002, PBT-V3-001. */
    }
    allocation allocate 'SIM-301' to vehicleAeb;
    verification 'VERIFY-SIM-301' {
        subject system : AebSystem;
        objective { verify 'SIM-301'; }
    }
    requirement 'PER-301' {
        subject system : AebSystem;
        doc /* Camera acquisition and delivery contract. External verification: UT-V3-004. */
    }
    allocation allocate 'PER-301' to vehicleAeb.camera;
    verification 'VERIFY-PER-301' {
        subject system : AebSystem;
        objective { verify 'PER-301'; }
    }
    requirement 'PER-302' {
        subject system : AebSystem;
        doc /* Per-source health and fusion assurance. External verification: UT-V3-005, UT-V3-006, ST-V3-001, ST-V3-004, PBT-V3-002. */
    }
    allocation allocate 'PER-302' to vehicleAeb.fusion;
    verification 'VERIFY-PER-302' {
        subject system : AebSystem;
        objective { verify 'PER-302'; }
    }
    requirement 'BRK-301' {
        subject system : AebSystem;
        doc /* Backup transport containment. External verification: UT-V3-009, UT-V3-011, ST-V3-002. */
    }
    allocation allocate 'BRK-301' to vehicleAeb.brake;
    verification 'VERIFY-BRK-301' {
        subject system : AebSystem;
        objective { verify 'BRK-301'; }
    }
    requirement 'DIA-301' {
        subject system : AebSystem;
        doc /* Achieved braking and transport diagnostic assurance. External verification: UT-V3-007, UT-V3-008, ST-V3-003. */
    }
    allocation allocate 'DIA-301' to vehicleAeb.adas;
    verification 'VERIFY-DIA-301' {
        subject system : AebSystem;
        objective { verify 'DIA-301'; }
    }
}

// SOURCE models/v0.4.0/security.sysml
package AegisSecurityV4 {
    private import ScalarValues::*;
    private import AegisDriveV3::*;
    item def ProtectedPdu {
        attribute version : Integer;
        attribute sender_id : Integer;
        attribute receiver_id : Integer;
        attribute key_id : Integer;
        attribute message_id : Integer;
        attribute boot_epoch : Integer;
        attribute freshness_counter : Integer;
        attribute issued_ms : Integer;
        attribute payload_length : Integer;
        attribute total_bytes : Integer = 64;
        attribute tag_bits : Integer = 128;
    }
    item def KeyPolicy {
        attribute test_only : Boolean = true;
        attribute retained_epoch : Integer;
    }
    port def ProtectedPort { out item pdu : ProtectedPdu; }
    port def PolicyPort { out item policy : KeyPolicy; }
    part def SharedSecurityService { port policy : PolicyPort; }
    part def CommandProtector {
        port input : ~RequestPort;
        port output : ProtectedPort;
        port policy : ~PolicyPort;
    }
    part def CommandVerifier {
        port input : ~ProtectedPort;
        port output : RequestPort;
        port policy : ~PolicyPort;
        attribute rejected_messages : Integer;
    }
    part def SensorProtector {
        port input : ~RadarPort;
        port output : ProtectedPort;
        port policy : ~PolicyPort;
    }
    part def SensorVerifier {
        port input : ~ProtectedPort;
        port output : RadarPort;
        port policy : ~PolicyPort;
    }
    part def StatusProtector {
        port input : ~StatusPort;
        port output : ProtectedPort;
        port policy : ~PolicyPort;
    }
    part def StatusVerifier {
        port input : ~ProtectedPort;
        port output : StatusPort;
        port policy : ~PolicyPort;
    }
    part def SecureSystem {
        part adas : AdasEcu;
        part brake : BrakeEcu;
        part body : BodyEcu;
        part radar : Radar;
        part camera : Camera;
        part fusion : Fusion;
        part shared : SharedSecurityService;
        part primaryTx : CommandProtector;
        part primaryRx : CommandVerifier;
        part backupTx : CommandProtector;
        part backupRx : CommandVerifier;
        part radarTx : SensorProtector;
        part radarRx : SensorVerifier;
        part cameraTx : SensorProtector;
        part cameraRx : SensorVerifier;
        part statusTx : StatusProtector;
        part adasStatusRx : StatusVerifier;
        part bodyStatusRx : StatusVerifier;
        connect adas.command to primaryTx.input;
        connect adas.command to backupTx.input;
        connect primaryTx.output to primaryRx.input;
        connect backupTx.output to backupRx.input;
        connect primaryRx.output to brake.command;
        connect backupRx.output to brake.backup;
        connect radar.output to radarTx.input;
        connect camera.output to cameraTx.input;
        connect radarTx.output to radarRx.input;
        connect cameraTx.output to cameraRx.input;
        connect radarRx.output to fusion.radarInput;
        connect cameraRx.output to fusion.cameraInput;
        connect fusion.output to adas.perception;
        connect brake.feedback to statusTx.input;
        connect statusTx.output to adasStatusRx.input;
        connect statusTx.output to bodyStatusRx.input;
        connect adasStatusRx.output to adas.feedback;
        connect bodyStatusRx.output to body.brakeState;
        connect shared.policy to primaryTx.policy;
        connect shared.policy to primaryRx.policy;
        connect shared.policy to backupTx.policy;
        connect shared.policy to backupRx.policy;
        connect shared.policy to radarTx.policy;
        connect shared.policy to radarRx.policy;
        connect shared.policy to cameraTx.policy;
        connect shared.policy to cameraRx.policy;
        connect shared.policy to statusTx.policy;
        connect shared.policy to adasStatusRx.policy;
        connect shared.policy to bodyStatusRx.policy;
    }
    part deployed : SecureSystem;
    state def SecurityLifecycle {
        entry; then provisioned;
        state provisioned;
        state operational;
        state rejected;
        state resynchronizing;
        state unavailable;
        transition first provisioned then operational;
        transition first operational then rejected;
        transition first rejected then resynchronizing;
        transition first resynchronizing then operational;
        transition first rejected then unavailable;
    }
    // Abstract security states; not an executable timing/fallback proof.
    requirement 'SEC-401' {
        subject system : SecureSystem;
        doc /* Authorized message authentication and bounded CAN FD framing. External executed tests: SEC-UT-001, SEC-PBT-001, SEC-PBT-002, SEC-UT-004, SEC-ST-002. */
    }
    allocation allocate 'SEC-401' to deployed.primaryRx;
    verification 'VERIFY-SEC-401' {
        subject system : SecureSystem;
        objective { verify 'SEC-401'; }
    }
    requirement 'SEC-402' {
        subject system : SecureSystem;
        doc /* Monotonic freshness and explicit recovery policy. External executed tests: SEC-UT-002, SEC-UT-003, SEC-UT-004, SEC-ST-003, SEC-ST-005. */
    }
    allocation allocate 'SEC-402' to deployed.primaryRx;
    verification 'VERIFY-SEC-402' {
        subject system : SecureSystem;
        objective { verify 'SEC-402'; }
    }
    requirement 'SEC-403' {
        subject system : SecureSystem;
        doc /* Authenticated ingress retains application safety validation. External executed tests: SEC-ST-001, SEC-ST-006, SEC-ST-002. */
    }
    allocation allocate 'SEC-403' to deployed.primaryRx;
    verification 'VERIFY-SEC-403' {
        subject system : SecureSystem;
        objective { verify 'SEC-403'; }
    }
    requirement 'SEC-404' {
        subject system : SecureSystem;
        doc /* Safety-security event and availability supervision. External executed tests: SEC-CPP-001, SEC-ST-002, SEC-ST-003, SEC-ST-004. */
    }
    allocation allocate 'SEC-404' to deployed.primaryRx;
    verification 'VERIFY-SEC-404' {
        subject system : SecureSystem;
        objective { verify 'SEC-404'; }
    }
    requirement 'SEC-405' {
        subject system : SecureSystem;
        doc /* Bounded attack handling and diagnostics. External executed tests: SEC-UT-004, SEC-ST-004. */
    }
    allocation allocate 'SEC-405' to deployed.primaryRx;
    verification 'VERIFY-SEC-405' {
        subject system : SecureSystem;
        objective { verify 'SEC-405'; }
    }
    dependency from 'SEC-404' to AegisRequirementsV3::'FSR-203';
    dependency from 'SEC-403' to AegisRequirementsV3::'PER-302';
}

