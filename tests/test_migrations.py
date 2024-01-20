import os
from unittest.mock import patch

from inspira.cli.cli import migrate
from inspira.constants import MIGRATION_DIRECTORY
from inspira.migrations.migrations import (
    Migration,
    db_session,
    execute_down_migration,
    execute_up_migration,
    insert_migration,
    run_migrations,
)
from inspira.migrations.utils import (
    get_latest_migration_number,
    get_migration_files,
    get_or_create_migration_directory,
)


def test_execute_up_migration(capsys, mock_connection, tmp_path):
    migration_name = "test_migration"
    migration_content = "-- Up\nCREATE TABLE test_table (id SERIAL PRIMARY KEY);\n"

    migration_file_path = tmp_path / f"{migration_name}.sql"
    with open(migration_file_path, "w") as migration_file:
        migration_file.write(migration_content)

    execute_up_migration(mock_connection, migration_file_path, migration_name)

    expected_sql = "CREATE TABLE test_table (id SERIAL PRIMARY KEY)"

    # Extract SQL string from the call and compare as a string
    actual_calls = [
        call_args[0][0].text for call_args in mock_connection.execute.call_args_list
    ]

    assert expected_sql in actual_calls
    assert "Applying 'Up' migration for test_migration" in capsys.readouterr().out


def test_execute_down_migration(capsys, mock_connection, tmp_path):
    migration_name = "test_migration"
    migration_content = "-- Down\nDROP TABLE test_table;\n"

    migration_file_path = tmp_path / f"{migration_name}.sql"
    with open(migration_file_path, "w") as migration_file:
        migration_file.write(migration_content)

    execute_down_migration(mock_connection, migration_file_path, migration_name)

    expected_sql = "DROP TABLE test_table"

    # Extract SQL string from the call and compare as a string
    actual_calls = [
        call_args[0][0].text for call_args in mock_connection.execute.call_args_list
    ]

    assert expected_sql in actual_calls
    assert "Applying 'Down' migration for test_migration" in capsys.readouterr().out


def test_run_migrations_up(capsys, mock_connection, tmp_path):
    migration_name = "test_migration"
    migration_content = "-- Up\nCREATE TABLE test_table (id SERIAL PRIMARY KEY);\n"

    migration_file_path = tmp_path / f"{migration_name}.sql"
    with open(migration_file_path, "w") as migration_file:
        migration_file.write(migration_content)

    run_migrations()

    mock_connection.execute.assert_called_once_with(
        "CREATE TABLE test_table (id SERIAL PRIMARY KEY)"
    )
    assert "Applying 'Up' migration for test_migration" in capsys.readouterr().out


def test_get_or_create_migration_directory():
    migration_directory = os.path.join(MIGRATION_DIRECTORY)
    with patch("inspira.logging.log.error") as log_error_mock:
        result = get_or_create_migration_directory()

    assert result == migration_directory
    assert os.path.exists(result)
    assert os.path.isdir(result)
    assert os.path.exists(os.path.join(result, "__init__.py"))
    log_error_mock.assert_not_called()


def test_get_migration_files(create_migration_files, teardown_migration_directory):
    migration_files, migration_dir = create_migration_files

    with patch("inspira.migrations.utils.os.listdir", return_value=migration_files):
        result = get_migration_files(migration_dir)

    assert result == [
        os.path.join(migration_dir, "0001_test.sql"),
        os.path.join(migration_dir, "0002_another.sql"),
        os.path.join(migration_dir, "003_missing.sql"),
    ]


@patch("inspira.migrations.utils.os.listdir")
def test_get_latest_migration_number(mock_listdir):
    migration_dir = "tests/migrations"
    migration_files = ["0001_test.sql", "0002_another.sql", "003_missing.sql"]

    mock_listdir.return_value = migration_files

    result = get_latest_migration_number(migration_dir)

    assert result == 3


def test_insert_migration(setup_teardown_db_session):
    current_version = 0
    migration_name = "example_migration"
    insert_migration(current_version, migration_name)

    result = (
        db_session.query(Migration)
        .filter_by(version=current_version + 1, migration_name=migration_name)
        .first()
    )

    assert result.version == 1
    assert result.migration_name == migration_name


def test_run_migrations_up(runner, monkeypatch, tmpdir, teardown_migration_directory):
    migration_file_path = tmpdir / "0001_create_table_customers.sql"
    migration_file_path.write_text(
        """
-- Up
CREATE TABLE customers (
    id INTEGER NOT NULL, 
    name VARCHAR(50) NOT NULL, 
    PRIMARY KEY (id)
);
-- Down
DROP TABLE customers;
""",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "inspira.migrations.migrations.initialize_database", lambda engine: None
    )
    monkeypatch.setattr(
        "inspira.migrations.utils.get_or_create_migration_directory",
        lambda: str(tmpdir),
    )

    result = runner.invoke(migrate)

    assert result.exit_code == 0
