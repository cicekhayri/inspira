import datetime
import json
import mimetypes
import os
from http import HTTPStatus

from jinja2 import Environment, FileSystemLoader

from inspira.constants import APPLICATION_JSON, NOT_FOUND, TEXT_HTML, TEXT_PLAIN, UTF8
from inspira.logging import log
from inspira.requests import RequestContext


class HttpResponse:
    def __init__(
        self,
        content=None,
        status_code=HTTPStatus.OK,
        content_type=TEXT_PLAIN,
        headers=None,
    ):
        self.content = content
        self.status_code = status_code
        self.content_type = content_type
        self.headers = dict(headers or {})

    def set_cookie(
        self,
        key,
        value,
        max_age=None,
        expires=None,
        path="/",
        domain=None,
        secure=False,
        httponly=False,
        samesite=None,
    ):
        cookie_str = f"{key}={value}"

        if max_age is not None:
            cookie_str += f"; Max-Age={max_age}"
        elif expires is not None and isinstance(expires, (int, float)):
            expires_dt = datetime.datetime.utcfromtimestamp(expires)
            expires_str = expires_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
            cookie_str += f"; Expires={expires_str}"

        if path:
            cookie_str += f"; Path={path}"
        if domain:
            cookie_str += f"; Domain={domain}"
        if secure:
            cookie_str += "; Secure"
        if httponly:
            cookie_str += "; HttpOnly"
        if samesite:
            cookie_str += f"; SameSite={samesite}"

        # Append the cookie to the headers dictionary
        self.headers.setdefault("set-cookie", []).append(cookie_str)

    async def __call__(self, scope, receive, send):
        headers = await self.encoded_headers()

        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": headers,
            }
        )

        body = await self.serialize_content()

        await send(
            {
                "type": "http.response.body",
                "body": body,
                "more_body": False,
            }
        )

    async def encoded_headers(self):
        request_headers = RequestContext().get_request().get_request_headers()

        headers = [(b"content-type", self.content_type.encode(UTF8))]

        headers.extend(request_headers)

        for key, value_list in self.headers.items():
            headers.extend(self.encode_header(key, value_list))

        return headers

    def encode_header(self, key, value_list):
        if not isinstance(value_list, list):
            value_list = [value_list]

        return [(key.encode(UTF8), self.encode_value(value)) for value in value_list]

    def encode_value(self, value):
        if isinstance(value, str):
            return value.encode(UTF8)
        return value

    async def serialize_content(self):
        if self.content is not None:
            if isinstance(self.content, bytes):
                body = self.content
            elif self.content_type == APPLICATION_JSON:
                body = json.dumps(self.content).encode(UTF8)
            else:
                body = str(self.content).encode(UTF8)
        else:
            body = b""
        return body


class JsonResponse(HttpResponse):
    def __init__(self, content=None, status_code=HTTPStatus.OK, headers=None):
        super().__init__(content, status_code, APPLICATION_JSON, headers)


class TemplateResponse(HttpResponse):
    def __init__(
        self,
        template_name=None,
        context=None,
        template_dir="templates",
        static_dir="static",
    ):
        super().__init__(None, HTTPStatus.OK, TEXT_HTML)
        self.template_name = template_name
        self.context = context or {}
        self.static_dir = static_dir
        self.template_dir = template_dir

    async def __call__(self, scope, receive, send):
        path_info = scope.get("path", "").lstrip("/") or scope.get(
            "raw_path", b""
        ).decode(UTF8).lstrip("/")

        if path_info.startswith("static/"):
            await self.handle_static_file(scope, receive, send)
        else:
            await self.render_template(scope, receive, send)

    async def render_template(self, scope, receive, send):
        if self.template_name is None:
            log.error("Template name is not provided.")
            not_found_response = JsonResponse(
                {"error": NOT_FOUND}, status_code=HTTPStatus.NOT_FOUND
            )
            await not_found_response(scope, receive, send)
            return

        template_path = os.path.join(self.template_dir, self.template_name)

        if not os.path.exists(template_path):
            log.error("Template not found:", template_path)
            not_found_response = JsonResponse(
                {"error": NOT_FOUND}, status_code=HTTPStatus.NOT_FOUND
            )
            await not_found_response(scope, receive, send)

        template_env = Environment(loader=FileSystemLoader(self.template_dir))
        template = template_env.get_template(self.template_name)
        content = template.render(**self.context)

        self.content = content.encode(UTF8)
        await super().__call__(scope, receive, send)

    async def handle_static_file(self, scope, receive, send):
        path_info = scope.get("path", "").lstrip("/") or scope.get(
            "raw_path", b""
        ).decode(UTF8).lstrip("/")
        static_prefix = "static/"

        if path_info.startswith(static_prefix):
            relative_path = path_info[len(static_prefix) :]
            file_path = os.path.join(self.static_dir, relative_path)

            if os.path.isfile(file_path):
                content_type, _ = mimetypes.guess_type(file_path)
                headers = [(b"content-type", content_type.encode(UTF8))]

                with open(file_path, "rb") as file:
                    body = file.read()

                await send(
                    {
                        "type": "http.response.start",
                        "status": HTTPStatus.OK,
                        "headers": headers,
                    }
                )

                await send(
                    {
                        "type": "http.response.body",
                        "body": body,
                        "more_body": False,
                    }
                )
            else:
                log.error("File not found:", file_path)

                # Return a 404 response for non-existing static files
                not_found_response = JsonResponse(
                    {"error": "Not Found"}, status_code=HTTPStatus.NOT_FOUND
                )
                await not_found_response(scope, receive, send)
        else:
            log.error("Unexpected path:", path_info)

            # Return a 404 response for unexpected paths
            not_found_response = JsonResponse(
                {"error": "Not Found"}, status_code=HTTPStatus.NOT_FOUND
            )
            await not_found_response(scope, receive, send)


class HttpResponseRedirect(HttpResponse):
    def __init__(self, url: str, status_code=HTTPStatus.FOUND, headers=None):
        super().__init__(content=None, status_code=status_code, headers=headers or {})
        self.headers["Location"] = url


class ForbiddenResponse(HttpResponse):
    def __init__(
        self,
        content=None,
        content_type=TEXT_PLAIN,
        status_code=HTTPStatus.FORBIDDEN,
        headers=None,
    ):
        super().__init__(content, status_code, content_type, headers)
