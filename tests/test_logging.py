import logging
from http import HTTPStatus

import pytest

from pyblaze.decorators.http_methods import put
from pyblaze.enums import HttpMethod
from pyblaze.responses import HttpResponse


@pytest.mark.asyncio
async def test_logging(app, caplog):
    caplog.set_level(logging.INFO)

    @put("/update/1")
    async def updating(request):
        app.logger.info("This is logging")
        return HttpResponse(status_code=HTTPStatus.NO_CONTENT)

    app.add_route("/update/1", HttpMethod.PUT, updating)

    response = await app.test_session(app, "PUT", "/update/1")

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert "This is logging" in caplog.text
