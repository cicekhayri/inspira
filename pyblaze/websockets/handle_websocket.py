from pyblaze.constants import WEBSOCKET_RECEIVE_TYPE, WEBSOCKET_DISCONNECT_TYPE
from pyblaze.websockets import WebSocket, WebSocketControllerRegistry


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

            if message["type"] == WEBSOCKET_DISCONNECT_TYPE:
                break

            if message["type"] == WEBSOCKET_RECEIVE_TYPE:
                await controller_instance.on_message(websocket_cls, message)

    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        await controller_instance.on_close(websocket_cls)
