import importlib
import inspect
import os
import re
import sys
from typing import Callable, Dict, List, Any

from httpx import AsyncClient

from inspira.enums import HttpMethod
from inspira.helpers.error_handlers import (
    default_error_handler,
    handle_method_not_allowed,
    handle_not_found,
)
from inspira.helpers.static_file_handler import handle_static_files
from inspira.requests import Request, RequestContext
from inspira.sessions import encode_session_data, get_or_create_session
from inspira.utils.controller_parser import parse_controller_decorators
from inspira.utils.dependency_resolver import resolve_dependencies_automatic
from inspira.utils.handler_invoker import invoke_handler
from inspira.websockets import handle_websocket


class Inspira:
    def __init__(self, secret_key=None, session_type=None):
        self.routes: Dict[str, Dict[str, Callable]] = {
            method.value: {} for method in HttpMethod
        }
        self.error_handler = default_error_handler
        self.middleware: List[Callable] = []
        self.secret_key = secret_key
        self.session_type = session_type
        self.discover_controllers()

    def add_middleware(self, middleware: Callable) -> Callable:
        self.middleware.append(middleware)
        return middleware

    def add_route(self, path: str, method: HttpMethod, handler: Callable) -> None:
        if path in self.routes[method.value]:
            raise AssertionError(
                f"Route with method '{method}' and path '{path}' already exists"
            )

        self.routes[method.value][path] = handler

    def discover_controllers(self) -> None:
        current_dir = os.getcwd()
        src_dir = os.path.join(current_dir, "src")

        for root, _, files in os.walk(src_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if self._is_controller_file(file_path):
                    rel_path = os.path.relpath(file_path, src_dir)[:-3].replace(
                        os.sep, "."
                    )
                    module_path = f"src.{rel_path}"
                    self._add_routes(module_path)

    def _add_routes(self, file_path: str) -> None:
        try:
            module_name = self._file_path_to_module(file_path)
            src_directory = os.path.abspath(
                os.path.join(file_path, os.pardir, os.pardir)
            )
            sys.path.insert(0, src_directory)
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, "__path__"):
                    self._add_class_routes(obj)
        except ImportError as e:
            print(f"Error importing module {file_path}: {e}")
        finally:
            # Remove the 'src' directory from the Python path after importing
            sys.path.pop(0)

    def _add_class_routes(self, cls) -> None:
        if not hasattr(cls, "__path__"):
            return

        dependencies = resolve_dependencies_automatic(cls)
        instance = cls(*dependencies) if dependencies is not None else cls()

        path_prefix = getattr(cls, "__path__", "")

        for name, method in inspect.getmembers(instance, inspect.ismethod):
            if (
                hasattr(method, "__is_handler__")
                and hasattr(method, "__method__")
                and hasattr(method, "__path__")
            ):
                http_method = getattr(method, "__method__")
                route = getattr(method, "__path__")
                full_route = path_prefix + route
                self.add_route(full_route, http_method, method)

    def _file_path_to_module(self, file_path: str) -> str:
        rel_path = os.path.relpath(file_path, os.getcwd())
        return rel_path.replace(os.sep, ".")

    def _is_controller_file(self, file_path: str) -> bool:
        return file_path.endswith("_controller.py") and parse_controller_decorators(
            file_path
        )

    async def __call__(
        self, scope: Dict[str, Any], receive: Callable, send: Callable
    ) -> None:
        if scope["type"] == "websocket":
            await handle_websocket(scope, receive, send)
        elif scope["type"] == "http":
            await self.handle_http(scope, receive, send)

    async def handle_http(
        self, scope: Dict[str, Any], receive: Callable, send: Callable
    ) -> None:
        request = await self.create_request(receive, scope)
        RequestContext.set_request(request)

        await self.set_request_session(request)
        await self.process_middlewares(request)

        method = scope["method"]
        path = scope["path"]

        if path.startswith("/static"):
            await handle_static_files(scope, receive, send, request)
        elif path in self.routes[method]:
            await self.handle_route(method, path, receive, request, scope, send)
        else:
            # Check if the route is present but with a different method
            if any(path in methods for methods in self.routes.values()):
                await handle_method_not_allowed(scope, receive, send)
            else:
                await self.handle_dynamic_route(
                    method, path, request, scope, receive, send
                )

    async def handle_dynamic_route(
        self,
        method: str,
        path: str,
        request: Request,
        scope: Dict[str, Any],
        receive: Callable,
        send: Callable,
    ):
        for route_path, handler in self.routes[method].items():
            if "{" in route_path and "}" in route_path:
                route_pattern = route_path.replace("{", "(?P<").replace("}", ">[^/]+)")
                match = re.fullmatch(route_pattern, path)
                if match:
                    try:
                        params = match.groupdict()
                        response = await invoke_handler(handler, request, scope, params)
                        await response(scope, receive, send)
                        return
                    except Exception as exc:
                        error_response = await self.error_handler(exc)
                        await error_response(scope, receive, send)
        # If no matching route is found, return a 404 response
        await handle_not_found(scope, receive, send)

    async def handle_route(
        self,
        method: str,
        path: str,
        receive: Callable,
        request: Request,
        scope: Dict[str, Any],
        send: Callable,
    ):
        try:
            handler = self.routes[method][path]
            response = await invoke_handler(handler, request, scope)

            if self.session_type:
                encoded_and_signed_data = encode_session_data(
                    request.session, self.secret_key
                )
                response.set_cookie(
                    "session", encoded_and_signed_data, secure=True, httponly=True
                )

            await response(scope, receive, send)
        except Exception as exc:
            error_response = await self.error_handler(exc)
            await error_response(scope, receive, send)

    async def process_middlewares(self, request: Request):
        for middleware in self.middleware:
            request = await middleware(request)

    async def create_request(self, receive: Callable, scope: Dict[str, Any]) -> Request:
        return Request(scope, receive)

    async def set_request_session(self, request: Request) -> None:
        if self.session_type:
            session = get_or_create_session(request, self.secret_key)
            request.session = session

    async def test_session(self, app, method, path, **kwargs):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            return await getattr(client, method.lower())(path, **kwargs)
