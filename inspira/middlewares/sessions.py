import datetime
from http.cookies import SimpleCookie
from typing import Dict, Any, Callable

from inspira.config import Config
from inspira.globals import get_global_app
from inspira.inspira import RequestContext
from inspira.utils.session_utils import encode_session_data, decode_session_data


class SessionMiddleware:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.config = get_global_app().config or Config()

    async def __call__(self, handler):
        async def middleware(scope: Dict[str, Any], receive: Callable, send: Callable):
            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = message.get("headers", [])
                    request = RequestContext().get_request()

                    if request.session:
                        cookies = SimpleCookie(request.get_headers().get("cookie", ""))
                        session_cookie = cookies.get(self.config["SESSION_COOKIE_NAME"])
                        decoded_session = None

                        if session_cookie:
                            decoded_session = decode_session_data(
                                session_cookie.value, self.secret_key
                            )

                        # Check if session is not present in the session cookie
                        if not session_cookie or decoded_session != request:
                            encoded_payload = encode_session_data(
                                request.session, self.secret_key
                            )
                            expires_date = (
                                datetime.datetime.utcnow()
                                + datetime.timedelta(
                                    seconds=self.config["SESSION_MAX_AGE"]
                                )
                            )
                            formatted_expires = expires_date.strftime(
                                "%a, %d %b %Y %H:%M:%S GMT"
                            )

                            # Build the "Set-Cookie" header with session configurations
                            cookie_value = f"{self.config['SESSION_COOKIE_NAME']}={encoded_payload}; Expires={formatted_expires}; Path={self.config['SESSION_COOKIE_PATH'] or '/'}; HttpOnly"

                            if self.config["SESSION_COOKIE_DOMAIN"]:
                                cookie_value += (
                                    f"; Domain={self.config['SESSION_COOKIE_DOMAIN']}"
                                )

                            if self.config["SESSION_COOKIE_SECURE"]:
                                cookie_value += "; Secure"

                            if self.config["SESSION_COOKIE_SAMESITE"]:
                                cookie_value += f"; SameSite={self.config['SESSION_COOKIE_SAMESITE']}"

                            headers.append((b"Set-Cookie", cookie_value.encode()))

                    message["headers"] = headers

                await send(message)

            await handler(scope, receive, send_wrapper)

        return middleware
