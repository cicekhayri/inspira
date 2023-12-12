import os
from http import HTTPStatus

import pytest

from pyblaze.constants import APPLICATION_JSON, TEXT_PLAIN
from pyblaze.decorators.http_methods import delete, get, post, put
from pyblaze.enums import HttpMethod
from pyblaze.responses import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    TemplateResponse,
)


def test_should_throw_error_when_same_endpoint_specified_twice(app):
    @get("/home")
    def home(request):
        return HttpResponse("This is a test endpoint")

    app.add_route("/home", HttpMethod.GET, home)

    with pytest.raises(AssertionError):

        @get("/home")
        def home2(request):
            return HttpResponse("This is a test endpoint")

        app.add_route("/home", HttpMethod.GET, home2)


@pytest.mark.asyncio
async def test_basic_route(app):
    @get("/home")
    async def home(request):
        return HttpResponse("This is a test endpoint")

    app.add_route("/home", HttpMethod.GET, home)

    response = await app.test_session(app, "GET", "/home")

    assert response.status_code == 200
    assert response.text == "This is a test endpoint"


@pytest.mark.asyncio
async def test_set_cookie(app):
    @get("/home")
    async def home(request):
        http_response = HttpResponse("This is a test endpoint")
        http_response.set_cookie("my_cookie", "my_cookie_value")
        return http_response

    app.add_route("/home", HttpMethod.GET, home)

    response = await app.test_session(app, "GET", "/home")
    headers_dict = dict(response.headers)

    expected_headers = {
        "content-type": TEXT_PLAIN,
        "set-cookie": "my_cookie=my_cookie_value; Path=/",
    }

    assert headers_dict == expected_headers


@pytest.mark.asyncio
async def test_set_multiple_cookie(app):
    @get("/home")
    async def home(request):
        http_response = HttpResponse("This is a test endpoint")
        http_response.set_cookie("my_cookie", "my_cookie_value")
        http_response.set_cookie("my_second_cookie", "my_second_cookie_value")

        return http_response

    app.add_route("/home", HttpMethod.GET, home)

    response = await app.test_session(app, "GET", "/home")
    headers_dict = dict(response.headers)

    expected_header = {
        "content-type": TEXT_PLAIN,
        "set-cookie": "my_cookie=my_cookie_value; Path=/, my_second_cookie=my_second_cookie_value; Path=/",
    }

    assert headers_dict == expected_header


@pytest.mark.asyncio
async def test_response_json(app):
    @get("/home/something")
    async def home(request):
        return JsonResponse({"message": "Hej something"})

    app.add_route("/home/something", HttpMethod.GET, home)

    response = await app.test_session(app, "GET", "/home/something")

    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == APPLICATION_JSON

    content = response.json()
    expected_content = {"message": "Hej something"}

    assert content == expected_content


@pytest.mark.asyncio
async def test_response_text(app):
    @get("/home/something")
    async def home(request):
        return HttpResponse("Hej something")

    app.add_route("/home/something", HttpMethod.GET, home)

    response = await app.test_session(app, "GET", "/home/something")

    assert response.status_code == HTTPStatus.OK

    content = response.text
    expected_content = "Hej something"
    assert content == expected_content


@pytest.mark.asyncio
async def test_number_parameter(app):
    @get("/home/1")
    async def home(request):
        return JsonResponse({"id": 1})

    app.add_route("/home/1", HttpMethod.GET, home)

    response = await app.test_session(app, "GET", "/home/1")

    assert response.status_code == HTTPStatus.OK

    content = response.json()
    expected_content = {"id": 1}
    assert content == expected_content


@pytest.mark.asyncio
async def test_endpoint_without_type_defaults_to_string(app):
    @get("/home/1")
    async def home(request):
        return JsonResponse({"id": "1"})

    app.add_route("/home/1", HttpMethod.GET, home)

    response = await app.test_session(app, "GET", "/home/1")

    assert response.status_code == HTTPStatus.OK

    content = response.json()
    expected_content = {"id": "1"}
    assert content == expected_content


@pytest.mark.asyncio
async def test_posting_json(app):
    payload = {"name": "Hayri", "email": "hayri@pyblaze.com"}

    @post("/posting-json")
    async def posting_json(request):
        json_data = await request.json()
        return JsonResponse(json_data)

    app.add_route("/posting-json", HttpMethod.POST, posting_json)

    response = await app.test_session(app, "POST", "/posting-json", json=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == payload


@pytest.mark.asyncio
async def test_posting_form_data(app):
    payload = {"name": "Hayri", "email": "hayri@pyblaze.com"}

    @post("/posting-form")
    async def posting_form(request):
        json_data = await request.form()
        return JsonResponse(json_data)

    app.add_route("/posting-form", HttpMethod.POST, posting_form)

    response = await app.test_session(app, "POST", "/posting-form", data=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == payload


@pytest.mark.asyncio
async def test_delete_method(app):
    @delete("/delete/1")
    async def deleting(request):
        return HttpResponse(status_code=HTTPStatus.NO_CONTENT)

    app.add_route("/delete/1", HttpMethod.DELETE, deleting)

    response = await app.test_session(app, "DELETE", "/delete/1")

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_put_method(app):
    @put("/update/1")
    async def updating(request):
        return HttpResponse(status_code=HTTPStatus.NO_CONTENT)

    app.add_route("/update/1", HttpMethod.PUT, updating)

    response = await app.test_session(app, "PUT", "/update/1")

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_redirect(app):
    @get("/")
    async def redirect(request):
        return HttpResponseRedirect("/hello")

    app.add_route("/", HttpMethod.GET, redirect)

    response = await app.test_session(app, "GET", "/")

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["location"] == "/hello"


@pytest.mark.asyncio
async def test_template(app):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))

    @get("/example")
    async def render_template(request):
        return TemplateResponse(
            "example.html", {"name": "test"}, template_dir=template_dir
        )

    app.add_route("/example", HttpMethod.GET, render_template)

    response = await app.test_session(app, "GET", "/example")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "<h1>test</h1>"


@pytest.mark.asyncio
async def test_nonexistent_template(app):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))

    @get("/nonexistent-example")
    async def render_nonexistent_template(request):
        return TemplateResponse(
            "nonexistent_template.html", {"name": "test"}, template_dir=template_dir
        )

    app.add_route("/nonexistent-example", HttpMethod.GET, render_nonexistent_template)

    response = await app.test_session(app, "GET", "/nonexistent-example")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
