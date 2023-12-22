from inspira.websockets import WebSocketControllerRegistry


def websocket(path: str):
    def decorator(cls):
        WebSocketControllerRegistry.register_controller(path, cls)
        return cls

    return decorator
