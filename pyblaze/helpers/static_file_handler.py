from typing import Dict, Any, Callable

from pyblaze.requests import Request
from pyblaze.responses import TemplateResponse


async def handle_static_files(
        scope: Dict[str, Any], receive: Callable, send: Callable, request: Request
) -> None:
    template_response = TemplateResponse(request, scope["path"])
    await template_response(scope, receive, send)
