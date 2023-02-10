import asyncio
import json
import typing
from collections import defaultdict

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from _types import SocketMsgType
from client import DefaultWsClient, WsClient
from utils import PackageHandler, WsOp, get_danmu_info, handle_danmu_msg


class BiliBiliLiveDanmu:
    def __init__(
        self,
        room_id: int,
        uid: typing.Optional[int] = None,
        client_factory: typing.Type[WsClient] = DefaultWsClient,
    ):
        self._room_id = room_id
        self._uid = uid or 0
        self._danmu_info = None
        self._on_message_callbacks = []
        self._client_factory: typing.Type[WsClient] = client_factory
        self._client: typing.Optional[WsClient] = None
        self._asyncio_scheduler = AsyncIOScheduler()
        self.event_listener = defaultdict(set)

    async def send_str(self, data: str, op: WsOp):
        await self._client.send(PackageHandler.pack(data.encode("utf-8"), op=op))

    async def send_json(self, body: typing.Dict, op: WsOp):
        await self.send_str(json.dumps(body), op=op)

    async def init(self):
        self._danmu_info = await get_danmu_info(self._room_id)
        host_info = self._danmu_info.data.host_list[0]
        uri = f"wss://{host_info.host}:{host_info.wss_port}/sub"
        self._client = self._client_factory(uri)
        await self._client.connect()
        await self._say_hello()
        await self._heart_beat()
        try:
            async for msg in self._client.recv():
                body = PackageHandler.unpack(msg)
                self.on_message(body)
        finally:
            await self.exit()

    def on_message(self, message):
        if isinstance(message, list):
            for item in message:
                self.on_message(item)
        elif isinstance(message, dict):
            if message["op"] == WsOp.WS_OP_HEARTBEAT_REPLY:
                self.handle_heart_beat_reply(message["body"])
            elif message["op"] == WsOp.WS_OP_MESSAGE:
                self.print_danmu(message["body"])

    def print_danmu(self, message: typing.Dict):
        for item in message:
            danmu_list = item.get("body", [])
            for danmu_info in danmu_list:
                if danmu_info["cmd"] == SocketMsgType.Danmaku.value:
                    msg = handle_danmu_msg(danmu_info)
                    print(f'{msg["date"]} {msg["uname"]}: {msg["text"]}')

    def handle_heart_beat_reply(self, resp):
        print(f"recv heart beat reply: {type(resp)}, {resp}")

    def add_listener(self, event, func: typing.Callable[[typing.Dict], str]):
        if func in self.event_listener[event]:
            raise RuntimeError(f"重复注册: {event} -> {func}")
        self.event_listener[event].add(func)

    def remove_listener(self, event, func):
        if event not in self.event_listener:
            raise RuntimeError(f"Unknown Event: {event}")
        if func not in self.event_listener[event]:
            raise RuntimeError(f"Unknown Func({func}) for event {event}")
        self.event_listener[event].discard(func)

    def dispatch_event(self, event, *args, **kwargs):
        for func in self.event_listener[event]:
            func(*args, **kwargs)

    async def recv(self):
        pass

    async def send(self):
        pass

    async def _say_hello(self):
        body = {
            "uid": self._uid,
            "roomid": self._room_id,
            "protover": 3,
            "platform": "web",
            "type": 2,
            "key": self._danmu_info.data.token,
        }
        await self.send_json(body, op=WsOp.WS_OP_USER_AUTHENTICATION)
        await self._client.recv_once()

    async def _heart_beat(self):
        async def do_heart_beat():
            await self.send_str("[object Object]", WsOp.WS_OP_HEARTBEAT)

        self._asyncio_scheduler.add_job(do_heart_beat, "interval", seconds=30)
        self._asyncio_scheduler.start()

    def add_on_message_callback(self, func: typing.Callable[[bytes], bytes]):
        self._on_message_callbacks.append(func)

    async def exit(self):
        await self._client.close()


if __name__ == "__main__":
    a = BiliBiliLiveDanmu(23219374)
    asyncio.run(a.init())
