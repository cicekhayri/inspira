import os

import click

from pyblaze.utils import get_random_secret_key, pluralize_word, singularize


def generate_project():
    create_app_file()
    click.echo("Project created successfully")


def create_app_file():
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "app_template.txt"
    )
    output_path = "app.py"

    with open(template_path, "r") as template_file, open(
        output_path, "w"
    ) as output_file:
        content = template_file.read().replace(
            "{{secret_key}}", get_random_secret_key()
        )
        output_file.write(content)


def add_route_to_app(resource_name):
    app_file_path = "app.py"
    route_line = f'app.add_resources("/{pluralize_word(resource_name)}", "src.{resource_name}.{singularize(resource_name)}_controller")\n'

    with open(app_file_path, "r") as app_file:
        lines = app_file.readlines()

    # Find the line after which to insert the new route line
    insert_index = 0
    for i, line in enumerate(lines):
        if "app = PyBlaze()" in line:
            insert_index = i + 5
            break

    # Insert the new route line
    lines.insert(insert_index, route_line)

    # Write the updated content back to app.py
    with open(app_file_path, "w") as app_file:
        app_file.writelines(lines)

    click.echo(f"Route for '{resource_name}' added to app.py.")
