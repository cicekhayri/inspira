from typing import List, Dict, Any, Callable

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

            if origin is not None and (
                origin not in self.allow_origins and "*" not in self.allow_origins
            ):
                return await handle_forbidden(scope, receive, send)

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = message.get("headers", [])

                    if origin in self.allow_origins:
                        headers.append(
                            (b"Access-Control-Allow-Origin", origin.encode())
                        )
                        headers.append(
                            (
                                b"Access-Control-Allow-Credentials",
                                str(self.allow_credentials).lower().encode(),
                            )
                        )
                        headers.append(
                            (
                                b"Access-Control-Allow-Methods",
                                ",".join(self.allow_methods).encode(),
                            )
                        )
                        headers.append(
                            (
                                b"Access-Control-Allow-Headers",
                                ",".join(self.allow_headers).encode(),
                            )
                        )

                    message["headers"] = headers

                await send(message)

            await handler(scope, receive, send_wrapper)

        return middleware
