import json
import urllib.parse
from typing import Any, Callable, Dict

from inspira.constants import UTF8


class RequestContext:
    _current_request = None
    _current_user = None

    @classmethod
    def set_request(cls, request):
        cls._current_request = request

    @classmethod
    def get_request(cls):
        return cls._current_request

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def set_current_user(cls, user):
        cls._current_user = user


class Request:
    def __init__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        self.scope = scope
        self.receive = receive
        self.send = send
        self._session = {}
        self._headers = {}
        self._forbidden = False
        self.user = None

    def is_forbidden(self):
        return self._forbidden

    def set_forbidden(self):
        self._forbidden = True

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    def set_session(self, key, value):
        if not isinstance(self._session, dict):
            self._session = {}

        self._session[key] = value

    def get_session(self, key, default=None):
        if not isinstance(self._session, dict):
            return default

        return self._session.get(key, default)

    def remove_session(self, key, default=None):
        if not isinstance(self._session, dict):
            return default

        return self._session.pop(key, default)

    def get_headers(self):
        return dict(
            (key.decode(UTF8), value.decode(UTF8))
            for key, value in self.scope.get("headers", [])
        )

    def set_header(self, key, value):
        self._headers[key] = value

    def get_request_headers(self):
        return list(
            (key.encode(UTF8), value.encode(UTF8))
            for key, value in self._headers.items()
        )

    def cookies(self):
        cookie_header = self.get_headers().get("cookie", "")
        if cookie_header:
            try:
                return {
                    key.strip(): value.strip()
                    for key, value in [
                        cookie.split("=", 1) for cookie in cookie_header.split(";")
                    ]
                }
            except ValueError:
                return {}
        return {}

    async def json(self):
        body = await self._get_body()
        if body:
            return json.loads(body.decode(UTF8))
        return {}

    async def _get_boundary(self):
        content_type_header = self.get_headers().get("content-type", "")
        if "multipart/form-data" in content_type_header:
            parts = content_type_header.split(";")
            for part in parts:
                if "boundary" in part:
                    _, boundary = part.strip().split("=")
                    return boundary.strip('"')
        return None

    async def form(self):
        content_type_header = self.get_headers().get("content-type", "")
        if "application/x-www-form-urlencoded" in content_type_header:
            body = await self._get_body()
            form_data = urllib.parse.parse_qsl(body.decode(UTF8))
            return {key: value for key, value in form_data}
        elif "multipart/form-data" in content_type_header:
            # Handle multipart form data
            return await self._parse_multipart_form_data()

        return {}

    async def _get_body(self):
        body = b""
        more_body = True
        while more_body:
            message = await self.receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)
        return body

    async def _parse_multipart_form_data(self):
        form_data = await self._get_body()
        boundary = await self._get_boundary()

        if not boundary or not form_data:
            return {}

        parts = form_data.split(b"--" + boundary.encode())

        form_data_dict = {}
        for part in parts:
            if not part.strip():
                continue

            headers_content = part.split(b"\r\n\r\n", 1)
            if len(headers_content) == 2:
                headers, content = headers_content
                content_lines = content.split(b"\r\n")
                # Filter out empty lines and join the rest
                content = b"\r\n".join(line for line in content_lines if line.strip())
            else:
                headers, content = headers_content[0], b""

            headers_lines = headers.decode(UTF8).split("\r\n")

            content_disposition = next(
                (
                    line
                    for line in headers_lines
                    if line.startswith("Content-Disposition")
                ),
                None,
            )

            if not content_disposition:
                continue

            _, name = content_disposition.split(";")
            name = name.split("=")[1].strip('"')

            content_str = content.decode(UTF8)

            form_data_dict[name] = content_str.strip()

        return form_data_dict
