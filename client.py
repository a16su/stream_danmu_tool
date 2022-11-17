import json
import typing

from websocket import WebSocket

from utils import Package, WsOp, get_danmu_info


class BiliBiliLiveDanmu:

    def __init__(self, room_id: int, uid: typing.Optional[int] = None):
        self._room_id = room_id
        self._uid = uid or 0
        self._danmu_info = get_danmu_info(self._room_id)
        host_info = self._danmu_info.data.host_list[0]
        self._uri = f"wss://{host_info.host}:{host_info.wss_port}/sub"
        self.client = WebSocket()
        self.client.connect(self._uri)
        self._on_message_callbacks = []

    def _say_hello(self):
        body = {
            "uid": self._uid,
            "roomid": self._room_id,
            "protover": 3,
            "platform": "web",
            "type": 2,
            "key": self._danmu_info.data.token
        }
        self.client.send(Package.pack(json.dumps(body).encode(), WsOp.WS_OP_USER_AUTHENTICATION))
        resp = self.client.recv()
        print(resp)
        self.client.close()

    def add_on_message_callback(self, func: typing.Callable[[bytes], bytes]):
        self._on_message_callbacks.append(func)

