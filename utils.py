import json
import struct
from typing import NamedTuple

import brotli
import httpx

from _types import DanMuInfo, WsOp


class Header(NamedTuple):
    msg_len: int
    header_len: int = 16
    ver: int = 1
    op: int = 1
    seq: int = 1


class WsMessageHandler:
    @classmethod
    def pack(cls):
        raise NotImplementedError

    @classmethod
    def unpack(cls):
        raise NotImplementedError


class HeaderPkgHandler(WsMessageHandler):
    """
    msg_len header_len ver  op    seq
    \_____/ \_______/  \/   \/    \/
     4byte   2byte    2byte 4byte 4byte

    """

    @classmethod
    def pack(
        cls,
        msg_len: int,
        header_len: int = WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH.value,
        ver: int = WsOp.WS_HEADER_DEFAULT_VERSION.value,
        op: int = WsOp.WS_HEADER_DEFAULT_OPERATION.value,
        seq: int = WsOp.WS_HEADER_DEFAULT_SEQUENCE.value,
    ):
        """
        pack head
        Args:
            msg_len: data_len + head_lean
            header_len: 16
            ver: 1
            op: op code
            seq: 1
        """
        # struct.pack_into("!I", cls.buffer, 0, msg_len)
        # struct.pack_into("!H", cls.buffer, 4, header_len)
        # struct.pack_into("!H", cls.buffer, 6, ver)
        # struct.pack_into("!I", cls.buffer, 8, op)
        # struct.pack_into("!I", cls.buffer, 12, seq)
        return struct.pack("!I2H2I", msg_len, header_len, ver, op, seq)

    @classmethod
    def unpack(cls, header_bytes: bytes) -> Header:
        assert len(header_bytes) == WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH.value
        data_len, header_len, ver, op, seq = struct.unpack("!I2H2I", header_bytes)
        assert header_len == WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH.value
        return Header(data_len, header_len, ver, op, seq)


class PackageHandler(WsMessageHandler):
    @classmethod
    def pack(cls, msg: bytes, op: WsOp):
        msg_len = len(msg)
        total_len = msg_len + WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH.value
        return HeaderPkgHandler.pack(total_len, op=op.value) + msg

    @classmethod
    def unpack(cls, package: bytes):
        header = HeaderPkgHandler.unpack(package[: WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH.value])
        if header.msg_len < len(package):
            cls.unpack(package=package[: header.msg_len])
            op = WsOp(header.op)
            if op != WsOp.WS_OP_MESSAGE and op != WsOp.WS_OP_CONNECT_SUCCESS:
                if op == WsOp.WS_OP_HEARTBEAT_REPLY:
                    body = {"count": struct.unpack("!I", package[WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH :])}
        else:
            index = WsOp.WS_PACKAGE_OFFSET.value
            s = header.msg_len
            a = ""
            u = ""
            body = []
            breakpoint()
            while index < len(package):
                s = struct.unpack_from("!I", package, index)[0]
                a = struct.unpack_from("!H", package, index + WsOp.WS_HEADER_OFFSET.value)[0]
                try:
                    if header.ver == WsOp.WS_BODY_PROTOCOL_VERSION_NORMAL.value:
                        c = package[index + a : index + s].decode("utf-8")
                        u = json.loads(c) if c else None
                    elif header.ver == WsOp.WS_BODY_PROTOCOL_VERSION_BROTLI:
                        l = package[index + a : index + s]
                        h = brotli.decompress(l.decode("utf-8"))
                        u = cls.unpack(h)
                    u and body.append(u)
                except Exception:
                    print("error")
                finally:
                    index += s
        return body


def get_danmu_info(room_id: int) -> DanMuInfo:
    url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo"
    with httpx.Client() as client:
        resp = client.get(url, params={"id": room_id})
        resp.raise_for_status()
        return DanMuInfo(**resp.json())
