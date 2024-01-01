import os
import shutil
from unittest.mock import AsyncMock

import pytest

from inspira import Inspira
from inspira.config import Config
from inspira.requests import Request
from inspira.testclient import TestClient


@pytest.fixture
def app():
    return Inspira()


@pytest.fixture
def app_with_session():
    app = Inspira()
    app.secret_key = "9s09iJ6wAV8m2wKzopWiAutLWwa1rYJGLkOfa8R4PzCghYnU-O"
    app.session_type = "cookie"

    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def client_session(app_with_session):
    return TestClient(app_with_session)


@pytest.fixture
def request_with_session(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    request.session = {"user_id": 123, "username": "john_doe"}
    return request


@pytest.fixture
def teardown_app_file():
    yield
    os.remove("main.py")


@pytest.fixture
def teardown_src_directory():
    yield
    shutil.rmtree("src")


@pytest.fixture
def teardown_database_file():
    yield
    os.remove("database.py")


@pytest.fixture
def setup_database_file(teardown_database_file):
    file_name = "database.py"
    with open(file_name, "w") as file:
        # You can write content to the file if needed
        file.write("Hello, this is a new file!")
    yield


@pytest.fixture
def mock_scope():
    return {
        "headers": [(b"content-type", b"application/json")],
    }


@pytest.fixture
def sample_config():
    return Config()
