import inspect


def convert_param_type(value, param_type):
    try:
        if param_type is None or param_type == inspect.Parameter.empty:
            return str(value)
        return param_type(value)
    except ValueError:
        return value
