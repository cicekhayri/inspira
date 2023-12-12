from pyblaze.utils import get_random_secret_key, pluralize_word, singularize


def test_singularize_word():
    word = "orders"
    expected = "order"
    assert singularize(word) == expected


def test_pluralize_word():
    word = "order"
    expected = "orders"
    assert pluralize_word(word) == expected


def test_get_random_secret_key_length():
    length = 10
    key = get_random_secret_key(length)
    assert len(key) == length


def test_get_random_secret_key_uniqueness():
    key1 = get_random_secret_key()
    key2 = get_random_secret_key()

    assert key1 != key2
