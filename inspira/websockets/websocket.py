import json

from inspira.constants import (
    WEBSOCKET_ACCEPT_TYPE,
    WEBSOCKET_CLOSE_TYPE,
    WEBSOCKET_SEND_TYPE,
    WEBSOCKET_TYPE,
)
from inspira.logging import log


class WebSocket:
    def __init__(self, scope, receive, send):
        assert scope["type"] == WEBSOCKET_TYPE
        self.receive = receive
        self._send = send

    async def send_text(self, data: str) -> None:
        await self._send({"type": WEBSOCKET_SEND_TYPE, "text": data})

    async def send_json(self, data: dict) -> None:
        text_message = json.dumps(data, separators=(",", ":"))
        await self._send({"type": WEBSOCKET_SEND_TYPE, "text": text_message})

    async def send_binary(self, data: bytes) -> None:
        await self._send({"type": WEBSOCKET_SEND_TYPE, "bytes": data})

    async def on_open(self):
        await self._send({"type": WEBSOCKET_ACCEPT_TYPE})

    async def on_close(self):
        try:
            await self._send({"type": WEBSOCKET_CLOSE_TYPE})
        except Exception as e:
            log.error(f"Error sending close message: {e}")
