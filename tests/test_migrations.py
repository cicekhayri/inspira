import os
from unittest.mock import patch, MagicMock

from sqlalchemy import Index, MetaData, Table, Column, Integer, String

from inspira.migrations.utils import (
    get_or_create_migration_directory,
    generate_drop_column_sql,
    generate_add_column_sql,
    generate_create_table_sql,
    get_migration_files,
    generate_rename_column_sql, generate_add_index_sql,
)


def test_get_or_create_migration_directory(teardown_src_directory):
    controller_name = "test_controller"
    result = get_or_create_migration_directory(controller_name)
    expected_directory = os.path.join("src", controller_name, "migrations")
    assert result == expected_directory
    assert os.path.exists(result)
    assert os.path.isdir(result)
    assert os.path.exists(os.path.join(result, "__init__.py"))


@patch('inspira.migrations.utils.generate_migration_file')
@patch('inspira.migrations.utils.generate_column_sql')
def test_generate_drop_column_sql(mock_generate_column_sql, mock_generate_migration_file):
    entity_name = "customers"
    existing_columns = ["email_dc"]
    new_columns = [
        Column('email_dc', String(255)),
        Column('name', String(50))
    ]

    expected_sql_statements = "ALTER TABLE customers DROP COLUMN email_dc;"
    expected_migration_name = "drop_column_email_dc_"

    mock_generate_column_sql.side_effect = lambda col: f"{col.key} VARCHAR(50)"
    generate_drop_column_sql(entity_name, existing_columns, new_columns)

    mock_generate_migration_file.assert_called_once_with(
        entity_name, expected_sql_statements, expected_migration_name
    )


@patch('inspira.migrations.utils.generate_migration_file')
@patch('inspira.migrations.utils.generate_column_sql')
def test_generate_add_column_sql(mock_generate_column_sql, mock_generate_migration_file):
    entity_name = "customers"
    existing_columns = ["email_dc"]
    new_columns = [
        Column('email_dc', String(255)),
        Column('name', String(50))
    ]

    expected_sql_statements = "ALTER TABLE customers ADD COLUMN name VARCHAR(50);\n"
    expected_migration_name = "add_column_name"

    mock_generate_column_sql.side_effect = lambda col: f"{col.key} VARCHAR(50)"
    generate_add_column_sql(entity_name, existing_columns, new_columns)

    mock_generate_migration_file.assert_called_once_with(
        entity_name, expected_sql_statements, expected_migration_name
    )



@patch('inspira.migrations.utils.generate_migration_file')
@patch('inspira.migrations.utils.generate_column_sql')
def test_generate_rename_column_sql(mock_generate_column_sql, mock_generate_migration_file):
    entity_name = "customers"
    existing_columns = ["email_dc", "name"]
    new_columns = [
        Column('email', String(255)),
        Column('name', String(50))
    ]

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


@patch('inspira.migrations.utils.generate_migration_file')
def test_generate_add_index_sql(mock_generate_migration_file):
    entity_name = "customers"
    existing_indexes = ["ix_customers_email_dc"]

    metadata = MetaData()
    customers = Table(
        'customers', metadata,
        Column('email_dc', Integer),
        Column('name', Integer)
    )

    new_indices = [
        Index('ix_customers_email_dc', customers.c.email_dc),
        Index('ix_customers_name', customers.c.name)
    ]

    generate_add_index_sql(entity_name, existing_indexes, new_indices)

    mock_generate_migration_file.assert_called_once_with(
        entity_name, "CREATE INDEX ix_customers_name ON customers (name);", "add_index_ix_customers_name"
    )


@patch('inspira.migrations.utils.generate_migration_file')
@patch('inspira.migrations.utils.generate_index_sql', return_value="")
@patch('inspira.migrations.utils.generate_column_sql')
@patch('inspira.migrations.utils.get_columns_from_model')
def test_generate_create_table_sql(mock_get_columns_from_model, mock_generate_column_sql, mock_generate_index_sql, mock_generate_migration_file):
    table_name = "customers"
    columns_mock = [
        Column('email_dc', String(255)),
        Column('name', String(50))
    ]

    mock_get_columns_from_model.return_value = columns_mock

    mock_generate_column_sql.side_effect = lambda col: f"{col.key} VARCHAR(50)"

    module_mock = MagicMock(__name__="YourModel")

    generate_create_table_sql(module_mock, table_name)

    expected_sql = "CREATE TABLE IF NOT EXISTS customers (\n    email_dc VARCHAR(50),\n\tname VARCHAR(50)\n);\n\n\n\n"
    expected_migration_name = "create_table_customers"

    mock_generate_migration_file.assert_called_once_with(
        table_name, expected_sql, expected_migration_name
    )