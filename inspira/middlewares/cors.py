from typing import Any, Callable, Dict, List

from inspira.helpers.error_handlers import handle_forbidden
from inspira.requests import Request


class CORSMiddleware:
    def __init__(
        self,
        allow_origins: List[str] = None,
        allow_credentials: bool = False,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
    ):
        self.allow_origins = allow_origins or []
        self.allow_credentials = allow_credentials
        self.allow_methods = allow_methods or []
        self.allow_headers = allow_headers or []

    async def __call__(self, handler):
        async def middleware(scope: Dict[str, Any], receive: Callable, send: Callable):
            request = Request(scope, receive, send)
            origin = request.get_headers().get("origin")

            if scope["method"] == "OPTIONS":
                return await self.handle_options(scope, receive, send, origin)

            if origin is not None and not self.is_origin_allowed(origin):
                return await handle_forbidden(scope, receive, send)

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = message.get("headers", [])

                    if origin in self.allow_origins:
                        headers.extend(self.get_cors_headers(origin))

                    message["headers"] = headers

                await send(message)

            await handler(scope, receive, send_wrapper)

        return middleware

    def is_origin_allowed(self, origin):
        return origin is not None and (
            origin in self.allow_origins or "*" in self.allow_origins
        )

    def get_cors_headers(self, origin):
        return [
            (b"Access-Control-Allow-Origin", origin.encode()),
            (
                b"Access-Control-Allow-Credentials",
                str(self.allow_credentials).lower().encode(),
            ),
            (b"Access-Control-Allow-Methods", ",".join(self.allow_methods).encode()),
            (b"Access-Control-Allow-Headers", ",".join(self.allow_headers).encode()),
        ]

    async def handle_options(self, scope, receive, send, origin):
        headers = self.get_cors_headers(origin)
        headers.append(
            (
                b"Access-Control-Allow-Headers",
                ",".join(self.allow_headers + ["Content-Type"]).encode(),
            )
        )
        response_message = {
            "type": "http.response.start",
            "status": 200,
            "headers": headers,
        }

        await send(response_message)
        await send({"type": "http.response.body", "body": b""})
