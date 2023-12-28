from typing import List

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

    async def __call__(self, request: Request):
        origin = request.get_headers().get("origin")

        if origin is not None and (
            origin not in self.allow_origins and "*" not in self.allow_origins
        ):
            request.set_forbidden()
            return request

        if origin is not None:
            request.set_header("Access-Control-Allow-Origin", origin)
            request.set_header(
                "Access-Control-Allow-Credentials", str(self.allow_credentials).lower()
            )
            request.set_header(
                "Access-Control-Allow-Methods", ",".join(self.allow_methods)
            )
            request.set_header(
                "Access-Control-Allow-Headers", ",".join(self.allow_headers)
            )

        return request
