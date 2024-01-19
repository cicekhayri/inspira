import os

import click

from inspira.cli.create_app import generate_project
from inspira.cli.init_file import create_init_file
from inspira.constants import SRC_DIRECTORY
from inspira.utils import singularize, pluralize_word


def create_src_directory():
    app_file_path = "main.py"

    if not os.path.exists(app_file_path):
        generate_project()
    if not os.path.exists(SRC_DIRECTORY):
        os.makedirs(SRC_DIRECTORY)
        create_init_file(SRC_DIRECTORY)


def create_controller_file(name, is_websocket):
    controller_directory = os.path.join(SRC_DIRECTORY, "controller")
    singularize_name = singularize(name.lower())
    controller_file_name = f"{singularize_name}_controller.py"
    controller_template_file = "controller_template.txt"

    controller_file_path = os.path.join(controller_directory, controller_file_name)

    if os.path.exists(controller_file_path):
        click.echo(f"Controller '{controller_file_name}' already exists.")
        return

    if is_websocket:
        controller_template_file = "websocket_controller_template.txt"

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", controller_template_file
    )

    with open(template_path, "r") as template_file, open(
        controller_file_path, "w"
    ) as output_file:
        content = (
            template_file.read()
            .replace("{{controller_name}}", singularize_name.capitalize())
            .replace("{{root_path}}", pluralize_word(name.lower()))
        )
        output_file.write(content)

    click.echo(f"Controller '{singularize_name}' created successfully.")
