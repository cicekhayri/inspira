from functools import wraps

from inspira.auth.auth_utils import decode_auth_token
from inspira.requests import RequestContext
from inspira.responses import HttpResponse


def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = RequestContext.get_request()

        token = request.get_session("token")

        if not token or decode_auth_token(token) is None:
            return HttpResponse("Unauthorized", status_code=401)

        return await func(*args, **kwargs)

    return wrapper
