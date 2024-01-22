import os

import click
from jinja2 import Template

from inspira.constants import SRC_DIRECTORY
from inspira.utils import pluralize_word, singularize


def generate_model_file(module_name):
    model_directory = os.path.join(SRC_DIRECTORY, "model")
    model_file_name = f"{singularize(module_name.lower())}.py"
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "model_template.jinja2"
    )
    model_file_path = os.path.join(model_directory, model_file_name)

    if os.path.exists(model_file_path):
        click.echo(f"Model '{model_file_name}' already exists.")
        return

    with open(template_path, "r") as template_file, open(
        model_file_path, "w"
    ) as output_file:
        template_content = template_file.read()
        template = Template(template_content)

        context = {
            "module_name_capitalize": singularize(module_name.capitalize()),
            "module_name_plural": pluralize_word(module_name),
        }
        content = template.render(context)
        output_file.write(content)

    click.echo(f"Model '{model_file_name}' created successfully.")


def database_file_exists() -> bool:
    main_script_path = "database.py"

    if not os.path.isfile(main_script_path):
        click.echo("Main script (database.py) not found.")
        return False

    return True
