import click

from inspira.cli.create_app import generate_project
from inspira.cli.generate_database_file import create_database_file
from inspira.cli.generate_model_file import database_file_exists
from inspira.cli.utils import handle_creations, handle_migrations, create_module_files


DATABASE_TYPES = ["postgres", "mysql", "sqlite", "mssql"]


@click.group()
def cli():
    pass


@cli.group()
def new():
    pass


@new.command()
@click.argument("name")
@click.option("--only-controller", "only_controller", is_flag=True, required=False)
@click.option("--websocket", "is_websocket", is_flag=True, required=False)
def module(name, only_controller, is_websocket):
    """
    Generate files for a new module.

    This command takes a required argument 'name' for the module name, and two optional flags:

    :param str name: Name of the module.

    Optional Flags:
    :param bool only_controller: If provided, generates only the controller file.

    :param bool is_websocket: If provided, includes WebSocket support in the module.

    Example usage:

    ```\n
    inspira new module orders --only-controller --websocket\n
    ```

    This command will generate files for a module named 'orders' with the specified options.
    """
    if not name:
        click.echo("Please provide a name for the module")
        return

    if not only_controller and not database_file_exists():
        click.echo(
            "Database file doesn't exist. Please generate one before generating modules"
        )
        return
    try:
        create_module_files(name, only_controller, is_websocket)
        return click.echo(f"Module '{name}' created successfully.")
    except FileExistsError:
        click.echo(f"Module '{name}' already exists.")





@new.command()
@click.option("--name", required=True, help="Name of the database.")
@click.option("--type", required=True, help="Database type")
def database(name, type):
    """
    Create a new database file with the given name and type.

    This command takes two required parameters:

    :param str name: Name of the database.

    :param str type: Type of the database.

    Example usage:
    ```
    inspira new database --name my_database --type sqlite
    ```

    This command will create a new database file named 'my_database' of type 'sqlite'.
    """
    create_database_file(name, type)


@cli.command()
@click.argument("module_name", required=False)
@click.option(
    "--empty", nargs=2, type=str, required=False, help="Generate empty migration file."
)
def createmigrations(module_name, empty):
    """
    Create migrations for the specified module(s).

    :param module_name: Name of the module for which migrations should be created.\n
    :param empty: If provided, generate an empty migration file with the specified name.
    """
    try:
        handle_creations(module_name, empty)
    except click.UsageError as e:
        click.echo(f"Error: {e}")
        click.echo("Use 'createmigrations --help' for usage information.")


@cli.command()
@click.argument("module_name", required=False)
def migrate(module_name):
    """
    Run migrations for the specified module(s).

    :param module_name: Name of the module for which migrations should be run.
    """
    try:
        handle_migrations(module_name)
    except Exception as e:
        click.echo(f"Error: {e}")
        click.echo("Migration failed. Check logs for more details.")


@cli.command()
def init():
    generate_project()
    click.echo("App file created successfully.")


if __name__ == "__main__":
    cli()
