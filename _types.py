#!/usr/bin/env python3
# encoding: utf-8
from enum import IntEnum
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
