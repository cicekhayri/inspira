import importlib
import os

from sqlalchemy import Integer, String

from inspira.cli.create_controller import create_init_file
from inspira.constants import SRC_DIRECTORY, MIGRATION_DIRECTORY
from inspira.logging import log
from inspira.utils import singularize


def get_or_create_migration_directory():
    migration_directory = os.path.join(MIGRATION_DIRECTORY)

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


def migration_file_exist(migration_file_name: str) -> bool:
    migration_dir = get_or_create_migration_directory()
    migration_files = get_migration_files(migration_dir)

    migration_exists = any(
        migration_file_name in migration for migration in migration_files
    )
    if migration_exists:
        log.info(f"Migration {migration_file_name} already exists. Skipping...")

    return migration_exists


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


def generate_migration_file(migration_name):
    migration_dir = get_or_create_migration_directory()
    latest_migration_number = get_latest_migration_number(migration_dir)
    new_migration_number = latest_migration_number + 1
    migration_file_path = os.path.join(
        migration_dir, f"{str(new_migration_number).zfill(4)}_{migration_name}.sql"
    )

    with open(migration_file_path, "w") as migration_file:
        pass

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
