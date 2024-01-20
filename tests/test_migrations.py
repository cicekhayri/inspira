import os
from unittest.mock import patch

from sqlalchemy import inspect

from inspira.cli.cli import migrate
from inspira.constants import MIGRATION_DIRECTORY
from inspira.migrations.migrations import (
    Migration,
    create_migrations,
    db_session,
    engine,
    execute_sql_file,
    get_existing_columns,
    get_existing_indexes,
    insert_migration,
)
from inspira.migrations.utils import (
    get_latest_migration_number,
    get_migration_files,
    get_or_create_migration_directory,
)


def test_get_or_create_migration_directory(
    setup_test_environment, teardown_src_directory
):
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


def test_execute_sql_file(sample_sql_file):
    execute_sql_file(sample_sql_file)

    inspector = inspect(engine)

    assert "users" in inspector.get_table_names()


def test_get_existing_columns_table_exists(sample_sql_file):
    execute_sql_file(sample_sql_file)
    result = get_existing_columns("users")
    assert result == ["id", "name", "email"]


def test_get_existing_columns_table_does_not_exist():
    table_name = "non_existent_table"
    result = get_existing_columns(table_name)
    assert result is None


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


def test_get_existing_indexes(
    setup_test_environment, teardown_src_directory, add_index_users
):
    execute_sql_file(add_index_users)
    indexes = get_existing_indexes("users")

    assert len(indexes) == 1
    assert "ix_users_name" in indexes


def test_empty_migration_file(
    setup_test_environment, teardown_src_directory, teardown_migration_directory
):
    empty_migration_file = "0001_empty_migration"
    create_migrations("empty_migration")
    expected_migration_file = f"migrations/{empty_migration_file}.sql"
    assert os.path.exists(
        expected_migration_file
    ), f"Migration file {expected_migration_file} not found."


def test_run_migrations_up(runner, monkeypatch, tmpdir):
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
