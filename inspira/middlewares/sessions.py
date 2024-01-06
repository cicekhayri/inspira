import datetime
import uuid
from typing import Dict, Any, Callable

from inspira.globals import get_global_app
from inspira.helpers.error_handlers import handle_forbidden
from inspira.inspira import RequestContext
from inspira.logging import log
from inspira.utils.session_utils import (
    encode_session_data,
    decode_session_data,
    get_session_token_from_request,
)


class SessionMiddleware:
    def __init__(self):
        self.app = get_global_app()

    def build_set_cookie_header(self, session_data):
        encoded_payload = encode_session_data(session_data, self.app.secret_key)
        expires_date = datetime.datetime.utcnow() + datetime.timedelta(
            seconds=self.app.config["SESSION_MAX_AGE"]
        )
        formatted_expires = expires_date.strftime("%a, %d %b %Y %H:%M:%S GMT")

        cookie_value = (
            f"{self.app.config['SESSION_COOKIE_NAME']}={encoded_payload}; "
            f"Expires={formatted_expires}; Path={self.app.config['SESSION_COOKIE_PATH'] or '/'}; HttpOnly"
        )

        if self.app.config["SESSION_COOKIE_DOMAIN"]:
            cookie_value += f"; Domain={self.app.config['SESSION_COOKIE_DOMAIN']}"

        if self.app.config["SESSION_COOKIE_SECURE"]:
            cookie_value += "; Secure"

        if self.app.config["SESSION_COOKIE_SAMESITE"]:
            cookie_value += f"; SameSite={self.app.config['SESSION_COOKIE_SAMESITE']}"

        return cookie_value

    async def __call__(self, handler):
        async def middleware(scope: Dict[str, Any], receive: Callable, send: Callable):
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = message.get("headers", [])
                    request = RequestContext().get_request()
                    session_cookie = get_session_token_from_request(
                        request, self.app.config["SESSION_COOKIE_NAME"]
                    )

                    decoded_session = {}

                    if request.session and not session_cookie:
                        request.set_session("session_id", str(uuid.uuid4()))

                    if session_cookie:
                        decoded_session = decode_session_data(
                            session_cookie, self.app.secret_key
                        )

                        if decoded_session is None:
                            log.error("Invalid session format.")
                            return await handle_forbidden(scope, receive, send)

                    if not request.session or decoded_session != request.session:
                        if request.session:
                            cookie_value = self.build_set_cookie_header(request.session)

                            headers.append((b"Set-Cookie", cookie_value.encode()))
                        else:
                            cookie_value = f"{self.app.config['SESSION_COOKIE_NAME']}=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path={self.app.config['SESSION_COOKIE_PATH'] or '/'}; HttpOnly"

                            headers.append((b"Set-Cookie", cookie_value.encode()))

                    message["headers"] = headers

                await send(message)

            await handler(scope, receive, send_wrapper)

        return middleware
