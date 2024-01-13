import importlib
import os

from sqlalchemy import String, Integer

from inspira.cli.create_controller import create_init_file
from inspira.constants import SRC_DIRECTORY
from inspira.logging import log
from inspira.utils import singularize


def get_or_create_migration_directory(name: str):
    controller_directory = os.path.join(SRC_DIRECTORY, name)
    migration_directory = os.path.join(controller_directory, "migrations")

    if not os.path.exists(controller_directory):
        log.error(f"Module '{name}' doesn't exists.")
        return

    os.makedirs(migration_directory, exist_ok=True)

    create_init_file(migration_directory)

    return migration_directory


def load_model_file(entity_name):
    module_path = os.path.join(
        SRC_DIRECTORY, entity_name.replace(".", "/" + entity_name)
    )
    model_file_path = os.path.join(module_path, f"{singularize(entity_name)}.py")
    model_name = singularize(entity_name).capitalize()
    spec = importlib.util.spec_from_file_location(model_name, model_file_path)
    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except FileNotFoundError:
        return None

    return module


def generate_drop_column_sql(table_name, existing_columns, new_columns):
    sql_statements = ""
    migration_name = ""

    for i, col in enumerate(existing_columns):
        if col not in new_columns:
            add_underscore = "_" if i < len(new_columns) - 1 else ""
            sql_statements += f"ALTER TABLE {table_name} DROP COLUMN {col};\n"
            migration_name += col + add_underscore

    if sql_statements:
        migration_file_name = f"drop_column_{migration_name}"
        if migration_file_exist(table_name, migration_file_name):
            return

        generate_migration_file(table_name, sql_statements, migration_file_name)


def generate_add_column_sql(table_name, existing_columns, new_columns):
    sql_statements = ""
    migration_name = ""
    for i, col in enumerate(new_columns):
        if col.key not in existing_columns:
            add_underscore = "_" if i < len(new_columns) - 1 else ""
            sql_statements += f"ALTER TABLE {table_name} ADD COLUMN {generate_column_sql(col).strip()};\n"
            migration_name += col.key + add_underscore

    if sql_statements:
        migration_file_name = f"add_column_{migration_name}"
        if migration_file_exist(table_name, migration_file_name):
            return
        generate_migration_file(table_name, sql_statements, migration_file_name)


def generate_rename_column_sql(table_name, existing_columns, new_columns):
    sql_statements = ""
    migration_name = ""

    for i, (old_col, new_col) in enumerate(zip(existing_columns, new_columns)):
        if old_col != new_col.key:
            add_underscore = "_" if i > 0 else ""
            sql_statements += (
                f"ALTER TABLE {table_name} RENAME COLUMN {old_col} TO {new_col.key};"
            )
            migration_name += f"{old_col}_to_{new_col.key}{add_underscore}"

    if sql_statements:
        migration_file_name = f"rename_column_{migration_name}"
        if migration_file_exist(table_name, migration_file_name):
            return

        generate_migration_file(table_name, sql_statements, migration_file_name)


def generate_migration_file_for_create_table(sql_str, table_name):
    migration_file_name = f"create_table_{table_name}"

    if migration_file_exist(table_name, migration_file_name):
        return

    generate_migration_file(table_name, sql_str, migration_file_name)


def migration_file_exist(table_name: str, migration_file_name: str) -> bool:
    migration_dir = get_or_create_migration_directory(table_name)
    migration_files = get_migration_files(migration_dir)

    migration_exists = any(
        migration_file_name in migration for migration in migration_files
    )
    if migration_exists:
        log.info(f"Migration {migration_file_name} already exists. Skipping...")

    return migration_exists


def generate_empty_sql_file(module, migration_name):
    generate_migration_file(module, "", migration_name)


def get_migration_files(migration_dir):
    migration_files = [
        os.path.join(migration_dir, f)
        for f in os.listdir(migration_dir)
        if f.endswith(".sql")
        and f.split("_")[0].isdigit()
        and os.path.isfile(os.path.join(migration_dir, f))
    ]
    migration_files.sort()
    return migration_files


def get_latest_migration_number(migration_dir):
    migration_files = [f for f in os.listdir(migration_dir) if f.endswith(".sql")]
    if not migration_files:
        return 0

    latest_migration = max(int(f.split("_")[0]) for f in migration_files)
    return latest_migration


def generate_migration_file(module_name, migration_sql, migration_name):
    migration_dir = get_or_create_migration_directory(module_name)
    latest_migration_number = get_latest_migration_number(migration_dir)
    new_migration_number = latest_migration_number + 1
    migration_file_path = os.path.join(
        migration_dir, f"{str(new_migration_number).zfill(4)}_{migration_name}.sql"
    )

    with open(migration_file_path, "w") as migration_file:
        migration_file.write(migration_sql)

    log.info(
        f"Migration file '{str(new_migration_number).zfill(4)}_{migration_name}.sql' created."
    )
    return migration_file


def generate_column_sql(column):
    column_name = column.key
    constraints = []

    if isinstance(column.type, String):
        column_type = f"VARCHAR({column.type.length})"
    elif isinstance(column.type, Integer):
        column_type = "INTEGER"
    else:
        column_type = str(column.type)

    if column.primary_key:
        column_type += " PRIMARY KEY"

    if column.nullable:
        column_type += " NULL"
    else:
        column_type += " NOT NULL"

    if column.unique:
        constraints.append("UNIQUE")

    return f"{column_name} {column_type} {''.join(constraints)}"


def get_columns_from_model(model_class):
    return model_class.__table__.columns


def get_indexes_from_model(model_class):
    return model_class.__table__.indexes


def get_all_module_names():
    module_names = []

    for dir_entry in os.listdir(SRC_DIRECTORY):
        full_path = os.path.join(SRC_DIRECTORY, dir_entry)
        if os.path.isdir(full_path):
            migrations_dir = os.path.join(full_path, "migrations")
            if os.path.exists(migrations_dir):
                module_names.append(dir_entry)

    return module_names
