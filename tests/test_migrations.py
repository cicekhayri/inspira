import os
from unittest.mock import MagicMock, patch

from sqlalchemy import Column, Integer, String, inspect

from inspira.constants import SRC_DIRECTORY, MIGRATION_DIRECTORY
from inspira.migrations.migrations import (
    Base,
    Migration,
    create_migrations,
    db_session,
    engine,
    execute_sql_file,
    generate_create_table_sql,
    get_existing_columns,
    get_existing_indexes,
    insert_migration,
)
from inspira.migrations.utils import (
    generate_column_sql,
    get_latest_migration_number,
    get_migration_files,
    get_or_create_migration_directory,
    load_model_file,
)


def test_get_or_create_migration_directory(
    setup_test_environment, teardown_src_directory
):
    controller_name = "module1"
    controller_directory = os.path.join(SRC_DIRECTORY, controller_name)
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


def test_generate_create_table_sql():
    table_name = "users"

    class User(Base):
        __tablename__ = table_name
        id = Column(Integer, primary_key=True)
        name = Column("name", String(50))

    sql_str = generate_create_table_sql(table_name)

    expected_sql = "\nCREATE TABLE users (\n\tid INTEGER NOT NULL, \n\tname VARCHAR(50), \n\tPRIMARY KEY (id)\n);\n"

    assert sql_str == expected_sql


@patch("inspira.migrations.utils.importlib.util.module_from_spec")
@patch("inspira.migrations.utils.importlib.util.spec_from_file_location")
@patch("inspira.migrations.utils.os.path.join")
@patch("inspira.migrations.utils.singularize")
def test_load_model_file(
    mock_singularize, mock_join, mock_spec_from_file_location, mock_module_from_spec
):
    entity_name = "customers"

    mock_singularize.return_value = "customer"
    mock_join.return_value = "src/your_entity/your_entity_singular.py"
    mock_spec = MagicMock()
    mock_module = MagicMock()
    mock_spec_from_file_location.return_value = mock_spec
    mock_module_from_spec.return_value = mock_module

    result = load_model_file(entity_name)

    mock_join.assert_any_call(
        SRC_DIRECTORY, entity_name.replace(".", "/" + entity_name)
    )
    mock_join.assert_any_call(
        mock_join.return_value, f"{mock_singularize.return_value}.py"
    )
    mock_spec_from_file_location.assert_called_once_with(
        mock_singularize.return_value.capitalize(), mock_join.return_value
    )
    mock_module_from_spec.assert_called_once_with(mock_spec)
    mock_spec.loader.exec_module.assert_called_once_with(mock_module)

    assert result == mock_module


def test_generate_column_sql():
    column1 = Column("id", Integer, primary_key=True)
    column2 = Column("name", String(50), nullable=False)
    column3 = Column("email", String(255), nullable=True)

    result1 = generate_column_sql(column1)
    result2 = generate_column_sql(column2)
    result3 = generate_column_sql(column3)

    assert result1 == "id INTEGER PRIMARY KEY NOT NULL "
    assert result2 == "name VARCHAR(50) NOT NULL "
    assert result3 == "email VARCHAR(255) NULL "


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
