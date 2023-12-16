import json


class WebSocket:
    def __init__(self, scope, receive, send):
        assert scope["type"] == "websocket"
        self.receive = receive
        self._send = send

    async def send_text(self, data: str) -> None:
        await self._send({"type": "websocket.send", "text": data})

    async def send_json(self, data: dict) -> None:
        text_message = json.dumps(data, separators=(",", ":"))
        await self._send({"type": "websocket.send", "text": text_message})

    async def send_binary(self, data: bytes) -> None:
        await self._send({"type": "websocket.send", "bytes": data})

    async def on_open(self):
        await self._send({"type": "websocket.accept"})

    async def on_close(self):
        try:
            await self._send({"type": "websocket.close"})
        except Exception as e:
            print(f"Error sending close message: {e}")


class WebSocketControllerRegistry:
    _controllers = {}

    @classmethod
    def register_controller(cls, path, controller_cls):
        cls._controllers[path] = controller_cls
        return controller_cls

    @classmethod
    def get_controller(cls, path):
        return cls._controllers.get(path)


def websocket(path):
    def decorator(cls):
        WebSocketControllerRegistry.register_controller(path, cls)
        return cls

    return decorator


async def handle_websocket(scope, receive, send):
    path = scope["path"]
    controller_cls = WebSocketControllerRegistry.get_controller(path)

    if not controller_cls:
        print(f"No WebSocket controller registered for path: {path}")
        return

    websocket_cls = WebSocket(scope, receive, send)
    controller_instance = controller_cls()

    try:
        await controller_instance.on_open(websocket_cls)

        while True:
            message = await websocket_cls.receive()

            if message["type"] == "websocket.disconnect":
                break

            if message["type"] == "websocket.receive":
                await controller_instance.on_message(websocket_cls, message)

    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        await controller_instance.on_close(websocket_cls)
