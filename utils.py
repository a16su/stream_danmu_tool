import datetime
import json
import struct
import typing
from typing import NamedTuple

import brotli
import httpx

from _types import DanMuInfo, WsOp, DanmuType


class Header(NamedTuple):
    msg_len: int
    header_len: int = 16
    ver: int = 1
    op: int = 1
    seq: int = 1


class WsMessageHandler:
    @classmethod
    def pack(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def unpack(cls, *args, **kwargs):
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
        total_len = msg_len + WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH
        return HeaderPkgHandler.pack(total_len, op=op) + msg

    @classmethod
    def unpack(cls, package: bytes):
        result = {"body": []}
        header = HeaderPkgHandler.unpack(
            package[: WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH.value]
        )
        result.update(header._asdict())
        if (
            header.msg_len < len(package)
            and cls.unpack(package=package[: header.msg_len])
            and (header.op not in [WsOp.WS_OP_MESSAGE, WsOp.WS_OP_CONNECT_SUCCESS])
        ):
            if header.op == WsOp.WS_OP_HEARTBEAT_REPLY:
                result["body"] = {
                    "count": struct.unpack_from(
                        "!I", package, WsOp.WS_PACKAGE_HEADER_TOTAL_LENGTH
                    )
                }
        else:
            index = WsOp.WS_PACKAGE_OFFSET
            s = header.msg_len
            a = ""
            u = ""
            while index < len(package):
                s = struct.unpack_from("!i", package, index)[0]
                a = struct.unpack_from("!H", package, index + WsOp.WS_HEADER_OFFSET)[0]
                try:
                    if header.ver == WsOp.WS_BODY_PROTOCOL_VERSION_NORMAL.value:
                        c = package[index + a : index + s].decode("utf-8")
                        u = json.loads(c) if c else None
                    elif header.ver == WsOp.WS_BODY_PROTOCOL_VERSION_BROTLI.value:
                        msg = package[index + a : index + s]
                        h = brotli.decompress(msg)
                        u = cls.unpack(h)
                    u and result["body"].append(u)
                except Exception as e:
                    print(e)
                finally:
                    index += s
            return result


def handle_danmu_msg(msg: dict):
    info: typing.List[typing.Any] = msg["info"]
    return handle_danmu_info(info)


def handle_danmu_info(info: typing.List[typing.Any]):
    t = info[0][12]
    n = info[0][14]
    i = info[0][13]
    o = {
        "stime": -1,
        "mode": info[0][1],
        "size": info[0][2],
        "color": info[0][3],
        "date": datetime.datetime.now(),
        "uid": info[2][0],
        "dmid": info[0][5],
        "text": info[1],
        "uname": info[2][1],
        "user": {"level": info[4][0], "rank": info[2][5], "verify": info[2][6]},
        "checkInfo": {"ts": info[9]["ts"], "ct": info[9]["ct"]},
        "type": info[0][9],
        "dmType": DanmuType.Text,
        "modeInfo": info[0][15],
    }
    if t == DanmuType.Emoji:
        o["dmType"] = DanmuType.Emoji
        o["emoticonOptions"] = i
    elif t == DanmuType.Voice:
        o["dmType"] = DanmuType.Voice
        o["voiceConfig"] = n
    return o


async def get_danmu_info(room_id: int) -> DanMuInfo:
    url = "https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params={"id": room_id})
        resp.raise_for_status()
        return DanMuInfo(**resp.json())
