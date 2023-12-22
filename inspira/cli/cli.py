import click

from inspira.cli.create_app import generate_project
from inspira.cli.create_controller import create_controller_file, create_src_directory
from inspira.cli.generate_database_file import create_database_file
from inspira.cli.generate_model_file import database_file_exists, generate_model_file
from inspira.cli.generate_repository_file import generate_repository_file
from inspira.cli.generate_service_file import generate_service_file

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
    if not name:
        click.echo("Please provide a name for the module")
        return

    if not only_controller and not database_file_exists():
        click.echo(
            "Database file doesn't exist. Please generate one before generating modules"
        )
        return

    create_module_files(name, only_controller, is_websocket)


def create_module_files(name, only_controller, is_websocket):
    create_src_directory()
    create_controller_file(name, is_websocket)

    if not only_controller:
        generate_model_file(name)
        generate_service_file(name)
        generate_repository_file(name)


@new.command()
@click.option("--name", required=True, help="Name of the database.")
@click.option("--type", required=True, help="Database type")
def database(name, type):
    create_database_file(name, type)


@cli.command()
def init():
    generate_project()
    click.echo("App file created successfully.")


if __name__ == "__main__":
    cli()
