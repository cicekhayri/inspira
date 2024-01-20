import os

from inspira.cli.create_controller import create_init_file
from inspira.constants import MIGRATION_DIRECTORY
from inspira.logging import log


def get_or_create_migration_directory():
    migration_directory = os.path.join(MIGRATION_DIRECTORY)

    os.makedirs(migration_directory, exist_ok=True)

    create_init_file(migration_directory)

    return migration_directory


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
        migration_file.write(f"-- Up\n")
        migration_file.write("\n")
        migration_file.write("\n-- Down\n")

    log.info(
        f"Migration file '{str(new_migration_number).zfill(4)}_{migration_name}.sql' created."
    )
    return migration_file
