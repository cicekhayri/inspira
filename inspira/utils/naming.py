import re


def convert_to_snake_case(input_string: str) -> str:
    snake_case_string = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", input_string)
    snake_case_string = snake_case_string.replace("-", "_")
    snake_case_string = snake_case_string.lower()

    return snake_case_string


def convert_to_camel_case(input_string: str) -> str:
    space_separated = input_string.replace("_", " ").replace("-", " ")
    capitalized_words = "".join(word.capitalize() for word in space_separated.split())
    camel_case_string = capitalized_words[0] + capitalized_words[1:]

    return camel_case_string
