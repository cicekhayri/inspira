import os

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