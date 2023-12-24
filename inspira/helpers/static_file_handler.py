from typing import Any, Callable, Dict

from inspira.requests import Request
from inspira.responses import TemplateResponse


async def handle_static_files(
    scope: Dict[str, Any], receive: Callable, send: Callable, request: Request
) -> None:
    template_response = TemplateResponse(request, scope["path"])
    await template_response(scope, receive, send)
