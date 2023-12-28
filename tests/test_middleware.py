import logging
from http import HTTPStatus

import pytest

from inspira.decorators.http_methods import get
from inspira.enums import HttpMethod
from inspira.middlewares.cors import CORSMiddleware
from inspira.responses import JsonResponse, HttpResponse


@pytest.mark.asyncio
async def test_middleware(app, client):
    async def sample_middleware(request):
        request.extra_data = "Modified by middleware"
        return request

    # Use the middleware
    app.add_middleware(sample_middleware)

    @get("/test")
    async def test_route(request):
        return JsonResponse({"message": request.extra_data})

    app.add_route("/test", HttpMethod.GET, test_route)

    response = await client.get("/test")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "Modified by middleware"


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
    async def test_route(request):
        return JsonResponse({"message": "hello"})

    app.add_route("/test", HttpMethod.GET, test_route)

    response_allowed = await client.get("/test", headers={'Origin': 'http://localhost:8000'})

    assert response_allowed.headers['Access-Control-Allow-Origin'] == 'http://localhost:8000'
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
    async def test_route(request):
        return HttpResponse("hello")

    app.add_route("/test", HttpMethod.GET, test_route)

    not_response_allowed = await client.get("/test", headers={'Origin': 'http://localhost:3000'})

    assert not_response_allowed.status_code == HTTPStatus.FORBIDDEN