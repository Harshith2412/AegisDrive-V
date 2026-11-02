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
