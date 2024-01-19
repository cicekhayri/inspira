import os
import click

from inspira.constants import SRC_DIRECTORY
from inspira.utils import pluralize_word, singularize


def generate_service_file(module_name):
    model_directory = os.path.join(SRC_DIRECTORY, "service")
    service_file_name = f"{singularize(module_name.lower())}_service.py"

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "service_template.txt"
    )
    service_file_path = os.path.join(model_directory, service_file_name)

    if os.path.exists(service_file_path):
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
