def path(path: str):
    def decorator(cls):
        cls.__path__ = path
        cls.__is_controller__ = True
        return cls
    return decorator