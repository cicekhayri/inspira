import os
import shutil

import pytest

from pyblaze import PyBlaze


@pytest.fixture
def app():
    return PyBlaze()


@pytest.fixture
def teardown_app_file():
    yield
    os.remove("app.py")


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
