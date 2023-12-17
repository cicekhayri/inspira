import os
import re

from pyblaze.utils import pluralize_word, singularize


def generate_repository_file(module_name):
    base_path = "src"
    # Specify the directory path
    model_directory = os.path.join(base_path, module_name.lower())

    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "repository_template.txt"
    )
    repository_file_path = os.path.join(
        model_directory, f"{singularize(module_name.lower())}_repository.py"
    )

    with open(template_path, "r") as template_file, open(
        repository_file_path, "w"
    ) as output_file:
        content = (
            template_file.read()
            .replace("{{model_name}}", pluralize_word(module_name))
            .replace("{{model_name_upper}}", singularize(module_name.capitalize()))
            .replace("{{module_name}}", module_name)
            .replace("{{model_name_singular}}", singularize(module_name.lower()))
        )
        output_file.write(content)

    add_repository_dependency_to_controller(module_name)


def add_repository_dependency_to_controller(module_name):
    controller_file_path = os.path.join(
        "src", module_name.lower(), f"{singularize(module_name.lower())}_controller.py"
    )
    module_name_capitalized = singularize(module_name.lower()).capitalize()
    singularized_module_name = singularize(module_name.lower())

    with open(controller_file_path, "r") as controller_file:
        existing_content = controller_file.read()

    # Define the __init__ method
    init_method = f"""\n
    def __init__(self, {singularized_module_name}_repository: {module_name_capitalized}Repository):
        self._{singularized_module_name}_repository = {singularized_module_name}_repository"""

    import_statement = (
        f""
        f"\n\nfrom src.{module_name.lower()}.{singularize(module_name.lower())}_repository"
        f" import {module_name_capitalized}Repository\n\n\n"
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
