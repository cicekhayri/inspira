import pytest

from inspira.auth.decorators import login_required
from inspira.decorators.http_methods import get
from inspira.enums import HttpMethod
from inspira.requests import Request
from inspira.responses import HttpResponse


@pytest.mark.asyncio
async def test_protected_route(app):
    @get("/auth")
    @login_required
    async def protected_route(request: Request):
        return HttpResponse("This is a test endpoint")

    app.add_route("/auth", HttpMethod.GET, protected_route)

    response = await app.test_session(app, "GET", "/auth")

    assert response.status_code == 401
