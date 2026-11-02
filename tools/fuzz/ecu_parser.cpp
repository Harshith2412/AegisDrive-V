// Fuzz native payload/CRC parsing only; HMAC envelope parsing is Python and tested separately.
#include <cstdint>
#include <cstddef>
#include <algorithm>
#include "aegis/codec.hpp"
#include "aegis/brake_ecu.hpp"
#include "aegis/e2e.hpp"
extern "C" int LLVMFuzzerTestOneInput(const std::uint8_t* data, std::size_t size) {
    if(size<9)return 0;
    std::uint8_t payload[8]{};std::copy(data+1,data+9,payload);
    aegis::codec::BrakeRequest command;
    aegis::codec::BrakeStatus brake;
    aegis::codec::AdasStatus status;
    aegis::codec::decode_brake_request(payload,10.,command);
    aegis::codec::decode_brake_status(payload,brake);
    aegis::codec::decode_adas_status(payload,status);
    aegis::e2e::Receiver receiver(2);receiver.check(0x120,payload);
    aegis::BrakeEcu ecu(aegis::default_brake_config());AegisBrakeInput in{};
    in.now_ms=10;in.dt_s=.01;in.frame_present=1;in.can_id=0x120;in.frame_dlc=data[0];
    std::copy(payload,payload+8,in.frame);ecu.step(in);
    in.frame_present=0;in.backup_present=1;in.backup_dlc=data[0];
    std::copy(payload,payload+8,in.backup_frame);ecu.step(in);
    return 0;
}
