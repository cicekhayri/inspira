import base64
import datetime
import hashlib
import json

import pytest

from inspira.utils.session_utils import (
    DateTimeEncoder,
    decode_session_data,
    encode_session_data,
    get_or_create_session,
)


def test_datatime_encoder():
    encoder = DateTimeEncoder()

    dt_object = datetime.datetime(2023, 1, 15, 12, 30, 0)
    encoded_dt = encoder.encode(dt_object)
    assert encoded_dt == '"2023-01-15T12:30:00"'


def test_datetime_encoder_list_with_datetime_object():
    encoder = DateTimeEncoder()
    dt_object = datetime.datetime(2023, 1, 15, 12, 30, 0)
    data = {"timestamp": dt_object, "other_data": "example"}
    encoded_data = encoder.encode(data)
    assert (
        encoded_data == '{"timestamp": "2023-01-15T12:30:00", "other_data": "example"}'
    )


def test_datatime_encoder_non_datetime_object():
    encoder = DateTimeEncoder()
    non_dt_object = {"key": "value"}
    encoded_non_dt = encoder.encode(non_dt_object)
    assert encoded_non_dt == '{"key": "value"}'


def test_encode_decode_session_data(secret_key):
    session_data = {"email": "hayri@inspiraframework.com"}
    session_token = encode_session_data(session_data, secret_key)

    decoded_session_data = decode_session_data(session_token, secret_key)

    assert decoded_session_data == session_data


def test_get_or_create_session_with_valid_cookie(secret_key):
    session_data = {"email": "hayri@inspiraframework.com"}
    encoded_session_token = encode_session_data(session_data, secret_key)

    class MockRequest:
        def __init__(self, cookie_value):
            self.headers = {"cookie": cookie_value}

        def get_headers(self):
            return self.headers

    mock_request = MockRequest(f"session={encoded_session_token}")
    result = get_or_create_session(mock_request, secret_key)

    assert result == session_data


def test_get_or_create_session_with_invalid_session(secret_key):
    session_id = "invalid_session"

    class MockRequest:
        def __init__(self, cookie_value):
            self.session = None
            self.headers = {"cookie": cookie_value}

        def get_headers(self):
            return self.headers

    mock_request = MockRequest(f"session={session_id}")

    with pytest.raises(ValueError, match="Invalid signature"):
        get_or_create_session(mock_request, secret_key)
