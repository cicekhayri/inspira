from http import HTTPStatus
from http.cookies import SimpleCookie

import pytest

from inspira.auth.auth_utils import login_user, decode_auth_token
from inspira.auth.decorators import login_required
from inspira.auth.mixins.user_mixin import AnonymousUserMixin
from inspira.decorators.http_methods import get
from inspira.enums import HttpMethod
from inspira.logging import log
from inspira.middlewares.cors import CORSMiddleware
from inspira.middlewares.sessions import SessionMiddleware
from inspira.middlewares.user_loader import UserLoaderMiddleware
from inspira.requests import Request, RequestContext
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
async def test_set_session_success(app, secret_key, client):
    session_middleware = SessionMiddleware()

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

    decoded_session = decode_session_data(session_cookie.value, secret_key)
    expected_session = {"message": "Hej"}

    expiration_time = decoded_session.pop("expiration_time", None)
    session_id = decoded_session.pop("session_id", None)

    assert decoded_session == expected_session
    assert response.status_code == HTTPStatus.OK
    assert expiration_time is not None
    assert session_id is not None


@pytest.mark.asyncio
async def test_invalid_signature_exception(app, client):
    session_middleware = SessionMiddleware()

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

    decoded_session = decode_session_data(session_cookie.value, "wrong_token")

    assert decoded_session is None
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_remove_session_success(app, client):
    session_middleware = SessionMiddleware()

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

    assert session_cookie.value == ""
    assert response2.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_session_success(app, client):
    session_middleware = SessionMiddleware()

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
    session_middleware = SessionMiddleware()

    app.add_middleware(session_middleware)

    @get("/remove")
    async def remove_route(request: Request):
        log.info(f"Session before removal: {request.session}")

        request.remove_session("nonexistent_key")
        return HttpResponse("Session key removed successfully")

    app.add_route("/remove", HttpMethod.GET, remove_route)

    response = await client.get("/remove")
    set_cookie_header = response.headers.get("set-cookie", "")

    cookies = SimpleCookie(set_cookie_header)
    session_cookie = cookies.get("session")

    assert session_cookie.value == ""
    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_user_loader_middleware(app, client, user_mock, secret_key):
    session_middleware = SessionMiddleware()

    user_loader_middleware = UserLoaderMiddleware(user_mock)

    app.add_middleware(session_middleware)
    app.add_middleware(user_loader_middleware)

    @get("/get")
    async def get_route(request: Request):
        user = user_mock(id=1)
        login_user(user.id)
        return HttpResponse(f"User ID: 1323")

    app.add_route("/get", HttpMethod.GET, get_route)

    response = await client.get("/get")
    set_cookie_header = response.headers.get("set-cookie", "")

    assert set_cookie_header is not None
    assert "session=" in set_cookie_header

    cookies = SimpleCookie(set_cookie_header)
    session_cookie = cookies.get("session")

    assert session_cookie is not None

    decoded_session = decode_session_data(session_cookie.value, secret_key)
    get_user_id = decode_auth_token(decoded_session["token"])

    assert get_user_id == 1


@pytest.mark.asyncio
async def test_user_not_logged_in(app, client, secret_key, user_mock):
    session_middleware = SessionMiddleware()
    user_loader_middleware = UserLoaderMiddleware(user_mock)
    app.add_middleware(session_middleware)
    app.add_middleware(user_loader_middleware)

    @get("/protected")
    @login_required
    async def protected(request: Request):
        return HttpResponse("Protected Route")

    app.add_route("/protected", HttpMethod.GET, protected)

    response = await client.get("/protected")

    assert response.status_code == HTTPStatus.UNAUTHORIZED.value
    assert "Unauthorized" in response.text


@pytest.mark.asyncio
async def test_user_loader_middleware_anonymous_user(
    app, client, secret_key, user_mock
):
    user_loader_middleware = UserLoaderMiddleware(user_mock)
    app.add_middleware(user_loader_middleware)

    @get("/protected")
    async def protected(request: Request):
        user_authenticated = request.user.is_authenticated
        return JsonResponse({"user_authenticated": user_authenticated})

    app.add_route("/protected", HttpMethod.GET, protected)

    response = await client.get("/protected")

    assert response.status_code == 200
    assert response.json() == {"user_authenticated": False}

    user_in_method = RequestContext.get_current_user()
    assert isinstance(user_in_method, AnonymousUserMixin)
