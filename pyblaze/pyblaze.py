import ast
import importlib
import inspect
import logging
import os
import re
import sys
from typing import Callable, Dict, List

from httpx import AsyncClient

from pyblaze.enums import HttpMethod
from pyblaze.helpers import format_not_found_exception, format_server_exception
from pyblaze.requests import Request, RequestContext
from pyblaze.responses import TemplateResponse
from pyblaze.sessions import encode_session_data, get_or_create_session


class PyBlaze:
    def __init__(self, secret_key=None, session_type=None):
        self.routes: Dict[str, Dict[str, Callable]] = {
            method.value: {} for method in HttpMethod
        }
        self.error_handler = self.default_error_handler
        self.middleware: List[Callable] = []
        self.secret_key = secret_key
        self.session_type = session_type
        self.discover_controllers()

    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)
        return middleware

    def add_route(self, path: str, method: HttpMethod, handler: Callable):
        if path in self.routes[method.value]:
            raise AssertionError(
                f"Route with method '{method}' and path '{path}' already exists"
            )

        self.routes[method.value][path] = handler

    def discover_controllers(self):
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

    def _add_routes(self, file_path: str):
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

    def _add_class_routes(self, cls):
        if not hasattr(cls, "__path__"):
            return

        instance = cls()
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

    def _file_path_to_module(self, file_path: str):
        rel_path = os.path.relpath(file_path, os.getcwd())
        return rel_path.replace(os.sep, ".")

    def _parse_controller_decorators(self, file_path):
        with open(file_path, "r") as file:
            tree = ast.parse(file.read(), filename=file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for decorator in node.decorator_list:
                    if (
                        isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Name)
                        and decorator.func.id == "path"
                    ):
                        return True
        return False

    def _is_controller_file(self, file_path):
        return file_path.endswith(
            "_controller.py"
        ) and self._parse_controller_decorators(file_path)

    async def __call__(self, scope, receive, send):
        request = await self._create_and_set_request_context(receive, scope)

        await self.set_request_session(request)

        method = scope["method"]
        path = scope["path"]

        await self.process_middlewares(request)

        if path.startswith("/static"):
            await self._handle_static_files(scope, receive, send, request)
        elif path in self.routes[method]:
            await self.handle_route(method, path, receive, request, scope, send)
        else:
            await self.handle_dynamic_route(method, path, request, scope, receive, send)

    async def handle_dynamic_route(self, method, path, request, scope, receive, send):
        for route_path, handler in self.routes[method].items():
            if "{" in route_path and "}" in route_path:
                route_pattern = route_path.replace("{", "(?P<").replace("}", ">[^/]+)")
                match = re.fullmatch(route_pattern, path)
                if match:
                    try:
                        params = match.groupdict()
                        response = await self.invoke_handler(
                            handler, request, scope, params
                        )
                        await response(scope, receive, send)
                        return
                    except Exception as exc:
                        error_response = await self.error_handler(exc)
                        await error_response(scope, receive, send)
        # If no matching route is found, return a 404 response
        await self.handle_not_found(scope, receive, send)

    async def handle_route(self, method, path, receive, request, scope, send):
        try:
            handler = self.routes[method][path]
            response = await self.invoke_handler(handler, request, scope)

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

    async def process_middlewares(self, request):
        for middleware in self.middleware:
            request = await middleware(request)

    async def _create_and_set_request_context(self, receive, scope):
        request = Request(scope, receive)
        RequestContext.set_request(request)
        return request

    async def set_request_session(self, request):
        if self.session_type:
            session = get_or_create_session(request, self.secret_key)
            request.session = session

    async def _handle_static_files(self, scope, receive, send, request):
        template_response = TemplateResponse(request, scope["path"])
        await template_response(scope, receive, send)

    async def handle_not_found(self, scope, receive, send):
        not_found_response = format_not_found_exception()
        await not_found_response(scope, receive, send)

    async def invoke_handler(self, handler, request, scope, params=None):
        handler_signature = inspect.signature(handler)
        handler_params = {}
        for param_name, param in handler_signature.parameters.items():
            if param_name == "request":
                handler_params["request"] = request
            elif param_name == "scope":
                handler_params["scope"] = scope
            elif param_name in params:
                handler_params[param_name] = self.convert_param_type(
                    params[param_name], param.annotation
                )
            elif param.default != inspect.Parameter.empty:
                handler_params[param_name] = param.default
            else:
                handler_params[param_name] = None

        return await handler(**handler_params)

    def convert_param_type(self, value, param_type):
        try:
            if param_type is None or param_type == inspect.Parameter.empty:
                return str(value)
            return param_type(value)
        except ValueError:
            return value

    async def default_error_handler(self, exc):
        logging.exception(exc)
        return format_server_exception()

    async def test_session(self, app, method, path, **kwargs):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            return await getattr(client, method.lower())(path, **kwargs)
