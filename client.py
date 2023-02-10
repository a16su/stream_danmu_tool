# encoding: utf-8
# author: liyn
# time: 2022/12/1 15:35
import asyncio
import json
import typing
from abc import ABC

import websockets


class WsClient(ABC):

    def __init__(self, uri: str):
        self._uri = uri

    async def connect(self):
        raise NotImplementedError

    async def send(self, msg: typing.Union[str, bytes]):
        raise NotImplementedError

    async def send_json(self, body: typing.Dict[typing.Any, typing.Any]):
        msg = json.dumps(body)
        return await self.send(msg)

    async def recv(self, run_time=0) -> typing.AsyncGenerator:
        raise NotImplementedError

    async def recv_once(self) -> typing.Union[str, bytes]:
        raise NotImplementedError

    async def close(self):
        raise NotImplementedError


class DefaultWsClient(WsClient):
    async def recv_once(self):
        return await self.__client.recv()

    def __init__(self, uri: str):
        super(DefaultWsClient, self).__init__(uri)
        self.__client: typing.Optional[websockets.WebSocketClientProtocol] = None

    async def connect(self) -> "DefaultWsClient":
        self.__client = await websockets.connect(self._uri)
        return self

    async def send(self, msg: typing.Union[str, bytes]):
        await self.__client.send(msg)

    async def __call__(self):
        await self.connect()

    def __await__(self):
        return self

    async def __aenter__(self) -> "DefaultWsClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def recv(self, run_time: int = 0) -> typing.AsyncGenerator:
        end_flag = False
        if self.__client is None:
            await self.connect()

        def stop_recv():
            nonlocal end_flag
            end_flag = True

        if run_time != 0:
            loop = asyncio.get_event_loop()
            loop.call_later(run_time, callback=stop_recv)
        async for msg in self.__client:
            yield msg
            if end_flag:
                break

    async def close(self):
        await self.__client.close()


# async def main():
#     # async with DefaultWsClient("ws://127.0.0.1:8001") as cc:
#     cc = DefaultWsClient("ws://127.0.0.1:8001")
#     # await cc.connect()
#     async for msg in cc.recv(2):
#         print(msg)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
