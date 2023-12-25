from inspira.utils import (
    convert_to_camel_case,
    convert_to_snake_case,
    get_random_secret_key,
    pluralize_word,
    singularize,
)


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


def test_convert_to_snake_case():
    assert convert_to_snake_case("get-started") == "get_started"
    assert convert_to_snake_case("getstarted") == "getstarted"
    assert convert_to_snake_case("Get-Started") == "get_started"


def test_convert_to_camel_case():
    assert convert_to_camel_case("get-started") == "GetStarted"
    assert convert_to_camel_case("get_started") == "GetStarted"
    assert convert_to_camel_case("GetStarted") == "Getstarted"
