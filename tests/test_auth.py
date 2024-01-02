from unittest.mock import AsyncMock

import pytest

from inspira.auth.decorators import login_required
from inspira.auth.auth_utils import login_user, logout_user, generate_token, decode_token
from inspira.requests import Request, RequestContext
from inspira.responses import HttpResponse


def test_generate_and_decode_token(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    RequestContext.set_request(request)

    user_id = 123
    token = generate_token(user_id)
    assert token is not None

    decoded_user_id = decode_token(token)
    assert decoded_user_id == user_id


@pytest.mark.asyncio
async def test_login_user(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    RequestContext.set_request(request)

    user_id = 123
    login_user(user_id)

    assert "token" in request.session

    token = request.session.get("token")
    decoded_user_id = decode_token(token)

    assert decoded_user_id == user_id


@pytest.mark.asyncio
async def test_logout_user(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    RequestContext.set_request(request)

    request.set_session("token", "dummy_token")

    logout_user()

    assert "token" not in request.session


@pytest.mark.asyncio
async def test_invalid_token(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    RequestContext.set_request(request)

    invalid_token = "invalid_token"

    decoded_user_id = decode_token(invalid_token)
    assert decoded_user_id is None


@pytest.mark.asyncio
async def test_login_logout_integration(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    RequestContext.set_request(request)

    user_id = 123

    login_user(user_id)
    assert "token" in request.session

    logout_user()
    assert "token" not in request.session


@pytest.mark.asyncio
async def test_login_required_decorator(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    RequestContext.set_request(request)

    @login_required
    async def protected_route():
        return HttpResponse("OK")

    response = await protected_route()
    assert response.status_code == 401

    request.set_session("token", "invalid_token")
    response = await protected_route()
    assert response.status_code == 401

    user_id = 123
    login_user(user_id)
    response = await protected_route()
    assert response.status_code == 200
