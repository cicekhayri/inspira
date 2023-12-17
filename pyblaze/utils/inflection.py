import inflect


def singularize(word):
    p = inflect.engine()
    return p.singular_noun(word) or word


def pluralize_word(word):
    p = inflect.engine()

    return p.plural(word) or word
