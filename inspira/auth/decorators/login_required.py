from functools import wraps

from inspira.requests import RequestContext
from inspira.responses import HttpResponse


def login_required(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = RequestContext.get_request()

        logged_in = request.get_session("logged_in")

        if not logged_in:
            return HttpResponse("Unauthorized", status_code=401)

        return await func(*args, **kwargs)

    return wrapper
