import secrets

import inflect


def singularize(word):
    p = inflect.engine()
    return p.singular_noun(word) or word


def pluralize_word(word):
    p = inflect.engine()

    if word.endswith("s"):
        return word

    return p.plural(word) or word


def get_random_secret_key(length=50):
    return secrets.token_urlsafe(length)[:length]
