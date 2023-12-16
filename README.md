# PyBlaze

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

PyBlaze is a lightweight framework for building asynchronous web applications.

## Features

- Asynchronous request handling
- Middleware support for extending functionality
- Routing system for defining URL patterns
- Templating engine for rendering dynamic content
- WebSocket support for real-time communication
- Sessions for managing user state across requests

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


## Sessions

Inside `app.py`, after initializing PyBlaze instance:


```python
app.session_type = "cookie"
```

Example 1: Setting a Session
```python
@get("/")
async def set_session_data(request):
    context = {"variable": "value"}
    request.set_session("key", 23)

    return JsonResponse(context)
```

Example 2: Retrieving Session Data
```python
@get("/")
async def get_session_data(request):
    context = {"variable": "value"}
    request.get_session("key")

    return JsonResponse(context)
```

Example 3: Removing Session Data
```python
@get("/")
async def remove_session_data(request):
    context = {"variable": "value"}
    request.remove_session("key")

    return JsonResponse(context)
```


## License

This project is licensed under the terms of the MIT license.