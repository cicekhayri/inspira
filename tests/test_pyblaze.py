from http import HTTPStatus

import pytest

from pyblaze.decorators.http_methods import get
from pyblaze.enums import HttpMethod
from pyblaze.responses import JsonResponse


@pytest.mark.asyncio
async def test_add_route(app):
    @get("/example")
    async def example_handler(request):
        return JsonResponse({"message": "Example response"})

    app.add_route("/example", HttpMethod.GET, example_handler)

    response = await app.test_session(app, "GET", "/example")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Example response"}
