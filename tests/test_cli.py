import os

import pytest
from click.testing import CliRunner

from inspira.cli import cli
from inspira.cli.create_app import create_directory_structure


def test_init_command(teardown_app_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    assert "Project created successfully" in result.output


def test_module_command(teardown_app_file, teardown_src_directory, setup_database_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "module", "example"])
    assert result.exit_code == 0
    assert "Module 'example' created successfully." in result.output


def test_module_command_missing_name():
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "module"])

    assert result.exit_code == 2
    assert "Error: Missing argument 'NAME'." in result.output


def test_module_command_existing_module(
    setup_test_environment,
    teardown_src_directory,
    teardown_app_file,
    setup_database_file,
):
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "module", "module1"])

    assert result.exit_code == 0
    assert "Module 'module1' already exists." in result.output


def test_database_command(teardown_database_file):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["new", "database", "--name", "hello_db", "--type", "sqlite"]
    )
    assert result.exit_code == 0
    assert "Database file created successfully." in result.output
