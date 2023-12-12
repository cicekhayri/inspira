# PyBlaze

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

PyBlaze is a lightweight framework for building asynchronous web applications using the ASGI (Asynchronous Server Gateway Interface) protocol.

## Features

- Asynchronous request handling
- Middleware support for extending functionality
- Routing system for defining URL patterns
- Templating engine for rendering dynamic content

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

**Install PyBlaze**

```bash
pip install pyblaze
```

## Generating an App

To generate a new app for your project, run the following command:

```bash
pyblaze init
```

## Generate Database file

Use the following command to generate a database file:

```bash
pyblaze new database --name mydb --type sqlite
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
pyblaze new module orders
```

## Generated Directory Structure

After running the command to generate a new module (`pyblaze new module orders`), the directory structure of your project should look like the following:

```bash
├── app.py
├── database.py
└── src
    └── orders
        ├── __init__.py
        ├── order.py
        ├── order_controller.py
        └── order_repository.py
```

## Starting the Server

After generating your app and setting up the necessary resources, start the server with the following command:

```bash
uvicorn app:app --reload
```

## License

This project is licensed under the terms of the MIT license.