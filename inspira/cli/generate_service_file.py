import os

import click
from jinja2 import Template

from inspira.constants import SRC_DIRECTORY
from inspira.utils import singularize


def generate_service_file(module_name):
    service_directory = os.path.join(SRC_DIRECTORY, "service")
    service_file_name = f"{singularize(module_name.lower())}_service.py"

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "service_template.jinja2"
    )
    service_file_path = os.path.join(service_directory, service_file_name)

    if os.path.exists(service_file_path):
        click.echo(f"Service '{service_file_name}' already exists.")
        return

    with open(template_path, "r") as template_file, open(
        service_file_path, "w"
    ) as output_file:
        template_content = template_file.read()
        template = Template(template_content)

        context = {
            "model_name_upper": singularize(module_name.capitalize()),
        }

        content = template.render(context)
        output_file.write(content)

    click.echo(f"Service '{service_file_name}' created successfully.")
