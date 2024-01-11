import sys

import click
from sqlalchemy import select, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql.expression import func
import os
from sqlalchemy import MetaData, Column, Integer, String, text


from inspira.migrations.utils import get_or_create_migration_directory, \
    get_migration_files, load_model_file, get_columns_from_model, generate_add_column_sql, generate_drop_column_sql, \
    generate_create_table_sql

PROJECT_ROOT = os.path.abspath(".")
sys.path.append(PROJECT_ROOT)

try:
    from database import Base, engine, db_session
except ImportError:
    Base = declarative_base()
    engine = create_engine('sqlite:///:memory:')
    db_session = None

class Migration(Base):
    __tablename__ = "migrations"
    id = Column(Integer, primary_key=True)
    migration_name = Column(String(255))
    version = Column(Integer)


def initialize_database(engine):
    Base.metadata.create_all(engine)


def execute_sql_file(file_path):
    with open(file_path, 'r') as file:
        sql_content = file.read()

    sql_statements = sql_content.split(';')

    with engine.connect() as connection:
        for statement in sql_statements:
            if statement.strip():
                connection.execute(text(statement))

def create_migrations(entity_name):
    module = load_model_file(entity_name)

    existing_columns = get_existing_columns(entity_name)
    if existing_columns:
        new_columns = get_columns_from_model(getattr(module, module.__name__))

        generate_add_column_sql(entity_name, existing_columns, new_columns)

        generate_drop_column_sql(entity_name, existing_columns, new_columns)
    else:
        generate_create_table_sql(module, entity_name)

def run_migrations(module_name):
    with engine.connect() as connection:
        if not engine.dialect.has_table(connection, 'migrations'):
            initialize_database(engine)

        if not engine.dialect.has_table(connection, module_name):
            initialize_database(engine)

        migration_dir = get_or_create_migration_directory(module_name)
        migration_files = get_migration_files(migration_dir)

        for file in migration_files:
            migration_name = os.path.basename(file).replace(".sql", "")

            current_version = connection.execute(
                select(func.max(Migration.version))
                .where(Migration.migration_name == migration_name)
            ).scalar() or 0

            if not current_version:
                execute_sql_file(file)
                click.echo(f"Applying migration for {migration_name} version {current_version}")

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
