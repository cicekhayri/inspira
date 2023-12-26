import json
import os
from http import HTTPStatus

import pytest

from inspira import Inspira
from inspira.constants import APPLICATION_JSON, TEXT_PLAIN, UTF8
from inspira.decorators.http_methods import delete, get, post, put
from inspira.enums import HttpMethod
from inspira.responses import (HttpResponse, HttpResponseRedirect,
                               JsonResponse, TemplateResponse)


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
async def test_basic_route(client, app):
    @get("/home")
    async def home(request):
        return HttpResponse("This is a test endpoint")

    app.add_route("/home", HttpMethod.GET, home)

    response = await client.get("/home")

    assert response.status_code == 200
    assert response.text == "This is a test endpoint"


@pytest.mark.asyncio
async def test_set_cookie_with_route(app, client):
    @get("/home")
    async def home(request):
        http_response = HttpResponse("This is a test endpoint")
        http_response.set_cookie("my_cookie", "my_cookie_value")
        return http_response

    app.add_route("/home", HttpMethod.GET, home)

    response = await client.get("/home")
    headers_dict = dict(response.headers)

    expected_headers = {
        "content-type": TEXT_PLAIN,
        "set-cookie": "my_cookie=my_cookie_value; Path=/, "
        "session=ImUzMD0uYTU2OTRkZDdkOTlhMTFmOTNiODAyYzRkMzE3MTZlYTk5OTE0NDA1N2Q2MzFkNWZlZWNmYTg4MDJkOTF"
        "lMTgzNSI=.8991ce9b78ed5878c22fdb0d757137409a61c26daf53e9c4ea41ab0a5fe8c8f9; Path=/; "
        "Secure; HttpOnly",
    }

    assert headers_dict == expected_headers


@pytest.mark.asyncio
async def test_set_multiple_cookie(app_with_session, client_session):
    @get("/home")
    async def home(request):
        http_response = HttpResponse("This is a test endpoint")
        http_response.set_cookie("my_cookie", "my_cookie_value")
        http_response.set_cookie("my_second_cookie", "my_second_cookie_value")

        return http_response

    app_with_session.add_route("/home", HttpMethod.GET, home)

    response = await client_session.get("/home")
    headers_dict = dict(response.headers)

    expected_header = {
        "content-type": TEXT_PLAIN,
        "set-cookie": "my_cookie=my_cookie_value; Path=/, my_second_cookie=my_second_cookie_value; Path=/, "
        "session=ImUzMD0uYWIxZTEzYjM5OWU4NmVlOTQxYzFiMDRiZjM4ODg5YjNmZmM1ZWJjZjBiYjc3ZDFjZjI0YzQxZTY5M"
        "2U5NzUwNSI=.94676004da3849de0f181a24441f2b3c9199f761e1392e3ceb1c1bc89267594f; Path=/; "
        "Secure; HttpOnly",
    }

    assert headers_dict == expected_header


@pytest.mark.asyncio
async def test_response_json(app, client):
    @get("/home/something")
    async def home(request):
        return JsonResponse({"message": "Hej something"})

    app.add_route("/home/something", HttpMethod.GET, home)

    response = await client.get("/home/something")

    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == APPLICATION_JSON

    content = response.json()
    expected_content = {"message": "Hej something"}

    assert content == expected_content


@pytest.mark.asyncio
async def test_response_text(app, client):
    @get("/home/something")
    async def home(request):
        return HttpResponse("Hej something")

    app.add_route("/home/something", HttpMethod.GET, home)

    response = await client.get("/home/something")

    assert response.status_code == HTTPStatus.OK

    content = response.text
    expected_content = "Hej something"
    assert content == expected_content


@pytest.mark.asyncio
async def test_number_parameter(app, client):
    @get("/home/1")
    async def home(request):
        return JsonResponse({"id": 1})

    app.add_route("/home/1", HttpMethod.GET, home)

    response = await client.get("/home/1")

    assert response.status_code == HTTPStatus.OK

    content = response.json()
    expected_content = {"id": 1}
    assert content == expected_content


@pytest.mark.asyncio
async def test_endpoint_without_type_defaults_to_string(app, client):
    @get("/home/1")
    async def home(request):
        return JsonResponse({"id": "1"})

    app.add_route("/home/1", HttpMethod.GET, home)

    response = await client.get("/home/1")

    assert response.status_code == HTTPStatus.OK

    content = response.json()
    expected_content = {"id": "1"}
    assert content == expected_content


@pytest.mark.asyncio
async def test_posting_json(app, client):
    payload = {"name": "Hayri", "email": "hayri@inspira.com"}

    @post("/posting-json")
    async def posting_json(request):
        json_data = await request.json()
        return JsonResponse(json_data)

    app.add_route("/posting-json", HttpMethod.POST, posting_json)

    response = await client.post("/posting-json", json=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == payload


@pytest.mark.asyncio
async def test_posting_form_data(client, app):
    payload = {"name": "Hayri", "email": "hayri@inspira.com"}

    @post("/posting-form")
    async def posting_form(request):
        json_data = await request.form()
        return JsonResponse(json_data)

    app.add_route("/posting-form", HttpMethod.POST, posting_form)

    response = await client.post("/posting-form", data=payload)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == payload


@pytest.mark.asyncio
async def test_delete_method(client, app):
    @delete("/delete/1")
    async def deleting(request):
        return HttpResponse(status_code=HTTPStatus.NO_CONTENT)

    app.add_route("/delete/1", HttpMethod.DELETE, deleting)

    response = await client.delete("/delete/1")

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_put_method(app, client):
    @put("/update/1")
    async def updating(request):
        return HttpResponse(status_code=HTTPStatus.NO_CONTENT)

    app.add_route("/update/1", HttpMethod.PUT, updating)

    response = await client.put("/update/1")

    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_redirect(app, client):
    @get("/")
    async def redirect(request):
        return HttpResponseRedirect("/hello")

    app.add_route("/", HttpMethod.GET, redirect)

    response = await client.get("/")

    assert response.status_code == HTTPStatus.FOUND
    assert response.headers["location"] == "/hello"


@pytest.mark.asyncio
async def test_template(client, app):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))

    @get("/example")
    async def render_template(request):
        return TemplateResponse(
            "example.html", {"name": "test"}, template_dir=template_dir
        )

    app.add_route("/example", HttpMethod.GET, render_template)

    response = await client.get("/example")

    assert response.status_code == HTTPStatus.OK
    assert response.text == "<h1>test</h1>"


@pytest.mark.asyncio
async def test_serialize_content_byte():
    response = HttpResponse(content=b"example")
    result = await response.serialize_content()
    assert result == b"example"


@pytest.mark.asyncio
async def test_serialize_content_json():
    response = JsonResponse(content={"key": "value"})
    result = await response.serialize_content()
    expected_result = json.dumps({"key": "value"}).encode(UTF8)
    assert result == expected_result


@pytest.mark.asyncio
async def test_serialize_content_default():
    response = HttpResponse(content="example")
    result = await response.serialize_content()
    expected_result = b"example"
    assert result == expected_result


@pytest.mark.asyncio
async def test_encoded_headers():
    response = HttpResponse(headers={"Key1": "Value1", "Key2": ["Value2a", "Value2b"]})
    result = await response.encoded_headers()

    expected_result = [
        (b"content-type", TEXT_PLAIN.encode(UTF8)),
        (b"Key1", b"Value1"),
        (b"Key2", b"Value2a"),
        (b"Key2", b"Value2b"),
    ]

    assert result == expected_result


@pytest.mark.asyncio
async def test_set_cookie():
    response = HttpResponse()
    response.set_cookie("user", "john_doe", max_age=3600, path="/")
    headers = response.headers.get("set-cookie", [])
    assert len(headers) == 1
    assert "user=john_doe" in headers[0]
    assert "Max-Age=3600" in headers[0]
    assert "Path=/" in headers[0]
