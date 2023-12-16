from unittest.mock import AsyncMock

import pytest
from pyblaze.websockets import (
    WebSocketControllerRegistry,
    websocket,
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
    receive_queue = [{"type": "websocket.receive", "text": "Test message"}]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": "websocket", "path": "/test"}, receive, send)

    assert send_queue == [
        {"type": "websocket.accept"},
        {"type": "websocket.send", "text": "Server response to: Test message"},
        {"type": "websocket.close"},
    ]


@pytest.mark.asyncio
async def test_handle_websocket_multiple_messages(app):
    receive_queue = [
        {"type": "websocket.receive", "text": "Message 1"},
        {"type": "websocket.receive", "text": "Message 2"},
        {"type": "websocket.receive", "text": "Message 3"},
    ]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": "websocket", "path": "/test"}, receive, send)

    assert send_queue == [
        {"type": "websocket.accept"},
        {"type": "websocket.send", "text": "Server response to: Message 1"},
        {"type": "websocket.send", "text": "Server response to: Message 2"},
        {"type": "websocket.send", "text": "Server response to: Message 3"},
        {"type": "websocket.close"},
    ]


@pytest.mark.asyncio
async def test_handle_websocket_connection_closure(app):
    receive_queue = [{"type": "websocket.disconnet"}]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": "websocket", "path": "/test"}, receive, send)

    assert send_queue == [
        {"type": "websocket.accept"},
        {"type": "websocket.close"},
    ]


@pytest.mark.asyncio
async def test_handle_websocket_invalid_path(app):
    receive_queue = [{"type": "websocket.receive", "text": "Test message"}]
    send_queue = []

    async def receive():
        return receive_queue.pop(0) if receive_queue else None

    async def send(message):
        send_queue.append(message)

    WebSocketControllerRegistry.register_controller("/test", TestWebSocketController)

    await app({"type": "websocket", "path": "/invalid_path"}, receive, send)

    assert send_queue == []


@pytest.mark.asyncio
async def test_send_text():
    websocket = WebSocket(
        scope={"type": "websocket"}, receive=AsyncMock(), send=AsyncMock()
    )

    data = "dddd"
    await websocket.send_text(data)

    expected_message = {"type": "websocket.send", "text": "dddd"}
    websocket._send.assert_called_once_with(expected_message)


@pytest.mark.asyncio
async def test_send_json_text():
    websocket = WebSocket(
        scope={"type": "websocket"}, receive=AsyncMock(), send=AsyncMock()
    )

    data = {"key": "value"}
    await websocket.send_json(data)

    expected_message = {"type": "websocket.send", "text": '{"key":"value"}'}
    websocket._send.assert_called_once_with(expected_message)


@pytest.mark.asyncio
async def test_send_bytes():
    websocket = WebSocket(
        scope={"type": "websocket"}, receive=AsyncMock(), send=AsyncMock()
    )

    data = b"value"
    await websocket.send_binary(data)

    expected_message = {"type": "websocket.send", "bytes": b"value"}
    websocket._send.assert_called_once_with(expected_message)
