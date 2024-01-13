import os

import click

from inspira.cli.create_app import generate_project
from inspira.cli.init_file import create_init_file
from inspira.constants import SRC_DIRECTORY
from inspira.utils import singularize


def create_src_directory():
    app_file_path = "main.py"

    if not os.path.exists(app_file_path):
        generate_project()
    if not os.path.exists(SRC_DIRECTORY):
        os.makedirs(SRC_DIRECTORY)
        create_init_file(SRC_DIRECTORY)


def create_test_directory(controller_directory):
    test_directory = os.path.join(controller_directory, "tests")
    os.makedirs(test_directory)

    create_init_file(test_directory)


def create_controller_file(name, is_websocket):
    controller_directory = os.path.join(SRC_DIRECTORY, name)
    singularize_name = singularize(name.lower())

    os.makedirs(controller_directory)

    create_test_directory(controller_directory)

    controller_template_file = "controller_template.txt"
    create_init_file(controller_directory)

    controller_file = os.path.join(
        controller_directory, f"{singularize_name}_controller.py"
    )

    if is_websocket:
        controller_template_file = "websocket_controller_template.txt"

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", controller_template_file
    )

    with open(template_path, "r") as template_file, open(
        controller_file, "w"
    ) as output_file:
        content = (
            template_file.read()
            .replace("{{controller_name}}", singularize_name.capitalize())
            .replace("{{root_path}}", name.lower())
        )
        output_file.write(content)

    click.echo(f"Module '{singularize_name}' created successfully.")
