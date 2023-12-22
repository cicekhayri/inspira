from unittest.mock import AsyncMock

import pytest

from inspira.constants import (
    WEBSOCKET_SEND_TYPE,
    WEBSOCKET_RECEIVE_TYPE,
    WEBSOCKET_CLOSE_TYPE,
    WEBSOCKET_ACCEPT_TYPE,
    WEBSOCKET_DISCONNECT_TYPE,
    WEBSOCKET_TYPE,
)
from inspira.decorators.websocket import websocket
from inspira.websockets import (
    WebSocketControllerRegistry,
    WebSocket,
)


@websocket("/test")
class TestWebSocketController:
    async def on_open(self, websocket: WebSocket):
        await websocket.on_open()

    async def on_message(self, websocket: WebSocket, message):
        modified_message = f"Server response to: {message.get('text', '')}"
        await websocket.send_text(modified_message)

    async def on_close(self, websocket: WebSocket):
        await websocket.on_close()


@pytest.mark.asyncio
async def test_handle_websocket(app):
    receive_queue = [{"type": WEBSOCKET_RECEIVE_TYPE, "text": "Test message"}]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": WEBSOCKET_TYPE, "path": "/test"}, receive, send)

    assert send_queue == [
        {"type": WEBSOCKET_ACCEPT_TYPE},
        {"type": WEBSOCKET_SEND_TYPE, "text": "Server response to: Test message"},
        {"type": WEBSOCKET_CLOSE_TYPE},
    ]


@pytest.mark.asyncio
async def test_handle_websocket_multiple_messages(app):
    receive_queue = [
        {"type": WEBSOCKET_RECEIVE_TYPE, "text": "Message 1"},
        {"type": WEBSOCKET_RECEIVE_TYPE, "text": "Message 2"},
        {"type": WEBSOCKET_RECEIVE_TYPE, "text": "Message 3"},
    ]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": WEBSOCKET_TYPE, "path": "/test"}, receive, send)

    assert send_queue == [
        {"type": WEBSOCKET_ACCEPT_TYPE},
        {"type": WEBSOCKET_SEND_TYPE, "text": "Server response to: Message 1"},
        {"type": WEBSOCKET_SEND_TYPE, "text": "Server response to: Message 2"},
        {"type": WEBSOCKET_SEND_TYPE, "text": "Server response to: Message 3"},
        {"type": WEBSOCKET_CLOSE_TYPE},
    ]


@pytest.mark.asyncio
async def test_handle_websocket_connection_closure(app):
    receive_queue = [{"type": WEBSOCKET_DISCONNECT_TYPE}]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": WEBSOCKET_TYPE, "path": "/test"}, receive, send)

    assert send_queue == [
        {"type": WEBSOCKET_ACCEPT_TYPE},
        {"type": WEBSOCKET_CLOSE_TYPE},
    ]


@pytest.mark.asyncio
async def test_handle_websocket_invalid_path(app):
    receive_queue = [{"type": WEBSOCKET_RECEIVE_TYPE, "text": "Test message"}]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": WEBSOCKET_TYPE, "path": "/invalid_path"}, receive, send)

    assert send_queue == []


@pytest.mark.asyncio
async def test_send_text():
    websocket = WebSocket(
        scope={"type": WEBSOCKET_TYPE}, receive=AsyncMock(), send=AsyncMock()
    )

    data = "dddd"
    await websocket.send_text(data)

    expected_message = {"type": WEBSOCKET_SEND_TYPE, "text": "dddd"}
    websocket._send.assert_called_once_with(expected_message)


@pytest.mark.asyncio
async def test_send_json_text():
    websocket = WebSocket(
        scope={"type": WEBSOCKET_TYPE}, receive=AsyncMock(), send=AsyncMock()
    )

    data = {"key": "value"}
    await websocket.send_json(data)

    expected_message = {"type": WEBSOCKET_SEND_TYPE, "text": '{"key":"value"}'}
    websocket._send.assert_called_once_with(expected_message)


@pytest.mark.asyncio
async def test_send_bytes():
    websocket = WebSocket(
        scope={"type": WEBSOCKET_TYPE}, receive=AsyncMock(), send=AsyncMock()
    )

    data = b"value"
    await websocket.send_binary(data)

    expected_message = {"type": WEBSOCKET_SEND_TYPE, "bytes": b"value"}
    websocket._send.assert_called_once_with(expected_message)
