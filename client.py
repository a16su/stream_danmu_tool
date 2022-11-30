import json
import typing

from websockets import WebSocketClientProtocol, connect

from utils import PackageHandler, WsOp, get_danmu_info


class BiliBiliLiveDanmu:
    def __init__(self, room_id: int, uid: typing.Optional[int] = None):
        self._room_id = room_id
        self._uid = uid or 0
        self._danmu_info = None
        self._on_message_callbacks = []
        self.client: typing.Optional[WebSocketClientProtocol] = None

    async def send_str(self, data: str, op: WsOp):
        await self.client.send(PackageHandler.pack(data.encode("utf-8"), op=op))

    async def send_json(self, body: typing.Dict, op: WsOp):
        await self.send_str(json.dumps(body), op=op)

    async def init(self):
        self._danmu_info = await get_danmu_info(self._room_id)
        host_info = self._danmu_info.data.host_list[0]
        uri = f"wss://{host_info.host}:{host_info.wss_port}/sub"
        self.client = await connect(uri)
        await self._say_hello()

    async def _say_hello(self):
        body = {
            "uid": self._uid,
            "roomid": self._room_id,
            "protover": 3,
            "platform": "web",
            "type": 2,
            "key": self._danmu_info.data.token,
        }
        try:
            await self.send_json(body, WsOp.WS_OP_USER_AUTHENTICATION)
            for i in range(20):
                resp = await self.client.recv()
                print(PackageHandler.unpack(resp))
        finally:
            await self.client.close()

    def add_on_message_callback(self, func: typing.Callable[[bytes], bytes]):
        self._on_message_callbacks.append(func)
