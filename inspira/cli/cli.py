import click

from inspira.cli.create_app import generate_project
from inspira.cli.create_controller import create_controller_file
from inspira.cli.generate_database_file import create_database_file

from inspira.migrations.migrations import run_migrations, create_migrations

DATABASE_TYPES = ["postgres", "mysql", "sqlite", "mssql"]


@click.group()
def cli():
    pass


@cli.group()
def new():
    pass


@new.command()
@click.argument("name")
@click.option("--websocket", "is_websocket", is_flag=True, required=False)
def controller(name, is_websocket):
    if not name:
        click.echo("Please provide a name for the module")
        return

    try:
        create_controller_file(name, is_websocket)
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
@click.argument("migration_name", required=True)
def createmigrations(migration_name):
    """
    Create migrations

    :param migration_name: Name of the migration e.g. add_column_name_to_order.\n
    """

    try:
        create_migrations(migration_name)
    except click.UsageError as e:
        click.echo(f"Error: {e}")
        click.echo("Use 'createmigrations --help' for usage information.")


@cli.command()
def migrate():
    """
    Run migrations from the migrations folder.
    """
    try:
        run_migrations()
    except Exception as e:
        click.echo(f"Error: {e}")
        click.echo("Migration failed. Check logs for more details.")


@cli.command()
def init():
    generate_project()
    click.echo("App file created successfully.")


if __name__ == "__main__":
    cli()
