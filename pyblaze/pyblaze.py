import importlib
import inspect
import logging
import re
from http import HTTPStatus
from typing import Callable, Dict, List

from httpx import AsyncClient

from pyblaze.config import Config
from pyblaze.enums import HttpMethod
from pyblaze.requests import Request, RequestContext
from pyblaze.responses import TemplateResponse, JsonResponse


class PyBlaze:
    def __init__(self, logger_name="pyblaze", secret_key=None):
        self.routes: Dict[str, Dict[str, Callable]] = {
            method.value: {} for method in HttpMethod
        }
        self.error_handler = self.default_error_handler
        self.middleware: List[Callable] = []
        self.logger = logging.getLogger(logger_name)
        self.configure_logging()
        self.config = Config()
        self.secret_key = secret_key

    def configure(self, config_dict):
        for key, value in config_dict.items():
            self.config.set(key, value)

    def configure_logging(self):
        logging.basicConfig(level=logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def add_route(self, path: str, method: HttpMethod, handler: Callable):
        if path in self.routes[method.value]:
            raise AssertionError(
                f"Route with method '{method}' and path '{path}' already exists"
            )

        self.routes[method.value][path] = handler

    def add_resources(self, root_path: str, module_name: str):
        module = importlib.import_module(module_name)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj):
                self._add_class_routes(obj, root_path)
            elif inspect.isfunction(obj) and hasattr(obj, "__method__"):
                method = getattr(obj, "__method__")
                path = root_path + getattr(obj, "__path__")
                self.add_route(path, method, obj)

    def _add_class_routes(self, cls, root_path):
        instance = cls()
        for name, method in inspect.getmembers(instance, inspect.ismethod):
            if hasattr(method, "__method__") and hasattr(method, "__path__"):
                http_method = getattr(method, "__method__")
                route = getattr(method, "__path__")
                path = root_path + route
                self.add_route(path, http_method, method)

    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)
        return middleware

    async def __call__(self, scope, receive, send):
        request = Request(scope, receive)
        RequestContext.set_request(request)

        method = scope["method"]
        path = scope["path"]

        for middleware in self.middleware:
            request = await middleware(request)

        if path.startswith("/static"):
            # Handle static files using TemplateResponse
            await self.handle_static_files(scope, receive, send, request)
        elif path in self.routes[method]:
            try:
                handler = self.routes[method][path]
                response = await self.invoke_handler(handler, request, scope)

                await response(scope, receive, send)
            except Exception as exc:
                error_response = await self.error_handler(request, exc)
                await error_response(scope, receive, send)
        else:
            # Check for routes with dynamic parameters
            for route_path, handler in self.routes[method].items():
                if "{" in route_path and "}" in route_path:
                    route_pattern = route_path.replace("{", "(?P<").replace(
                        "}", ">[^/]+)"
                    )
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
                            error_response = await self.error_handler(request, exc)
                            await error_response(scope, receive, send)
            # If no matching route is found, return a 404 response
            await self.handle_not_found(scope, receive, send)

    async def handle_static_files(self, scope, receive, send, request):
        template_response = TemplateResponse(request, scope["path"])
        await template_response(scope, receive, send)

    async def handle_not_found(self, scope, receive, send):
        not_found_response = JsonResponse(
            {"error": "Not Found"}, status_code=HTTPStatus.NOT_FOUND
        )
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

    async def default_error_handler(self, request, exc):
        return JsonResponse(
            {"error": str(exc)}, status_code=HTTPStatus.INTERNAL_SERVER_ERROR
        )

    async def test_session(self, app, method, path, **kwargs):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            return await getattr(client, method.lower())(path, **kwargs)
