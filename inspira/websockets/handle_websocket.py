from inspira.constants import WEBSOCKET_DISCONNECT_TYPE, WEBSOCKET_RECEIVE_TYPE
from inspira.logging import log
from inspira.utils.dependency_resolver import resolve_dependencies_automatic
from inspira.websockets import WebSocket, WebSocketControllerRegistry


async def handle_websocket(scope, receive, send):
    path = scope["path"]
    controller_cls = WebSocketControllerRegistry.get_controller(path)

    if not controller_cls:
        log.info(f"No WebSocket controller registered for path: {path}")
        return

    websocket_cls = WebSocket(scope, receive, send)

    dependencies = resolve_dependencies_automatic(controller_cls)
    instance = (
        controller_cls(*dependencies) if dependencies is not None else controller_cls()
    )

    try:
        await instance.on_open(websocket_cls)

        while True:
            message = await websocket_cls.receive()

            if message["type"] == WEBSOCKET_DISCONNECT_TYPE:
                break

            if message["type"] == WEBSOCKET_RECEIVE_TYPE:
                await instance.on_message(websocket_cls, message)

    except Exception as e:
        log.info(f"WebSocket connection error: {e}")
    finally:
        await instance.on_close(websocket_cls)
