import inspect
from typing import Any, Callable, List, Optional, Type


def resolve_dependencies_automatic(cls: Type) -> Optional[List[Any]]:
    dependencies: List[Any] = []

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


def resolve_dependency(dependency_type: Type[Callable]) -> Optional[Callable]:
    if dependency_type:
        init_method = getattr(dependency_type, "__init__", None)
        if init_method and init_method != object.__init__:
            constructor_params = inspect.signature(init_method).parameters.values()
            resolved_params = [
                resolve_dependency(param.annotation)
                for param in constructor_params
                if param.name != "self"
            ]
            return dependency_type(*resolved_params)
        else:
            return dependency_type()
    else:
        return None
