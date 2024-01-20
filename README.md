# Inspira

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Inspira is a lightweight framework for building asynchronous web applications.

## Quick Start

### Prerequisites

Make sure you have Python and `pip` installed on your system.

### Create a Python Virtual Environment

```bash
# Create a new directory for your project
$ mkdir myproject
$ cd myproject
```

**Create and activate a virtual environment**

```bash
$ python -m venv venv
$ source venv/bin/activate
```

**Install Inspira**

```bash
$ pip install inspira
```

## Generating an App

To generate a new app for your project, run the following command:

```bash
$ inspira init
```

## Generated Directory Structure

After running the `init` command, the directory structure of your project should look like the following:

```bash
├── main.py
├── src
│   ├── __init__.py
│   ├── controller
│   │   └── __init__.py
│   ├── model
│   │   └── __init__.py
│   ├── repository
│   │   └── __init__.py
│   └── service
│       └── __init__.py
└── tests
    └── __init__.py
```

## Generate Database file

Use the following command to generate a database file:

```bash
$ inspira new database --name mydb --type sqlite
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
```

## Generating Controller

To generate necessary controller for your project, run the following command:

```bash
$ inspira new controller order
```

## Generating Repository

To generate repository file, run the following command:

```bash
$ inspira new repository order
```

## Generating Service

To generate service file, run the following command:

```bash
$ inspira new service order
```

## Generating Model

To generate model file, run the following command:

```bash
$ inspira new model order
```

## Starting the Server

After generating your app and setting up the necessary resources, start the server with the following command:

```bash
$ uvicorn main:app --reload
```

## Links
Documentation: https://www.inspiraframework.com/


## License

This project is licensed under the terms of the MIT license.