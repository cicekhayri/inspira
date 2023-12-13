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
@click.option("--skip-repository", "skip_repository", is_flag=True, required=False)
@click.option("--skip-model", "skip_model", is_flag=True, required=False)
def module(name, skip_repository, skip_model):
    if not name:
        click.echo("Please provide a name for the module")
        return

    if not (skip_model or skip_repository) and not database_file_exists():
        click.echo(
            "Database file doesn't exist. Please generate one before generating modules"
        )
        return

    create_module_files(name, skip_repository, skip_model)
    add_route_to_app(name)


def create_module_files(name, skip_repository, skip_model):
    create_src_directory()
    create_controller_file(name)

    if not skip_model:
        generate_model_file(name)

    if not skip_repository:
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
