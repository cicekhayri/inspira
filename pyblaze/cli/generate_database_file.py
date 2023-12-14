import os

import click


def create_database_file(database_name, database_type):
    template_path = os.path.join(
        os.path.dirname(__file__), "templates", "database_template.txt"
    )
    output_path = "database.py"

    if database_type == "postgres":
        database_url = f"postgresql://USERNAME:PASSWORD@localhost:5432/{database_name}"
    elif database_type == "mysql":
        database_url = f"mysql://USERNAME:PASSWORD@localhost:3306/{database_name}"
    elif database_type == "sqlite":
        database_url = f"sqlite:///{database_name}.db"
    elif database_type == "mssql":
        # Assuming a Windows authentication connection
        database_url = (
            f"mssql+pyodbc://"
            f"@localhost/{database_name}?driver=ODBC+Driver+17+for+SQL+Server"
        )

    with open(template_path, "r") as template_file, open(
        output_path, "w"
    ) as output_file:
        template_content = template_file.read()
        template_content = template_content.replace("{{database_url}}", database_url)
        output_file.write(template_content)

    click.echo("Database file created successfully.")
