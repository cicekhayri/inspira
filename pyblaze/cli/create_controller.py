import os

import click

from pyblaze.cli.create_app import generate_project
from pyblaze.utils import singularize


def create_src_directory():
    src_directory = "src"
    app_file_path = "app.py"

    if not os.path.exists(app_file_path):
        generate_project()
    if not os.path.exists(src_directory):
        os.makedirs(src_directory)


def create_controller_file(name):
    src_directory = "src"
    resource_directory = os.path.join(src_directory, name)
    singularize_name = singularize(name.lower())
    # Create the resource directory
    os.makedirs(resource_directory)

    # Create __init__.py in the resource directory
    init_file = os.path.join(resource_directory, "__init__.py")

    with open(init_file, "w"):
        pass

    # Create the controller file
    controller_file = os.path.join(
        resource_directory, f"{singularize_name}_controller.py"
    )
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "controller_template.txt"
    )

    with open(template_path, "r") as template_file, open(
        controller_file, "w"
    ) as output_file:
        content = template_file.read().replace(
            "{{controller_name}}", singularize_name.capitalize()
        )
        output_file.write(content)

    click.echo(f"Controller '{singularize_name}' created successfully.")
    