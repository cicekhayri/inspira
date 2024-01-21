import os
from unittest.mock import patch

from click.testing import CliRunner

from inspira.cli import cli
from inspira.cli.cli import controller
from inspira.cli.generate_model_file import database_file_exists, generate_model_file


def test_database_command(teardown_database_file):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["new", "database", "--name", "hello_db", "--type", "sqlite"]
    )
    assert result.exit_code == 0
    assert "Database file created successfully." in result.output


def test_run_migrations_down(teardown_migration_directory):
    runner = CliRunner()
    result = runner.invoke(cli, ["migrate", "--down"])
    assert result.exit_code == 0


def test_controller_command(runner, teardown_main_file, teardown_src_directory):
    runner.invoke(cli, ["init"])
    result = runner.invoke(cli, ["new", "controller", "order"])

    controller_file_path = os.path.join("src", "controller", "order_controller.py")

    assert os.path.isfile(controller_file_path)
    assert result.exit_code == 0


def test_controller_creation_avoided_if_exists(
    runner, teardown_main_file, teardown_src_directory
):
    runner.invoke(cli, ["init"])
    result = runner.invoke(controller, ["order"])

    controller_file_path = os.path.join("src", "controller", "order_controller.py")

    assert os.path.isfile(controller_file_path)
    assert result.exit_code == 0

    result = runner.invoke(controller, ["order"])
    assert "Controller 'order_controller.py' already exists." in result.output
    assert result.exit_code == 0


def test_controller_command_without_name(
    runner, teardown_main_file, teardown_src_directory
):
    runner.invoke(cli, ["init"])
    result = runner.invoke(cli, ["new", "controller"])

    assert "Error: Missing argument 'NAME'." in result.output
    assert result.exit_code == 2


def test_repository_command(runner, teardown_main_file, teardown_src_directory):
    runner.invoke(cli, ["init"])
    result = runner.invoke(cli, ["new", "repository", "order"])
    repository_file_path = os.path.join("src", "repository", "order_repository.py")

    assert os.path.isfile(repository_file_path)
    assert result.exit_code == 0


def test_repository_command_without_name(
    runner, teardown_main_file, teardown_src_directory
):
    runner.invoke(cli, ["init"])
    result = runner.invoke(cli, ["new", "repository"])

    assert "Error: Missing argument 'NAME'." in result.output
    assert result.exit_code == 2


def test_service_command(runner, teardown_main_file, teardown_src_directory):
    runner.invoke(cli, ["init"])
    result = runner.invoke(cli, ["new", "service", "order"])

    service_file_path = os.path.join("src", "service", "order_service.py")

    assert os.path.isfile(service_file_path)
    assert result.exit_code == 0


def test_service_command_without_name(
    runner, teardown_main_file, teardown_src_directory
):
    runner.invoke(cli, ["init"])
    result = runner.invoke(cli, ["new", "service"])
    assert "Error: Missing argument 'NAME'." in result.output
    assert result.exit_code == 2


def test_database_file_exists_when_file_exists():
    with patch('os.path.isfile', return_value=True):
        assert database_file_exists() is True

def test_database_file_exists_prints_error_message():
    with patch('inspira.cli.cli.click.echo') as mock_echo, \
         patch('os.path.isfile', return_value=False):
        database_file_exists()

        mock_echo.assert_called_once_with("Main script (database.py) not found.")

