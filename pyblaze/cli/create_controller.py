import os

import click

from pyblaze.cli.create_app import generate_project
from pyblaze.utils import pluralize_word, singularize


def create_src_directory():
    src_directory = "src"
    app_file_path = "app.py"

    if not os.path.exists(app_file_path):
        generate_project()
    if not os.path.exists(src_directory):
        os.makedirs(src_directory)


def create_controller_file(name):
    src_directory = "src"
    controller_directory = os.path.join(src_directory, name)
    singularize_name = singularize(name.lower())
    # Create the resource directory
    os.makedirs(controller_directory)

    # Create __init__.py in the resource directory
    init_file = os.path.join(controller_directory, "__init__.py")

    with open(init_file, "w"):
        pass

    # Create the controller file
    controller_file = os.path.join(
        controller_directory, f"{singularize_name}_controller.py"
    )
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "controller_template.txt"
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
