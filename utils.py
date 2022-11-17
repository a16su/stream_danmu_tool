import struct
from typing import Optional, Tuple

import httpx

from _types import WsOp, DanMuInfo


class Header:
    """
    msg_len header_len ver  op    seq
    \_____/ \_______/  \/   \/    \/
     4byte   2byte    2byte 4byte 4byte

    """
    header_len: int = 16
    ver: int = 1
    op: int = 1
    seq: int = 1

    @classmethod
    def pack(cls, msg_len, header_len: Optional[int] = None, ver: Optional[int] = None, op: Optional[WsOp] = None,
             seq: Optional[int] = None):
        header_len = header_len or cls.header_len
        ver = ver or cls.ver
        op = op.value if op else cls.op
        seq = seq or cls.seq
        # struct.pack_into("!I", cls.buffer, 0, msg_len)
        # struct.pack_into("!H", cls.buffer, 4, header_len)
        # struct.pack_into("!H", cls.buffer, 6, ver)
        # struct.pack_into("!I", cls.buffer, 8, op)
        # struct.pack_into("!I", cls.buffer, 12, seq)
        return struct.pack("!I2H2I", msg_len, header_len, ver, op, seq)

    @classmethod
    def unpack(cls, header_bytes: bytes) -> Tuple[int, WsOp]:
        assert len(header_bytes) == cls.header_len
        mes_len, header_len, ver, op, seq = struct.unpack("!I2H2I", header_bytes)
        assert header_len == cls.header_len
        return mes_len - header_len, WsOp(op)


class Package:
    @classmethod
    def pack(cls, msg: bytes, op: WsOp):
        msg_len = len(msg)
        total_len = msg_len + WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH
        return Header.pack(total_len, op=op) + msg

    @classmethod
    def unpack(cls, package: bytes):
        msg_len, op = Header.unpack(package[:Header.header_len])


def get_danmu_info(room_id: int) -> DanMuInfo:
    url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo"
    with httpx.Client() as client:
        resp = client.get(url, params={
            "id": room_id
        })
        resp.raise_for_status()
        return DanMuInfo(**resp.json())
