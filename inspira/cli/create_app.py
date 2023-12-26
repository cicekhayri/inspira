import os

import click

from inspira.utils import get_random_secret_key


def generate_project():
    create_app_file()
    click.echo("Project created successfully")


def create_app_file():
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "app_template.txt"
    )
    output_path = "main.py"

    with open(template_path, "r") as template_file, open(
        output_path, "w"
    ) as output_file:
        content = template_file.read().replace(
            "{{secret_key}}", get_random_secret_key()
        )
        output_file.write(content)
