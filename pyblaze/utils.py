import re
import secrets

import inflect


def singularize(word):
    p = inflect.engine()
    return p.singular_noun(word) or word


def pluralize_word(word):
    p = inflect.engine()

    # if word.endswith("s"):
    #     return word

    return p.plural(word) or word


def get_random_secret_key(length=50):
    return secrets.token_urlsafe(length)[:length]


def convert_to_snake_case(input_string):
    snake_case_string = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", input_string)
    snake_case_string = snake_case_string.replace("-", "_")
    snake_case_string = snake_case_string.lower()

    return snake_case_string


def convert_to_camel_case(input_string):
    space_separated = input_string.replace("_", " ").replace("-", " ")
    capitalized_words = "".join(word.capitalize() for word in space_separated.split())
    camel_case_string = capitalized_words[0] + capitalized_words[1:]

    return camel_case_string
