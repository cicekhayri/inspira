from typing import Dict, Any


class WebSocketControllerRegistry:
    _controllers = {}

    @classmethod
    def register_controller(cls, path: str, controller_cls: Dict[str, Any]):
        cls._controllers[path] = controller_cls
        return controller_cls

    @classmethod
    def get_controller(cls, path: str):
        return cls._controllers.get(path)
