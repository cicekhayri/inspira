from click.testing import CliRunner

from inspira.cli import cli


def test_init_command(teardown_app_file):
    runner = CliRunner()
    result = runner.invoke(cli, ["init"])
    assert result.exit_code == 0
    assert "Project created successfully" in result.output


def test_resource_command(
    teardown_app_file, teardown_src_directory, setup_database_file
):
    runner = CliRunner()
    result = runner.invoke(cli, ["new", "module", "example"])
    print(result.output)
    assert result.exit_code == 0
    assert "Module 'example' created successfully." in result.output


def test_database_command(teardown_database_file):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["new", "database", "--name", "hello_db", "--type", "sqlite"]
    )
    assert result.exit_code == 0
    assert "Database file created successfully." in result.output
