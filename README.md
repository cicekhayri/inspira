# Inspira

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Inspira is a lightweight framework for building asynchronous web applications.

## Quick Start

### Prerequisites

Make sure you have Python and `pip` installed on your system.

### Create a Python Virtual Environment

```bash
# Create a new directory for your project
mkdir myproject
cd myproject
```

**Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
```

**Install Inspira**

```bash
pip install inspira
```

## Generating an App

To generate a new app for your project, run the following command:

```bash
inspira init
```

## Generate Database file

Use the following command to generate a database file:

```bash
inspira new database --name mydb --type sqlite
```

This command will create a new database file named `mydb` with `SQLite` as the database type.

The generated database file (`database.py`) will typically contain initial configurations and may look like this:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

engine = create_engine("sqlite:///mydb.db")
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
```

## Generating Modules

To generate necessary resources for your project, run the following command:

```bash
inspira new module orders
```

## Generated Directory Structure

After running the command to generate a new module (`inspira new module orders`), the directory structure of your project should look like the following:

```bash
├── main.py
├── database.py
└── src
    └── orders
        ├── __init__.py
        ├── order.py
        ├── order_controller.py
        └── order_repository.py
        └── order_service.py
```

## Starting the Server

After generating your app and setting up the necessary resources, start the server with the following command:

```bash
uvicorn main:app --reload
```

## Links
Documentation: https://www.inspiraframework.com/


## License

This project is licensed under the terms of the MIT license.