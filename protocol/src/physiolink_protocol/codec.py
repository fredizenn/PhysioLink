import struct

from .frames import PROTOCOL_VERSION, Frame, FrameType

class ProtocolError(ValueError):
        """Bytes that are not a valid PhysioLink frame."""

HEADER = struct.Struct("<BBHIBB")       #version, type, seq, t_device_ms, n_samples, flags
IMU_SAMPLE = struct.Struct("<6h")       #6 x signed 16-bit
PPG_SAMPLE_SIZE = 3
PPG_MAX = (1 << 19) - 1         #524287, largest 19-bit value
SEQ_MODULUS = 1 << 16       #seq wraps after 65535
    
    
def encode(frame: Frame) -> bytes:
    if frame.frame_type is FrameType.PPG:
        payload = b"".join(_encode_ppg(v) for v in frame.samples)
    elif frame.frame_type is FrameType.IMU:
        payload = b"".join(IMU_SAMPLE.pack(*s) for s in frame.samples)
    else:
        raise ProtocolError(f"encoding {frame.frame_type.name} is not defined in v0")
    try:
        header = HEADER.pack(frame.version, frame.frame_type, frame.seq, frame.t_device_ms, frame.n_samples, frame.flags)
    except struct.error as e :
        raise ProtocolError(f"header field out of range: {e}") from e
    return header + payload

def _encode_ppg(value: int) -> bytes:
    if not 0 <= value <= PPG_MAX:
        raise ProtocolError(f"PPG sample {value} outside 0..{PPG_MAX}")
    return value.to_bytes(PPG_SAMPLE_SIZE, "little")

def decode(data: bytes) -> Frame:
    if len(data) < HEADER.size:
        raise ProtocolError(f"need at least {HEADER.size} bytes, got {len(data)}")
    version, ftype, seq, t_ms, n, flags = HEADER.unpack_from(data)
    if version != PROTOCOL_VERSION:
        raise ProtocolError(f"unsupported protocol version {version}")
    try:
        frame_type = FrameType(ftype)
    except ValueError:
        raise ProtocolError(f"unknown frame type 0x{ftype:02x}") from None
    
    payload = data[HEADER.size:]
    if frame_type is FrameType.PPG:
        samples = _split(payload, n, PPG_SAMPLE_SIZE, _decode_ppg)
    elif frame_type is FrameType.IMU:
        samples = _split(payload, n, IMU_SAMPLE.size, IMU_SAMPLE.unpack)
    else:
        raise ProtocolError(f"decoding {frame_type.name} is not defined in v0")
    return Frame(frame_type, seq, t_ms, samples, flags, version)


def _split(payload: bytes, n: int, size: int, parse) -> list:
    if len(payload) != n * size:
        raise ProtocolError(f"payload is {len(payload)} bytes, expected {n} × {size}")
    return [parse(payload[i:i + size]) for i in range(0, len(payload), size)]

def _decode_ppg(chunk: bytes) -> int:
    value = int.from_bytes(chunk, "little")
    if value > PPG_MAX:
        raise ProtocolError(f"PPG sample {value} exceeds 19 bits")
    return value