from pyblaze.constants import TEXT_HTML
from pyblaze.helpers.error_templates import (
    format_server_exception,
    format_not_found_exception,
    format_method_not_allowed_exception,
)


def test_format_server_exception():
    response = format_server_exception()
    assert response.content_type == TEXT_HTML
    assert response.status_code == 500
    assert "Internal Server Error" in response.content


def test_format_not_found_exception():
    response = format_not_found_exception()
    assert response.content_type == TEXT_HTML
    assert response.status_code == 404
    assert "Ooops!!! The page you are looking for is not found" in response.content


def test_format_method_not_allowed_exception():
    response = format_method_not_allowed_exception()
    assert response.content_type == TEXT_HTML
    assert response.status_code == 405
    assert "Method Not Allowed" in response.content
    assert "The method is not allowed for the requested URL." in response.content
