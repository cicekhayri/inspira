from unittest.mock import AsyncMock

import pytest

from inspira.auth.utils import login_user, logout_user, generate_token, decode_token
from inspira.requests import Request, RequestContext


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
