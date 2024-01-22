import os

import click
from jinja2 import Template

from inspira.constants import SRC_DIRECTORY
from inspira.utils import singularize


def generate_repository_file(module_name):
    repository_directory = os.path.join(SRC_DIRECTORY, "repository")
    repository_file_name = f"{singularize(module_name.lower())}_repository.py"

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "repository_template.jinja2"
    )
    repository_file_path = os.path.join(repository_directory, repository_file_name)

    if os.path.exists(repository_file_path):
        click.echo(f"Repository '{repository_file_name}' already exists.")
        return

    with open(template_path, "r") as template_file, open(
        repository_file_path, "w"
    ) as output_file:
        template_content = template_file.read()
        template = Template(template_content)

        context = {
            "model_name_upper": singularize(module_name.capitalize())
        }

        content = template.render(context)
        output_file.write(content)

    click.echo(f"Repository '{repository_file_name}' created successfully.")
