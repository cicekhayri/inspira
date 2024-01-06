import logging
from typing import Any, Callable, Dict

from inspira.helpers.error_templates import (
    format_method_not_allowed_exception,
    format_not_found_exception,
    format_internal_server_error,
    format_forbidden_exception,
    format_unauthorized_exception,
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


async def handle_forbidden(
    scope: Dict[str, Any], receive: Callable, send: Callable
) -> None:
    forbidden_response = format_forbidden_exception()
    await forbidden_response(scope, receive, send)


async def handle_unauthorized(
    scope: Dict[str, Any], receive: Callable, send: Callable
) -> None:
    unauthorized_response = format_unauthorized_exception()
    await unauthorized_response(scope, receive, send)


async def handle_internal_server_error(
    scope: Dict[str, Any], receive: Callable, send: Callable
) -> None:
    internal_server_error = format_internal_server_error()
    await internal_server_error(scope, receive, send)


async def default_error_handler(exc):
    logging.exception(exc)
    return format_internal_server_error()
