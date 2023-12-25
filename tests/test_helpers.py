from unittest.mock import mock_open, patch

from inspira.constants import TEXT_HTML
from inspira.helpers.error_templates import (
    format_method_not_allowed_exception,
    format_not_found_exception,
    format_server_exception,
)
from inspira.utils.controller_parser import parse_controller_decorators


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


def test_parse_controller_decorators_with_path_decorator():
    code = """
@path("/example")
class MyController:
    pass
    """
    with patch("builtins.open", mock_open(read_data=code)):
        result = parse_controller_decorators("fake_file_path")
        assert result is True


def test_parse_controller_decorators_with_websocket_decorator():
    code = """
@websocket("/example")
class MyController:
    pass
    """
    with patch("builtins.open", mock_open(read_data=code)):
        result = parse_controller_decorators("fake_file_path")
        assert result is True


def test_parse_controller_decorators_without_matching_decorators():
    code = """
class MyController:
    pass
    """
    with patch("builtins.open", mock_open(read_data=code)):
        result = parse_controller_decorators("fake_file_path")
        assert result is False


def test_parse_controller_decorators_with_invalid_code():
    code = "invalid_python_code"
    with patch("builtins.open", mock_open(read_data=code)):
        result = parse_controller_decorators("fake_file_path")
        assert result is False
