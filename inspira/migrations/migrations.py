import sys

import click
from sqlalchemy import select, create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.ddl import CreateTable, CreateIndex, DropIndex
from sqlalchemy.sql.expression import func
import os
from sqlalchemy import MetaData, Column, Integer, String, text

from inspira.logging import log
from inspira.migrations.utils import (
    get_or_create_migration_directory,
    get_migration_files,
    load_model_file,
    get_columns_from_model,
    generate_add_column_sql,
    generate_drop_column_sql,
    generate_migration_file_for_create_table,
    generate_rename_column_sql,
    generate_empty_sql_file,
    get_indexes_from_model,
    generate_migration_file,
)

PROJECT_ROOT = os.path.abspath(".")
sys.path.append(PROJECT_ROOT)

try:
    from database import Base, engine, db_session
except ImportError:
    Base = declarative_base()
    engine = create_engine("sqlite:///:memory:")
    db_session = None


class Migration(Base):
    __tablename__ = "migrations"
    id = Column(Integer, primary_key=True)
    migration_name = Column(String(255))
    version = Column(Integer)


def initialize_database(engine):
    Base.metadata.create_all(engine)


def execute_sql_file(file_path):
    with open(file_path, "r") as file:
        sql_content = file.read()

    sql_statements = [
        statement.strip() for statement in sql_content.split(";") if statement.strip()
    ]

    with engine.connect() as connection:
        try:
            for statement in sql_statements:
                connection.execute(text(statement))
            connection.commit()
            log.info("Table creation successful.")
        except SQLAlchemyError as e:
            log.error("Error:", e)
            connection.rollback()
            log.info("Transaction rolled back.")


def generate_create_table_sql(model_name):
    metadata = Base.metadata
    table = metadata.tables[model_name]
    sql = str(CreateTable(table).compile(engine))[:-2] + ";" + "\n"
    index_sqls = [CreateIndex(index).compile(engine) for index in table.indexes]

    for index_sql in index_sqls:
        sql += "\n" + str(index_sql) + ";"

    return sql


def create_migrations(entity_name, empty_migration_file):
    if empty_migration_file:
        generate_empty_sql_file(entity_name, empty_migration_file)

    module = load_model_file(entity_name)

    existing_columns = get_existing_columns(entity_name)
    new_columns = get_columns_from_model(getattr(module, module.__name__))

    if not existing_columns:
        sql_str = generate_create_table_sql(entity_name)
        generate_migration_file_for_create_table(sql_str, entity_name)
    else:
        renamed_columns = [
            (old_col, new_col.key)
            for old_col, new_col in zip(existing_columns, new_columns)
            if old_col != new_col.key
        ]
        if renamed_columns:
            generate_rename_column_sql(entity_name, existing_columns, new_columns)
        else:
            added_columns = [
                col for col in new_columns if col.key not in existing_columns
            ]
            if added_columns:
                generate_add_column_sql(entity_name, existing_columns, added_columns)
            else:
                removed_columns = [
                    col for col in existing_columns if col not in new_columns
                ]
                if removed_columns:
                    generate_drop_column_sql(entity_name, existing_columns, new_columns)

        existing_indexes = get_existing_indexes(entity_name)
        new_indexes = get_indexes_from_model(getattr(module, module.__name__))
        generate_add_index_sql(entity_name, existing_indexes, new_indexes)
        generate_drop_index_sql(entity_name, existing_indexes, new_indexes)


def run_migrations(module_name):
    with engine.connect() as connection:
        if not engine.dialect.has_table(connection, "migrations"):
            initialize_database(engine)

        if not engine.dialect.has_table(connection, module_name):
            initialize_database(engine)

        migration_dir = get_or_create_migration_directory(module_name)
        migration_files = get_migration_files(migration_dir)

        for file in migration_files:
            migration_name = os.path.basename(file).replace(".sql", "")

            current_version = (
                connection.execute(
                    select(func.max(Migration.version)).where(
                        Migration.migration_name == migration_name
                    )
                ).scalar()
                or 0
            )

            if not current_version:
                execute_sql_file(file)
                click.echo(
                    f"Applying migration for {migration_name} version {current_version}"
                )

                insert_migration(current_version, migration_name)


def get_existing_columns(table_name):
    metadata = MetaData()
    metadata.reflect(bind=engine)

    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        return [column.name for column in table.columns]
    else:
        return None


def insert_migration(current_version, migration_name):
    migration = Migration()
    migration.version = current_version + 1
    migration.migration_name = migration_name
    db_session.add(migration)
    db_session.commit()


def get_existing_indexes(table_name):
    inspector = inspect(engine)
    indexes = inspector.get_indexes(table_name)
    return [index["name"] for index in indexes]


def generate_add_index_sql(entity_name, existing_indexes, new_indexes):
    for new_index in new_indexes:
        if new_index.name not in existing_indexes:
            index_sql = str(CreateIndex(new_index).compile(engine))

            migration_file_name = f"add_index_{new_index.name}"
            generate_migration_file(entity_name, index_sql, migration_file_name)


def generate_drop_index_sql(entity_name, existing_indexes, new_indexes):
    new_index_names = set(index.name for index in new_indexes)

    for removed_index_name in set(existing_indexes) - new_index_names:
        drop_index_sql = str(DropIndex(removed_index_name).compile(engine))
        migration_file_name = f"drop_index_{removed_index_name}"
        generate_migration_file(entity_name, drop_index_sql, migration_file_name)
