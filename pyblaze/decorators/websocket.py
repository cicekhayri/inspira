from pyblaze.websockets import WebSocketControllerRegistry


def websocket(path):
    def decorator(cls):
        WebSocketControllerRegistry.register_controller(path, cls)
        return cls

    return decorator
