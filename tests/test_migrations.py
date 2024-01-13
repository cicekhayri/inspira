import os
from unittest.mock import patch, MagicMock

from sqlalchemy import Column, Integer, String, inspect

from inspira.constants import SRC_DIRECTORY
from inspira.migrations.migrations import (
    execute_sql_file,
    engine,
    Base,
    generate_create_table_sql,
    get_existing_columns,
    insert_migration,
    db_session,
    Migration,
    get_existing_indexes,
)
from inspira.migrations.utils import (
    get_or_create_migration_directory,
    generate_drop_column_sql,
    generate_add_column_sql,
    get_migration_files,
    generate_rename_column_sql,
    load_model_file,
    generate_column_sql,
    get_latest_migration_number,
    get_all_module_names,
)


def test_get_or_create_migration_directory(setup_test_environment,teardown_src_directory):
    controller_name = "module1"
    controller_directory = os.path.join(SRC_DIRECTORY, controller_name)
    migration_directory = os.path.join(controller_directory, "migrations")
    with patch('inspira.logging.log.error') as log_error_mock:
        result = get_or_create_migration_directory(controller_name)

    assert result == migration_directory
    assert os.path.exists(result)
    assert os.path.isdir(result)
    assert os.path.exists(os.path.join(result, "__init__.py"))
    log_error_mock.assert_not_called()


def test_get_or_create_migration_directory_missing_module(setup_test_environment, teardown_src_directory):
    controller_name = "Module"

    with patch('inspira.logging.log.error') as log_error_mock:
        result = get_or_create_migration_directory(controller_name)

    assert result is None
    assert not os.path.exists(result) if result else True
    assert log_error_mock.called

@patch("inspira.migrations.utils.generate_migration_file")
@patch("inspira.migrations.utils.generate_column_sql")
def test_generate_drop_column_sql(
    mock_generate_column_sql, mock_generate_migration_file
):
    entity_name = "customers"
    existing_columns = ["email_dc"]
    new_columns = [Column("email_dc", String(255)), Column("name", String(50))]

    expected_sql_statements = "ALTER TABLE customers DROP COLUMN email_dc;\n"
    expected_migration_name = "drop_column_email_dc_"

    mock_generate_column_sql.side_effect = lambda col: f"{col.key} VARCHAR(50)"
    generate_drop_column_sql(entity_name, existing_columns, new_columns)

    mock_generate_migration_file.assert_called_once_with(
        entity_name, expected_sql_statements, expected_migration_name
    )


@patch("inspira.migrations.utils.generate_migration_file")
@patch("inspira.migrations.utils.generate_column_sql")
def test_generate_add_column_sql(
    mock_generate_column_sql, mock_generate_migration_file
):
    entity_name = "customers"
    existing_columns = ["email_dc"]
    new_columns = [Column("email_dc", String(255)), Column("name", String(50))]

    expected_sql_statements = "ALTER TABLE customers ADD COLUMN name VARCHAR(50);\n"
    expected_migration_name = "add_column_name"

    mock_generate_column_sql.side_effect = lambda col: f"{col.key} VARCHAR(50)"
    generate_add_column_sql(entity_name, existing_columns, new_columns)

    mock_generate_migration_file.assert_called_once_with(
        entity_name, expected_sql_statements, expected_migration_name
    )


@patch("inspira.migrations.utils.generate_migration_file")
@patch("inspira.migrations.utils.generate_column_sql")
def test_generate_rename_column_sql(
    mock_generate_column_sql, mock_generate_migration_file
):
    entity_name = "customers"
    existing_columns = ["email_dc", "name"]
    new_columns = [Column("email", String(255)), Column("name", String(50))]

    expected_sql_statements = "ALTER TABLE customers RENAME COLUMN email_dc TO email;"
    expected_migration_name = "rename_column_email_dc_to_email"

    mock_generate_column_sql.side_effect = lambda col: f"{col.key} VARCHAR(50)"
    generate_rename_column_sql(entity_name, existing_columns, new_columns)

    mock_generate_migration_file.assert_called_once_with(
        entity_name, expected_sql_statements, expected_migration_name
    )


def test_get_migration_files(create_migration_files):
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

    mock_join.assert_any_call(SRC_DIRECTORY, entity_name.replace(".", "/" + entity_name))
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


def test_get_existing_indexes(setup_test_environment, teardown_src_directory,add_index_users):
    execute_sql_file(add_index_users)
    indexes = get_existing_indexes("users")

    assert len(indexes) == 1
    assert "ix_users_name" in indexes


def test_get_all_module_names_with_migration_folder(setup_test_environment, teardown_src_directory):
    expected_module_names = ["module1", "module2", "module3"]

    module_names = get_all_module_names()

    assert set(module_names) == set(expected_module_names)


def test_get_all_module_names_without_migrations(setup_test_environment, teardown_src_directory):
    module3_migrations_dir = os.path.join(
        setup_test_environment, "module3", "migrations"
    )
    os.rmdir(module3_migrations_dir)

    expected_module_names = ["module1", "module2"]
    module_names = get_all_module_names()

    assert set(module_names) == set(expected_module_names)
