from typing import Type, Callable


def path(path: str) -> Callable[[Type], Type]:
    def decorator(cls: Type) -> Type:
        cls.__path__ = path
        cls.__is_controller__ = True
        return cls

    return decorator
