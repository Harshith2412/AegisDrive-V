"""Virtual CAN bus for the vertical slice.

Two backends with the same interface:
  * InProcessCanBus (default, zero dependencies): deterministic, step-synchronous.
    Frames sent during step k are delivered at step k+1 (one-cycle bus latency).
  * PythonCanBus: wraps python-can's 'virtual' interface when python-can is installed.
    It is provided for interoperability; the deterministic in-process bus is used for
    all evidence in the vertical slice because python-can was not installable in the
    development sandbox (see docs/toolchain_notes.md).

Classic CAN only in the slice (DLC 8). CAN FD is a planned extension.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CanFrame:
    arbitration_id: int
    data: bytes
    timestamp_ms: int
    sender: str
    is_fd: bool = False

    def __post_init__(self):
        if not 0 <= self.arbitration_id <= 0x7FF:
            raise ValueError("only 11-bit identifiers are supported in the slice")
        if len(self.data) > (64 if self.is_fd else 8):
            raise ValueError("payload too long")


@dataclass
class InProcessCanBus:
    """Broadcast bus with one-cycle latency and a complete frame log."""
    log: list[CanFrame] = field(default_factory=list)
    _pending: list[CanFrame] = field(default_factory=list)
    _deliverable: list[CanFrame] = field(default_factory=list)
    drop_filter: object = None  # optional callable(frame) -> bool (True = drop), for fault injection
    tamper: object = None       # optional callable(frame) -> frame, models on-wire corruption/manipulation

    def send(self, frame: CanFrame) -> None:
        if self.tamper is not None:
            frame = self.tamper(frame)
        self.log.append(frame)
        if self.drop_filter is not None and self.drop_filter(frame):
            return
        self._pending.append(frame)

    def advance(self) -> None:
        """Make all frames sent in the previous step available to receivers."""
        self._deliverable = self._pending
        self._pending = []

    def receive(self, arbitration_id: int) -> CanFrame | None:
        """Latest deliverable frame with the given ID (receivers sample once per step)."""
        for f in reversed(self._deliverable):
            if f.arbitration_id == arbitration_id:
                return f
        return None


class PythonCanBus:  # pragma: no cover - exercised only where python-can is installed
    def __init__(self, channel: str = "aegis"):
        import can  # noqa: F401  (optional dependency)
        self._can = can
        self._tx = can.Bus(interface="virtual", channel=channel, receive_own_messages=False)
        self._rx = can.Bus(interface="virtual", channel=channel)
        self._deliverable: list[CanFrame] = []
        self.log: list[CanFrame] = []

    def send(self, frame: CanFrame) -> None:
        self.log.append(frame)
        self._tx.send(self._can.Message(arbitration_id=frame.arbitration_id, data=frame.data,
                                        is_extended_id=False, is_fd=frame.is_fd,
                                        timestamp=frame.timestamp_ms / 1000.0))

    def advance(self) -> None:
        frames = []
        while (m := self._rx.recv(timeout=0.0)) is not None:
            frames.append(CanFrame(m.arbitration_id, bytes(m.data), int(m.timestamp * 1000), "bus", m.is_fd))
        self._deliverable = frames

    def receive(self, arbitration_id: int) -> CanFrame | None:
        for f in reversed(self._deliverable):
            if f.arbitration_id == arbitration_id:
                return f
        return None

    def shutdown(self) -> None:
        self._tx.shutdown()
        self._rx.shutdown()
