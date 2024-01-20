from click.testing import CliRunner

from inspira.cli import cli
from inspira.cli.cli import migrate


def test_database_command(teardown_database_file):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["new", "database", "--name", "hello_db", "--type", "sqlite"]
    )
    assert result.exit_code == 0
    assert "Database file created successfully." in result.output


def test_run_migrations_down(runner):
    result = runner.invoke(migrate, ["--down"])
    assert result.exit_code == 0
