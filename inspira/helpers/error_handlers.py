import logging
from typing import Dict, Any, Callable

from inspira.helpers.error_templates import (
    format_method_not_allowed_exception,
    format_not_found_exception,
    format_server_exception,
)


async def handle_method_not_allowed(
    scope: Dict[str, Any], receive: Callable, send: Callable
) -> None:
    method_not_allowed_response = format_method_not_allowed_exception()
    await method_not_allowed_response(scope, receive, send)


async def handle_not_found(
    scope: Dict[str, Any], receive: Callable, send: Callable
) -> None:
    not_found_response = format_not_found_exception()
    await not_found_response(scope, receive, send)


async def default_error_handler(exc):
    logging.exception(exc)
    return format_server_exception()
