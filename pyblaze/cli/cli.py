import click

from pyblaze.cli.create_app import add_route_to_app, generate_project
from pyblaze.cli.create_controller import create_controller_file, create_src_directory
from pyblaze.cli.generate_database_file import create_database_file
from pyblaze.cli.generate_model_file import database_file_exists, generate_model_file
from pyblaze.cli.generate_repository_file import generate_repository_file

DATABASE_TYPES = ["postgres", "mysql", "sqlite", "mssql"]


@click.group()
def cli():
    pass


@cli.group()
def new():
    pass


@new.command()
@click.argument("name")
def module(name):
    if not name:
        click.echo("Please provide a name for the module")
        return
    if not database_file_exists():
        click.echo(
            "Database file doesn't exists, please generate one before generating modules"
        )
        return

    create_src_directory()
    create_controller_file(name)
    generate_model_file(name)
    generate_repository_file(name)
    add_route_to_app(name)


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
