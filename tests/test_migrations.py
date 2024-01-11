import os
from textwrap import dedent
from unittest.mock import patch, MagicMock


from inspira.migrations.utils import (
    get_or_create_migration_directory,
    generate_drop_column_sql,
    generate_add_column_sql,
    generate_create_table_sql,
    get_migration_files,
)


def test_get_or_create_migration_directory(teardown_src_directory):
    controller_name = "test_controller"
    result = get_or_create_migration_directory(controller_name)
    expected_directory = os.path.join("src", controller_name, "migrations")
    assert result == expected_directory
    assert os.path.exists(result)
    assert os.path.isdir(result)
    assert os.path.exists(os.path.join(result, "__init__.py"))


def test_generate_drop_column_sql():
    entity_name = "your_entity"
    existing_columns = ["column1", "column2", "column3"]
    new_columns = ["column1", "column3"]

    with patch(
        "inspira.migrations.utils.generate_migration_file", MagicMock()
    ) as mock_generate_migration_file:
        generate_drop_column_sql(entity_name, existing_columns, new_columns)
        mock_generate_migration_file.assert_called_once_with(
            entity_name,
            "ALTER TABLE your_entity DROP COLUMN column2;",
            "drop_column_column2",
        )


def test_generate_add_column_sql():
    entity_name = "your_entity"
    existing_columns = ["column1", "column2"]
    new_columns = [
        MagicMock(key="column3", type="VARCHAR(255)"),
        MagicMock(key="column4", type="INTEGER"),
    ]

    with patch(
        "inspira.migrations.utils.generate_migration_file", MagicMock()
    ) as mock_generate_migration_file:
        generate_add_column_sql(entity_name, existing_columns, new_columns)
        expected_sql = (
            "ALTER TABLE your_entity ADD COLUMN column3 VARCHAR(255);\n"
            "ALTER TABLE your_entity ADD COLUMN column4 INTEGER;\n"
        )
        mock_generate_migration_file.assert_called_once_with(
            entity_name, expected_sql, "add_column_column3_column4"
        )


def test_generate_create_table_sql():
    module_mock = MagicMock()
    module_mock.__name__ = "YourModel"
    table_name = "your_table"
    columns_mock = [
        MagicMock(key="column1", type="VARCHAR(255)"),
        MagicMock(key="column2", type="INTEGER"),
    ]

    with patch(
        "inspira.migrations.utils.get_columns_from_model", return_value=columns_mock
    ):
        with patch(
            "inspira.migrations.utils.generate_migration_file", MagicMock()
        ) as mock_generate_migration_file:
            generate_create_table_sql(module_mock, table_name)
            expected_sql = dedent(
                """
                            CREATE TABLE IF NOT EXISTS your_table (
                                column1 VARCHAR(255),
                            \tcolumn2 INTEGER
                            );
                        """
            )
            mock_generate_migration_file.assert_called_once_with(
                table_name, expected_sql, "create_table_your_table"
            )


def test_get_migration_files(create_migration_files):
    # Arrange
    migration_files, migration_dir = create_migration_files

    # Act
    with patch("inspira.migrations.utils.os.listdir", return_value=migration_files):
        result = get_migration_files(migration_dir)

    # Assert
    assert result == [
        os.path.join(migration_dir, "0001_test.sql"),
        os.path.join(migration_dir, "0002_another.sql"),
        os.path.join(migration_dir, "003_missing.sql"),
    ]
