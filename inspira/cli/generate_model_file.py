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

    update_init_db(module_name)


def update_init_db(module_name):
    # Assuming the database.py is in the same directory as this script
    main_script_path = "database.py"

    if database_file_exists():
        # Read the content of the main script
        with open(main_script_path, "r") as main_script_file:
            main_script_content = main_script_file.read()

        # Check if the import statement already exists in the init_db function
        import_statement = (
            f"import src.{module_name.lower()}.{singularize(module_name)}"
        )
        if import_statement in main_script_content:
            click.echo(
                f"Import statement for '{module_name}' already exists in init_db."
            )
            return

        # Find the location of the init_db function
        init_db_keyword = "def init_db():"
        init_db_index = main_script_content.find(init_db_keyword)

        # If init_db function is found, insert the import statement after it
        if init_db_index != -1:
            init_db_end = init_db_index + len(init_db_keyword)
            main_script_content = (
                main_script_content[:init_db_end]
                + f"\n    {import_statement}\n"
                + main_script_content[init_db_end:]
            )
            click.echo(f"Import statement for '{module_name}' added to init_db.")
        else:
            click.echo("Function 'init_db()' not found in database.py.")

        # Write the updated content back to the main script
        with open(main_script_path, "w") as main_script_file:
            main_script_file.write(main_script_content)


def database_file_exists() -> bool:
    main_script_path = "database.py"

    # Check if the main script exists
    if not os.path.isfile(main_script_path):
        click.echo("Main script (database.py) not found.")
        return False

    return True
