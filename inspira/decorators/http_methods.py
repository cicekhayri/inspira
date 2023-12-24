from typing import Callable, Type

from inspira.enums import HttpMethod


def get(path: str = "") -> Callable[[Type], Type]:
    def decorator(handler: Type) -> Type:
        handler.__method__ = HttpMethod.GET
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator


def post(path: str = "") -> Callable[[Type], Type]:
    def decorator(handler: Type) -> Type:
        handler.__method__ = HttpMethod.POST
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator


def put(path: str = "") -> Callable[[Type], Type]:
    def decorator(handler: Type) -> Type:
        handler.__method__ = HttpMethod.PUT
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator


def patch(path: str = "") -> Callable[[Type], Type]:
    def decorator(handler: Type) -> Type:
        handler.__method__ = HttpMethod.PATCH
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator


def delete(path: str = "") -> Callable[[Type], Type]:
    def decorator(handler: Type) -> Type:
        handler.__method__ = HttpMethod.DELETE
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator
