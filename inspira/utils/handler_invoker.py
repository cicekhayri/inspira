import inspect
from typing import Any, Dict

from inspira.requests import Request
from inspira.utils.param_converter import convert_param_type


async def invoke_handler(handler, request: Request, scope: Dict[str, Any], params=None):
    handler_signature = inspect.signature(handler)
    handler_params = {}
    for param_name, param in handler_signature.parameters.items():
        if param_name == "request":
            handler_params["request"] = request
        elif param_name == "scope":
            handler_params["scope"] = scope
        elif param_name in params:
            handler_params[param_name] = convert_param_type(
                params[param_name], param.annotation
            )
        elif param.default != inspect.Parameter.empty:
            handler_params[param_name] = param.default
        else:
            handler_params[param_name] = None

    return await handler(**handler_params)
