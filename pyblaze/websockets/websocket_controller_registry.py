class WebSocketControllerRegistry:
    _controllers = {}

    @classmethod
    def register_controller(cls, path, controller_cls):
        cls._controllers[path] = controller_cls
        return controller_cls

    @classmethod
    def get_controller(cls, path):
        return cls._controllers.get(path)
