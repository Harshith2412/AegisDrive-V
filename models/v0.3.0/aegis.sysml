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
