from unittest.mock import AsyncMock

import pytest

from inspira.requests import Request, RequestContext


def test_set_request(mock_scope):
    receive = AsyncMock()
    request = Request(mock_scope, receive)
    RequestContext.set_request(request)

    assert RequestContext.get_request() == request


def test_get_session(request_with_session):
    assert request_with_session.get_session("user_id") == 123
    assert request_with_session.get_session("username") == "john_doe"


def test_set_session(mock_scope):
    receive = AsyncMock()
    request = Request(mock_scope, receive)
    request.set_session("new_key", "new_value")
    assert request.session == {"new_key": "new_value"}


def test_remove_session(request_with_session):
    removed_value = request_with_session.remove_session("user_id")
    assert removed_value == 123
    assert "user_id" not in request_with_session.session


def test_remove_session_nonexistent_key(request_with_session):
    removed_value = request_with_session.remove_session("nonexistent_key")

    assert removed_value is None
    assert request_with_session.session == {"user_id": 123, "username": "john_doe"}


@pytest.mark.asyncio
async def test_json_with_valid_json(mock_scope):
    receive = AsyncMock()
    request = Request(mock_scope, receive)

    receive.side_effect = [
        {"body": b'{"key": "value"}', "more_body": False},
    ]

    json_data = await request.json()

    assert json_data == {"key": "value"}


@pytest.mark.asyncio
async def test_json_with_empty_body(mock_scope):
    receive = AsyncMock()
    request = Request(mock_scope, receive)

    receive.side_effect = [
        {"body": b"", "more_body": False},
    ]

    json_data = await request.json()

    assert json_data == {}


@pytest.mark.asyncio
async def test_form_with_urlencoded_data():
    scope = {"headers": [(b"content-type", b"application/x-www-form-urlencoded")]}
    receive = AsyncMock()
    request = Request(scope, receive)

    receive.side_effect = [
        {"body": b"key1=value1&key2=value2", "more_body": False},
    ]

    form_data = await request.form()

    assert form_data == {"key1": "value1", "key2": "value2"}


@pytest.mark.asyncio
async def test_form_with_multipart_form_data():
    scope = {
        "headers": [(b"content-type", b"multipart/form-data; boundary=boundary123")]
    }
    receive = AsyncMock()
    request = Request(scope, receive)

    receive.side_effect = [
        {
            "body": b'--boundary123\r\nContent-Disposition: form-data; name="key1"\r\n\r\nvalue1\r\n--boundary123\r\nContent-Disposition: form-data; name="key2"\r\n\r\nvalue2\r\n--boundary123--',
            "more_body": False,
        },
    ]

    form_data = await request.form()

    assert form_data == {"key1": "value1", "key2": "value2"}


@pytest.mark.asyncio
async def test_cookies_with_valid_cookie_header():
    scope = {"headers": [(b"cookie", b"key1=value1; key2=value2")]}
    receive = AsyncMock()
    request = Request(scope, receive)

    cookies = request.cookies()

    assert cookies == {"key1": "value1", "key2": "value2"}


@pytest.mark.asyncio
async def test_cookies_with_empty_cookie_header():
    scope = {"headers": [(b"cookie", b"")]}
    receive = AsyncMock()
    request = Request(scope, receive)

    cookies = request.cookies()

    assert cookies == {}


@pytest.mark.asyncio
async def test_cookies_without_cookie_header():
    scope = {"headers": []}
    receive = AsyncMock()
    request = Request(scope, receive)

    cookies = request.cookies()

    assert cookies == {}


@pytest.mark.asyncio
async def test_cookies_with_malformed_cookie_header():
    scope = {"headers": [(b"cookie", b"invalid_cookie_header")]}
    receive = AsyncMock()
    request = Request(scope, receive)

    cookies = request.cookies()

    assert cookies == {}
