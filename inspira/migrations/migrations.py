import os
import sys

import click
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    create_engine,
    inspect,
    select,
    text,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker
from sqlalchemy.sql.expression import func

from inspira.constants import MIGRATION_DIRECTORY
from inspira.logging import log
from inspira.migrations.utils import (
    generate_migration_file,
    get_migration_files,
    get_or_create_migration_directory,
    migration_file_exist,
)

PROJECT_ROOT = os.path.abspath(".")
sys.path.append(PROJECT_ROOT)

try:
    from database import Base, db_session, engine
except ImportError:
    Base = declarative_base()
    engine = create_engine("sqlite:///:memory:")
    db_session = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )


class Migration(Base):
    __tablename__ = MIGRATION_DIRECTORY
    id = Column(Integer, primary_key=True)
    migration_name = Column(String(255))
    version = Column(Integer)


def initialize_database(engine):
    Base.metadata.create_all(engine)


def create_migrations(migration_name):
    if migration_file_exist(migration_name):
        return

    generate_migration_file(migration_name)


def run_migrations(down=False):
    with engine.connect() as connection:
        if not engine.dialect.has_table(connection, MIGRATION_DIRECTORY):
            initialize_database(engine)

        migration_dir = get_or_create_migration_directory()
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

            if not current_version and not down:
                execute_up_migration(connection, file, migration_name)

                insert_migration(current_version, migration_name)
                continue

            if down:
                execute_down_migration(connection, file, migration_name)
                remove_migration(migration_name)


def execute_up_migration(connection, file, migration_name):
    with open(file, "r") as migration_file:
        sql = migration_file.read()

        up_sql_start = sql.find("-- Up")
        if up_sql_start != -1:
            up_sql_start += len("-- Up")
            up_sql_end = sql.find("-- Down") if "-- Down" in sql else None
            up_sql = sql[up_sql_start:up_sql_end].strip()

            execute_sql_file_contents(connection, up_sql)

            click.echo(f"Applying 'Up' migration for {migration_name}")
        else:
            click.echo(f"No 'Up' migration found in {migration_name}")


def execute_down_migration(connection, file, migration_name):
    with open(file, "r") as migration_file:
        sql = migration_file.read()

        down_sql_start = sql.find("-- Down")
        if down_sql_start != -1:
            down_sql_start += len("-- Down")
            down_sql_end = sql.find("-- End Down") if "-- End Down" in sql else None
            down_sql = sql[down_sql_start:down_sql_end].strip()

            execute_sql_file_contents(connection, down_sql)

            click.echo(f"Applying 'Down' migration for {migration_name}")
        else:
            click.echo(f"No 'Down' migration found in {migration_name}")


def execute_sql_file_contents(connection, sql_content):
    sql_statements = [
        statement.strip() for statement in sql_content.split(";") if statement.strip()
    ]

    try:
        for statement in sql_statements:
            connection.execute(text(statement))
        connection.commit()
        log.info("Migration run successfully.")
    except SQLAlchemyError as e:
        log.error("Error:", e)
        connection.rollback()
        log.info("Transaction rolled back.")


def insert_migration(current_version, migration_name):
    migration = Migration()
    migration.version = current_version + 1
    migration.migration_name = migration_name
    db_session.add(migration)
    db_session.commit()


def remove_migration(migration_name):
    migration = (
        db_session.query(Migration).filter_by(migration_name=migration_name).first()
    )

    if migration:
        try:
            db_session.delete(migration)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            log.error(f"Error deleting migration {migration_name}: {e}")
    else:
        log.error(f"Migration {migration_name} not found.")
