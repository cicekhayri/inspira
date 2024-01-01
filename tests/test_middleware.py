from http import HTTPStatus
from http.cookies import SimpleCookie

import pytest

from inspira.decorators.http_methods import get
from inspira.enums import HttpMethod
from inspira.middlewares.cors import CORSMiddleware
from inspira.middlewares.sessions import SessionMiddleware
from inspira.requests import Request
from inspira.responses import JsonResponse, HttpResponse
from inspira.utils.session_utils import decode_session_data


@pytest.mark.asyncio
async def test_cors_middleware(app, client):
    origins = ["http://localhost:8000"]

    cors_middleware = CORSMiddleware(
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(cors_middleware)

    @get("/test")
    async def test_route(request: Request):
        return JsonResponse({"message": "hello"})

    app.add_route("/test", HttpMethod.GET, test_route)

    response_allowed = await client.get(
        "/test", headers={"Origin": "http://localhost:8000"}
    )

    assert (
        response_allowed.headers["Access-Control-Allow-Origin"]
        == "http://localhost:8000"
    )
    assert response_allowed.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_cors_middleware_origin(app, client):
    origins = ["http://localhost:8000"]

    cors_middleware = CORSMiddleware(
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(cors_middleware)

    @get("/test")
    async def test_route(request: Request):
        return HttpResponse("hello")

    app.add_route("/test", HttpMethod.GET, test_route)

    not_response_allowed = await client.get(
        "/test", headers={"Origin": "http://localhost:3000"}
    )

    assert not_response_allowed.status_code == HTTPStatus.FORBIDDEN


@pytest.mark.asyncio
async def test_cors_middleware_without_origin_header(app, client):
    origins = ["http://localhost:8000"]

    cors_middleware = CORSMiddleware(
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(cors_middleware)

    @get("/test")
    async def test_route(request: Request):
        return HttpResponse("hello")

    app.add_route("/test", HttpMethod.GET, test_route)

    not_response_allowed = await client.get("/test")

    assert not_response_allowed.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_set_session_success(app, client):
    session_middleware = SessionMiddleware(secret_key="dummy")

    app.add_middleware(session_middleware)

    @get("/test")
    async def test_route(request: Request):
        request.set_session("message", "Hej")
        return HttpResponse("hello")

    app.add_route("/test", HttpMethod.GET, test_route)

    response = await client.get("/test")
    set_cookie_header = response.headers.get("set-cookie", "")

    cookies = SimpleCookie(set_cookie_header)
    session_cookie = cookies.get("session")

    assert session_cookie is not None

    decoded_session = decode_session_data(session_cookie.value, "dummy")
    expected_session = {"message": "Hej"}

    assert decoded_session == expected_session
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_invalid_signature_exception(app, client):
    cors_middleware = SessionMiddleware(secret_key="dummy")

    app.add_middleware(cors_middleware)

    @get("/test")
    async def test_route(request: Request):
        request.set_session("message", "Hej")
        return HttpResponse("hello")

    app.add_route("/test", HttpMethod.GET, test_route)

    response = await client.get("/test")
    set_cookie_header = response.headers.get("set-cookie", "")

    cookies = SimpleCookie(set_cookie_header)
    session_cookie = cookies.get("session")

    assert session_cookie is not None

    with pytest.raises(ValueError, match="Invalid signature"):
        decode_session_data(session_cookie.value, "wrong_token")

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_remove_session_success(app, client):
    session_middleware = SessionMiddleware(secret_key="dummy")

    app.add_middleware(session_middleware)

    @get("/test")
    async def test_route(request: Request):
        request.set_session("message", "Hej")
        return HttpResponse("hello")

    @get("/remove")
    async def remove_route(request: Request):
        request.remove_session("message")
        return HttpResponse("hello")

    app.add_route("/test", HttpMethod.GET, test_route)

    response1 = await client.get("/test")

    assert "set-cookie" in response1.headers

    app.add_route("/remove", HttpMethod.GET, remove_route)
    response2 = await client.get("/remove")

    assert "set-cookie" in response2.headers
    set_cookie_header = response2.headers.get("set-cookie", "")

    cookies = SimpleCookie(set_cookie_header)
    session_cookie = cookies.get("session")

    assert session_cookie.value == ''
    assert response2.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_session_success(app, client):
    session_middleware = SessionMiddleware(secret_key="dummy")

    app.add_middleware(session_middleware)

    @get("/get")
    async def get_route(request: Request):
        request.set_session("user_id", 123)
        user_id = request.get_session("user_id")
        return HttpResponse(f"User ID: {user_id}")

    app.add_route("/get", HttpMethod.GET, get_route)

    response = await client.get("/get")

    assert response.content == b"User ID: 123"

@pytest.mark.asyncio
async def test_remove_nonexistent_key(app, client):
    session_middleware = SessionMiddleware(secret_key="dummy")

    app.add_middleware(session_middleware)

    @get("/remove")
    async def remove_route(request: Request):
        print(f"Session before removal: {request.session}")

        request.remove_session("nonexistent_key")
        return HttpResponse("Session key removed successfully")

    app.add_route("/remove", HttpMethod.GET, remove_route)

    response = await client.get("/remove")
    set_cookie_header = response.headers.get("set-cookie", "")

    cookies = SimpleCookie(set_cookie_header)
    session_cookie = cookies.get("session")

    assert session_cookie.value == ''
    assert response.status_code == HTTPStatus.OK