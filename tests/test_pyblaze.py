import importlib
import inspect
import os
import sys
import tempfile
from http import HTTPStatus
from unittest.mock import Mock

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


def test_discover_controllers(app, monkeypatch):
    monkeypatch.setattr(os, "getcwd", Mock(return_value="/path/to"))
    monkeypatch.setattr(os.path, "join", lambda *args: "/".join(args))
    monkeypatch.setattr(
        os, "walk", lambda path: [("/path/to/src", [], ["controller_file.py"])]
    )
    monkeypatch.setattr(os.path, "relpath", lambda *args: "controller_file.py")

    app._is_controller_file = Mock(return_value=True)
    app._add_resources = Mock()

    app.discover_controllers()

    app._is_controller_file.assert_called_once_with("/path/to/src/controller_file.py")
    app._add_resources.assert_called_once_with("src.controller_file")
