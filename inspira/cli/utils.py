from inspira.cli.create_controller import create_src_directory, create_controller_file
from inspira.cli.generate_model_file import generate_model_file
from inspira.cli.generate_repository_file import generate_repository_file
from inspira.cli.generate_service_file import generate_service_file
from inspira.migrations.migrations import create_migrations, run_migrations
from inspira.migrations.utils import get_all_module_names


def handle_creations(module_name, empty):
    """
    Handle migration creations based on the provided arguments.

    :param module_name: Name of the module for which migrations should be created.
    :param empty: If provided, generate an empty migration file with the specified name.
    """

    if empty:
        module_name = empty[0]
        migration_name = empty[1]
    else:
        migration_name = None

    module_names = [module_name] if module_name else get_all_module_names()

    for module_name in module_names:
        create_migrations(module_name, migration_name)


def handle_migrations(module_name):
    """
    Handle migration process based on the provided arguments.

    :param module_name: Name of the module for which migrations should be run.
    """
    module_names = [module_name] if module_name else get_all_module_names()

    for current_module_name in module_names:
        run_migrations(current_module_name)


def create_module_files(name, only_controller, is_websocket):
    create_src_directory()
    create_controller_file(name, is_websocket)

    if not only_controller:
        generate_model_file(name)
        generate_service_file(name)
        generate_repository_file(name)