import os

import click

from inspira.utils import pluralize_word, singularize


def generate_model_file(module_name):
    base_path = "src"
    # Specify the directory path
    model_directory = os.path.join(base_path, module_name.lower())

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "model_template.txt"
    )
    repository_file_path = os.path.join(
        model_directory, f"{singularize(module_name.lower())}.py"
    )

    with open(template_path, "r") as template_file, open(
        repository_file_path, "w"
    ) as output_file:
        content = (
            template_file.read()
            .replace(
                "{{module_name_capitalize}}", singularize(module_name.capitalize())
            )
            .replace("{{module_name_plural}}", pluralize_word(module_name))
        )
        output_file.write(content)


def database_file_exists() -> bool:
    main_script_path = "database.py"

    # Check if the main script exists
    if not os.path.isfile(main_script_path):
        click.echo("Main script (database.py) not found.")
        return False

    return True
