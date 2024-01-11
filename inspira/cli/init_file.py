import os


def create_init_file(directory):
    init_file = os.path.join(directory, "__init__.py")
    with open(init_file, "w"):
        pass
