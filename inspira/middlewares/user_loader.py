from http.cookies import SimpleCookie
from typing import Dict, Any, Callable

from inspira.auth.auth_utils import decode_auth_token
from inspira.config import Config
from inspira.requests import RequestContext
from inspira.utils.session_utils import decode_session_data


class UserLoaderMiddleware:
    def __init__(self, user_model, secret_key, config = Config()):
        self.user_model = user_model
        self.config = config
        self.secret_key = secret_key

    async def __call__(self, handler):
        async def middleware(scope: Dict[str, Any], receive: Callable, send: Callable):
            request = RequestContext().get_request()

            cookies = SimpleCookie(request.get_headers().get("cookie", ""))
            token = cookies.get(self.config["SESSION_COOKIE_NAME"])

            if token:
                decoded_session = decode_session_data(
                    token.value, self.secret_key
                )
                get_user_id = decode_auth_token(decoded_session['token'])
                if get_user_id:
                    user = self.user_model.query.get(get_user_id)
                    RequestContext.set_current_user(user)
                    request.user = RequestContext.get_current_user()
            else:
                request.user = None

            await handler(scope, receive, send)

        return middleware