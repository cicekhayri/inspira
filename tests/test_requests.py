from unittest.mock import AsyncMock

import pytest

from pyblaze.requests import Request, RequestContext


def test_set_request():
    scope = {"headers": [(b"content-type", b"application/json")]}
    receive = AsyncMock()
    request = Request(scope, receive)
    RequestContext.set_request(request)

    assert RequestContext.get_request() == request


@pytest.mark.asyncio
async def test_json_with_valid_json():
    scope = {"headers": [(b"content-type", b"application/json")]}
    receive = AsyncMock()
    request = Request(scope, receive)

    receive.side_effect = [
        {"body": b'{"key": "value"}', "more_body": False},
    ]

    json_data = await request.json()

    assert json_data == {"key": "value"}


@pytest.mark.asyncio
async def test_json_with_empty_body():
    scope = {"headers": [(b"content-type", b"application/json")]}
    receive = AsyncMock()
    request = Request(scope, receive)

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