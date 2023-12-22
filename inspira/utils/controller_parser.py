import ast


def parse_controller_decorators(file_path: str) -> bool:
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Name)
                    and (
                        decorator.func.id == "path" or decorator.func.id == "websocket"
                    )
                ):
                    return True
    return False
