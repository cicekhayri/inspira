import os
import re

import click

from inspira.constants import SRC_DIRECTORY
from inspira.utils import pluralize_word, singularize


def generate_service_file(module_name):
    model_directory = os.path.join(SRC_DIRECTORY, "service")
    service_file_name = f"{singularize(module_name.lower())}_service.py"

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "service_template.txt"
    )
    service_file_path = os.path.join(
        model_directory, service_file_name
    )

    if service_file_path:
        click.echo(f"Service '{service_file_name}' already exists.")
        return

    with open(template_path, "r") as template_file, open(
        service_file_path, "w"
    ) as output_file:
        content = (
            template_file.read()
            .replace("{{model_name}}", pluralize_word(module_name))
            .replace("{{model_name_upper}}", singularize(module_name.capitalize()))
            .replace("{{module_name}}", module_name)
            .replace("{{model_name_singular}}", singularize(module_name.lower()))
        )
        output_file.write(content)

    click.echo(f"Service '{service_file_name}' created successfully.")
    # add_service_dependency_to_controller(module_name)


def add_service_dependency_to_controller(module_name):
    controller_file_path = os.path.join(
        SRC_DIRECTORY,
        module_name.lower(),
        f"{singularize(module_name.lower())}_controller.py",
    )
    module_name_capitalized = singularize(module_name.lower()).capitalize()
    singularized_module_name = singularize(module_name.lower())

    with open(controller_file_path, "r") as controller_file:
        existing_content = controller_file.read()

    # Define the __init__ method
    init_method = f"""\n
    def __init__(self, {singularized_module_name}_service: {module_name_capitalized}Service):
        self._{singularized_module_name}_service = {singularized_module_name}_service"""

    import_statement = (
        f""
        f"\n\nfrom src.{module_name.lower()}.{singularize(module_name.lower())}_service"
        f" import {module_name_capitalized}Service\n\n\n"
    )

    # Update the regular expression to match @path or @websocket
    class_pattern = re.compile(
        r"@(path|websocket)\(.+\)\nclass\s+[A-Za-z_][A-Za-z0-9_]*:"
    )
    match = class_pattern.search(existing_content)

    if match:
        start, end = match.span()
        updated_content = (
            existing_content[:start].rstrip()
            + import_statement
            + existing_content[start:end]
            + init_method
            + existing_content[end:]
        )

        with open(controller_file_path, "w") as controller_file:
            controller_file.write(updated_content)
