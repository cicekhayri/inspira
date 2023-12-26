import inspect
import os
from http import HTTPStatus
from unittest.mock import Mock

import pytest

from inspira.decorators.http_methods import get
from inspira.enums import HttpMethod
from inspira.responses import JsonResponse
from inspira.utils.param_converter import convert_param_type


@pytest.mark.asyncio
async def test_add_route(app, client):
    @get("/example")
    async def example_handler(request):
        return JsonResponse({"message": "Example response"})

    app.add_route("/example", HttpMethod.GET, example_handler)

    response = await client.get("/example")

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
    app._add_routes = Mock()

    app.discover_controllers()

    app._is_controller_file.assert_called_once_with("/path/to/src/controller_file.py")
    app._add_routes.assert_called_once_with("src.controller_file")


def test_convert_param_type_with_valid_type(app):
    result = convert_param_type("10", int)
    assert result == 10, "Expected the value to be converted to int"


def test_convert_param_type_with_none_type(app):
    result = convert_param_type("10", None)
    assert result == "10", "Expected the value to be converted to str"


def test_convert_param_type_with_empty_type(app):
    result = convert_param_type("10", inspect.Parameter.empty)
    assert result == "10", "Expected the value to be converted to str"
