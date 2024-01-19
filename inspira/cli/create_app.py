import os

import click

from inspira.cli.init_file import create_init_file
from inspira.constants import SRC_DIRECTORY
from inspira.utils import get_random_secret_key


def generate_project():
    create_app_file()
    create_directory_structure()
    create_test_directory()
    click.echo("Project created successfully")


def create_test_directory():
    test_directory = os.path.join("tests")
    os.makedirs(test_directory)

    create_init_file(test_directory)


def create_directory_structure():
    base_dir = SRC_DIRECTORY
    dirs = [
        base_dir,
        os.path.join(base_dir, "__init__.py"),
        os.path.join(base_dir, "controller"),
        os.path.join(base_dir, "controller", "__init__.py"),
        os.path.join(base_dir, "model"),
        os.path.join(base_dir, "model", "__init__.py"),
        os.path.join(base_dir, "repository"),
        os.path.join(base_dir, "repository", "__init__.py"),
        os.path.join(base_dir, "service"),
        os.path.join(base_dir, "service", "__init__.py"),
    ]

    for dir_path in dirs:
        if not os.path.exists(dir_path):
            if "." in dir_path:
                module_name = os.path.basename(os.path.dirname(dir_path))
                import_statement = ""

                if module_name != base_dir:
                    import_statement = f"from src import {module_name}\n"

                with open(dir_path, "a") as init_file:
                    init_file.write(import_statement)
            else:
                os.makedirs(dir_path)


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
