from typing import Dict, Any, Callable

from inspira.auth.auth_utils import decode_auth_token
from inspira.auth.mixins.user_mixin import AnonymousUserMixin
from inspira.globals import get_global_app
from inspira.helpers.error_handlers import handle_forbidden
from inspira.logging import log
from inspira.requests import RequestContext
from inspira.utils.session_utils import (
    decode_session_data,
    get_session_token_from_request,
)


class UserLoaderMiddleware:
    def __init__(self, user_model):
        self.user_model = user_model
        self.app = get_global_app()

    async def __call__(self, handler):
        async def middleware(scope: Dict[str, Any], receive: Callable, send: Callable):
            request = RequestContext().get_request()
            session_cookie = get_session_token_from_request(
                request, self.app.config["SESSION_COOKIE_NAME"]
            )

            user = None

            if session_cookie:
                decoded_session = decode_session_data(
                    session_cookie, self.app.secret_key
                )
                if decoded_session is None:
                    log.error("Invalid session format.")
                    return await handle_forbidden(scope, receive, send)
                else:
                    user_id = decode_auth_token(decoded_session.get("token", None))

                    if user_id:
                        user = self.user_model.query.get(user_id)
            RequestContext.set_current_user(user or AnonymousUserMixin())
            request.user = RequestContext.get_current_user()

            await handler(scope, receive, send)

        return middleware
