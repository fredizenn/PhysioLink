from dataclasses import dataclass
from enum import IntEnum

PROTOCOL_VERSION = 0

class FrameType(IntEnum):
    PPG = 0x01
    IMU = 0x02
    STATUS = 0x10
    EVENT = 0x11
    
ImuSample = tuple[int, int, int, int, int, int] #ax, ay, az, gx, gy, gz


@dataclass(Frozen=True)

class Frame:
    frame_type: FrameType
    seq: int
    t_device_ms: int
    samples: list[int] | list[ImuSample]
    flags: int = 0
    version: int = PROTOCOL_VERSION
    
    @property
    def n_samples(self) -> int:
        return len(self.samples)