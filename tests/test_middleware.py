from http import HTTPStatus

import pytest

from inspira.decorators.http_methods import get
from inspira.enums import HttpMethod
from inspira.responses import JsonResponse


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
