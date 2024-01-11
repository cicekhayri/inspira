import importlib
import os

from inspira.cli.create_controller import create_init_file
from inspira.logging import log
from inspira.utils import singularize


def get_or_create_migration_directory(name: str):
    src_directory = "src"
    controller_directory = os.path.join(src_directory, name)
    migration_directory = os.path.join(controller_directory, "migrations")
    os.makedirs(migration_directory, exist_ok=True)

    create_init_file(migration_directory)

    return migration_directory


def load_model_file(entity_name):
    module_path = os.path.join("src", entity_name.replace(".", "/" + entity_name))
    model_file_path = os.path.join(module_path, f"{singularize(entity_name)}.py")
    model_name = singularize(entity_name).capitalize()
    spec = importlib.util.spec_from_file_location(model_name, model_file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def generate_drop_column_sql(entity_name, existing_columns, new_columns):
    sql_statements = ""
    migration_name = ""

    for i, col in enumerate(existing_columns):
        if col not in new_columns:
            add_underscore = "_" if i < len(new_columns) - 1 else ""
            sql_statements += f"ALTER TABLE {entity_name} DROP COLUMN {col};"
            migration_name += col + add_underscore

    if sql_statements:
        migration_file_name = f"drop_column_{migration_name}"
        generate_migration_file(entity_name, sql_statements, migration_file_name)


def generate_add_column_sql(entity_name, existing_columns, new_columns):
    sql_statements = ""
    migration_name = ""
    for i, col in enumerate(new_columns):
        if col.key not in existing_columns:
            add_underscore = "_" if i < len(new_columns) - 1 else ""
            sql_statements += f"ALTER TABLE {entity_name} ADD COLUMN {generate_column_sql(col).strip()};\n"
            migration_name += col.key + add_underscore

    if sql_statements:
        migration_file_name = f"add_column_{migration_name}"
        generate_migration_file(entity_name, sql_statements, migration_file_name)


def generate_rename_column_sql(entity_name, existing_columns, new_columns):
    sql_statements = ""
    migration_name = ""

    for i, (old_col, new_col) in enumerate(zip(existing_columns, new_columns)):
        if old_col != new_col.key:
            add_underscore = "_" if i < len(new_columns) - 1 else ""
            sql_statements += f"ALTER TABLE {entity_name} RENAME COLUMN {old_col} TO {new_col.key};"
            migration_name += f"{old_col}_to_{new_col.key}{add_underscore}"

    if sql_statements:
        migration_file_name = f"rename_column_{migration_name}"
        generate_migration_file(entity_name, sql_statements, migration_file_name)


def generate_create_table_sql(module, table_name):
    backslash = "\n\t"
    columns = get_columns_from_model(getattr(module, module.__name__))

    create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    {f',{backslash}'.join(generate_column_sql(col) for col in columns)}
);
"""
    migration_file_name = f"create_table_{table_name}"
    generate_migration_file(table_name, create_table_sql, migration_file_name)


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
    return f"{column.key} {column.type}"


def get_columns_from_model(model_class):
    return model_class.__table__.columns
