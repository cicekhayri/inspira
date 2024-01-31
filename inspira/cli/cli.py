import click

from inspira.cli.create_app import generate_project
from inspira.cli.create_controller import create_controller_file
from inspira.cli.generate_database_file import create_database_file
from inspira.cli.generate_model_file import generate_model_file
from inspira.cli.generate_repository_file import generate_repository_file
from inspira.cli.generate_service_file import generate_service_file
from inspira.migrations.migrations import create_migrations, run_migrations

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
        click.echo("Please provide a name for the controller")
        return

    try:
        create_controller_file(name, is_websocket)
    except FileExistsError:
        click.echo(f"Controller '{name}' already exists.")


@new.command()
@click.argument("name")
def repository(name):
    if not name:
        click.echo("Please provide a name of the repository")
        return

    try:
        generate_repository_file(name)
    except FileExistsError:
        click.echo(f"Repository '{name}' already exists.")


@new.command()
@click.argument("name")
def service(name):
    if not name:
        click.echo("Please provide a name of the service")
        return

    try:
        generate_service_file(name)
    except FileExistsError:
        click.echo(f"Service '{name}' already exists.")


@new.command()
@click.argument("name")
def model(name):
    if not name:
        click.echo("Please provide a name for the model.")
        return

    try:
        generate_model_file(name)
    except FileExistsError:
        click.echo(f"Model '{name}' already exists.")


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


@new.command()
@click.argument("migration_name", required=True)
def migration(migration_name):
    """
    Create migration

    :param migration_name: Name of the migration e.g. add_column_name_to_order.\n
    """

    try:
        create_migrations(migration_name)
    except click.UsageError as e:
        click.echo(f"Error: {e}")
        click.echo("Use 'migration --help' for usage information.")


@cli.command()
@click.option("--down", is_flag=True, help="Run Down migrations.")
def migrate(down):
    """
    Run migrations from the migrations folder.
    """
    try:
        run_migrations(down=down)
    except Exception as e:
        click.echo(f"Error: {e}")
        click.echo("Migration failed. Check logs for more details.")


@cli.command()
@click.option("--only-controller",  "only_controller", is_flag=True, required=False, help="Generates only controller module")
def init(only_controller):
    generate_project(only_controller)
    click.echo("App file created successfully.")


if __name__ == "__main__":
    cli()
