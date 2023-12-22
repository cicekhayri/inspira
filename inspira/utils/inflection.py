from typing import Literal

import inflect


def singularize(word: str) -> str | Literal[False]:
    p = inflect.engine()
    return p.singular_noun(word) or word


def pluralize_word(word: str) -> str:
    p = inflect.engine()

    return p.plural(word) or word
