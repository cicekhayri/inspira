import os
import shutil
from unittest.mock import AsyncMock

import pytest
from click.testing import CliRunner

from inspira import Inspira
from inspira.config import Config
from inspira.constants import SRC_DIRECTORY, MIGRATION_DIRECTORY
from inspira.requests import Request
from inspira.testclient import TestClient


@pytest.fixture
def secret_key():
    return "your_secret_key"


@pytest.fixture
def app(secret_key):
    return Inspira(secret_key)


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def client_session(app):
    return TestClient(app)


@pytest.fixture
def request_with_session(mock_scope):
    receive = AsyncMock()
    send = AsyncMock()
    request = Request(mock_scope, receive, send)
    request.session = {"user_id": 123, "username": "john_doe"}
    return request


@pytest.fixture
def teardown_src_directory():
    yield
    shutil.rmtree(SRC_DIRECTORY)


@pytest.fixture
def teardown_migration_directory():
    yield
    shutil.rmtree(MIGRATION_DIRECTORY)


@pytest.fixture
def teardown_database_file():
    yield
    os.remove("database.py")


@pytest.fixture
def create_migration_files(tmpdir):
    migration_files = [
        "0001_test.sql",
        "0002_another.sql",
        "not_a_migration.txt",
        "003_missing.sql",
    ]

    path = "tests/migrations"
    os.makedirs(path, exist_ok=True)

    for file_name in migration_files:
        file_path = os.path.join(path, file_name)
        with open(file_path, "w") as file:
            file.write("Sample content")

    return migration_files, path


@pytest.fixture
def mock_scope():
    return {
        "headers": [(b"content-type", b"application/json")],
    }


@pytest.fixture
def sample_config():
    return Config()


@pytest.fixture
def user_mock():
    class User:
        def __init__(self, id):
            self.id = id

    return User


@pytest.fixture
def setup_teardown_db_session():
    from inspira.migrations.migrations import db_session, engine, initialize_database

    initialize_database(engine)
    yield db_session
    db_session.rollback()


@pytest.fixture
def runner(teardown_migration_directory):
    return CliRunner()
