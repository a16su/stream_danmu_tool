#!/usr/bin/env python3
# encoding: utf-8
from enum import IntEnum, Enum
from typing import List

from pydantic import BaseModel


class DanMuInfoHost(BaseModel):
    host: str
    port: int
    wss_port: int
    ws_port: int


class DanMuInfoData(BaseModel):
    business_id: int
    group: str
    host_list: List[DanMuInfoHost]
    max_delay: int
    refresh_rate: int
    refresh_row_factor: float
    token: str


class DanMuInfo(BaseModel):
    code: int
    data: DanMuInfoData
    message: str
    ttl: int


class WsOp(IntEnum):
    WS_OP_HEARTBEAT = 2
    WS_OP_HEARTBEAT_REPLY = 3
    WS_OP_MESSAGE = 5
    WS_OP_USER_AUTHENTICATION = 7
    WS_OP_CONNECT_SUCCESS = 8
    WS_PACKAGE_HEADER_TOTAL_LENGTH = 16
    WS_PACKAGE_OFFSET = 0
    WS_HEADER_OFFSET = 4
    WS_VERSION_OFFSET = 6
    WS_OPERATION_OFFSET = 8
    WS_SEQUENCE_OFFSET = 12
    WS_BODY_PROTOCOL_VERSION_NORMAL = 0
    WS_BODY_PROTOCOL_VERSION_BROTLI = 3
    WS_HEADER_DEFAULT_VERSION = 1
    WS_HEADER_DEFAULT_OPERATION = 1
    WS_HEADER_DEFAULT_SEQUENCE = 1
    WS_AUTH_OK = 0
    WS_AUTH_TOKEN_ERROR = -101


class SocketMsgType(Enum):
    Danmaku = "DANMU_MSG"
    SysMsg = "SYS_MSG"
    SysGift = "SYS_GIFT"
    GuardMsg = "GUARD_MSG"
    SendGift = "SEND_GIFT"
    Live = "LIVE"
    Preparing = "PREPARING"
    End = "END"
    Close = "CLOSE"
    Block = "BLOCK"
    Round = "ROUND"
    Welcome = "WELCOME"
    Refresh = "REFRESH"
    ActivityRedPacket = "ACTIVITY_RED_PACKET"
    AreaBlock = "ROOM_LIMIT"
    PkPre = "PK_PRE"
    PkEnd = "PK_END"
    PkSettle = "PK_SETTLE"
    PkMicEnd = "PK_MIC_END"
    HotRoomNotify = "HOT_ROOM_NOTIFY"
    PLAY_TAG = "PLAY_TAG"
    PLAY_PROGRESS_BAR = "PLAY_PROGRESS_BAR"
    PlayerLogRecycle = "LIVE_PLAYER_LOG_RECYCLE"


class DanmuType(IntEnum):
    Text = 0
    Emoji = 1
    Voice = 2
