import inspect


def resolve_dependencies_automatic(cls):
    dependencies = []

    # Get the constructor parameters, if available
    init_method = getattr(cls, "__init__", None)

    if init_method and init_method != object.__init__:
        constructor_params = inspect.signature(init_method).parameters.values()
        for param in constructor_params:
            if param.name != "self":  # Exclude 'self' parameter
                param_type = param.annotation
                dependency = resolve_dependency(param_type)
                dependencies.append(dependency)

    return dependencies if dependencies else None


def resolve_dependency(dependency_type):
    return dependency_type() if dependency_type else None
