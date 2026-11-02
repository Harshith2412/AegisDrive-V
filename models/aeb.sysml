package AegisDriveV {
    private import ScalarValues::*;
    // SysML v2 textual structure; no parser installed here, semantic validation pending.
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
    port def RadarPort { out item measurement : RadarMeasurement; }
    port def RequestPort { out item request : BrakeRequest; }
    port def StatusPort { out item status : BrakeStatus; }
    part def Radar { port output : RadarPort; }
    part def AdasEcu {
        port perception : ~RadarPort;
        port command : RequestPort;
        port feedback : ~StatusPort;
    }
    part def BrakeEcu {
        port command : ~RequestPort;
        port feedback : StatusPort;
    }
    part def BodyEcu { port brakeState : ~StatusPort; }
    part def AebSystem {
        part radar : Radar;
        part adas : AdasEcu;
        part brake : BrakeEcu;
        part body : BodyEcu;
        connect radar.output to adas.perception;
        connect adas.command to brake.command;
        connect brake.feedback to adas.feedback;
        connect brake.feedback to body.brakeState;
    }
    part vehicleAeb : AebSystem;
}
