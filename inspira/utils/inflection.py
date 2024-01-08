from typing import Literal

import inflect

p = inflect.engine()


def singularize(word: str) -> str | Literal[False]:
    return p.singular_noun(word) or word


def pluralize_word(word: str) -> str:
    if word.endswith("s"):
        return word
    return p.plural(word) or word
