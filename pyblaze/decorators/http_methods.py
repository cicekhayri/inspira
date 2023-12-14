from pyblaze.enums import HttpMethod


def get(path: str):
    def decorator(handler):
        handler.__method__ = HttpMethod.GET
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler
    return decorator


def post(path: str):
    def decorator(handler):
        handler.__method__ = HttpMethod.POST
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator


def put(path: str):
    def decorator(handler):
        handler.__method__ = HttpMethod.PUT
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator


def delete(path: str):
    def decorator(handler):
        handler.__method__ = HttpMethod.DELETE
        handler.__path__ = path
        handler.__is_handler__ = True
        return handler

    return decorator
