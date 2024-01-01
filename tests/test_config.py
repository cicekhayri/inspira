from inspira.config import default_max_age


def test_get_item(sample_config):
    assert sample_config["SESSION_COOKIE_NAME"] == "session"
    assert sample_config["INVALID_KEY"] is None


def test_set_item(sample_config):
    sample_config["SESSION_COOKIE_NAME"] = "new_session"
    sample_config["NEW_KEY"] = "this_new_key"

    assert sample_config["SESSION_COOKIE_NAME"] == "new_session"
    assert sample_config["NEW_KEY"] == "this_new_key"


def test_default_values(sample_config):
    assert sample_config["SESSION_MAX_AGE"] == 2678400
    assert sample_config["SESSION_COOKIE_DOMAIN"] is None
    assert sample_config["SESSION_COOKIE_PATH"] is None
    assert sample_config["SESSION_COOKIE_HTTPONLY"] is True
    assert sample_config["SESSION_COOKIE_SECURE"] is True
    assert sample_config["SESSION_COOKIE_SAMESITE"] is None


def test_unknown_key_returns_none(sample_config):
    assert sample_config["UNKNOWN_KEY"] is None


def test_default_max_age():
    expected_result = 24 * 60 * 60 * 31
    print(expected_result)
    assert default_max_age() == expected_result