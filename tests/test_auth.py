from unittest.mock import AsyncMock

import pytest

from inspira.auth.decorators import login_required
from inspira.auth.utils import login_user, logout_user
from inspira.decorators.http_methods import get
from inspira.enums import HttpMethod
from inspira.requests import Request, RequestContext
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


@pytest.mark.asyncio
async def test_login_user(app_with_session, mock_scope):
    receive = AsyncMock()
    request = Request(mock_scope, receive)
    RequestContext.set_request(request)

    login_user()
    assert "logged_in" in request.session
    assert request.session["logged_in"] is True


@pytest.mark.asyncio
async def test_login_user(app_with_session, mock_scope):
    receive = AsyncMock()
    request = Request(mock_scope, receive)
    request.set_session("logged_in", True)
    RequestContext.set_request(request)

    logout_user()
    assert "logged_in" not in request.session
