import base64
import hashlib
import json

from pyblaze.sessions import (
    decode_session_data,
    encode_session_data,
    get_or_create_session,
)


def test_encode_session_data():
    session_data = {"user_id": 123, "username": "test_user"}
    secret_key = "your_secret_key"

    expected_result = encode_session_data(session_data, secret_key)

    assert expected_result is not None
    assert isinstance(expected_result, str)

    parts = expected_result.split(".")
    assert len(parts) == 2

    decoded_payload = base64.urlsafe_b64decode(
        parts[0] + "=" * (-len(parts[0]) % 4)
    ).decode()
    decoded_data = json.loads(decoded_payload)
    assert decoded_data == session_data

    expected_signature = hashlib.sha256(f"{parts[0]}{secret_key}".encode()).hexdigest()
    assert parts[1] == expected_signature


def test_encode_session_data_empty():
    secret_key = "you_secret_key"

    empty_session_data = {}
    empty_result = encode_session_data(empty_session_data, secret_key)

    assert empty_result is not None
    assert isinstance(empty_result, str)
    assert "." in empty_result


def test_decode_session_data():
    session_id = "eyJlbWFpbCI6ImhheXJpQHB5YmxhemUuY29tIn0.e30.zOEUjH6Q3PtYI16WgpF7xM1jlHDM8gbD9mRNgYxOKgI"

    actual_result = decode_session_data(session_id)
    expected_result = {"email": "hayri@pyblaze.com"}

    assert actual_result == expected_result


def test_get_or_create_session():
    session_id = "eyJlbWFpbCI6ImhheXJpQHB5YmxhemUuY29tIn0.e30.zOEUjH6Q3PtYI16WgpF7xM1jlHDM8gbD9mRNgYxOKgI"
    expected_result = {"email": "hayri@pyblaze.com"}

    class MockRequest:
        def __init__(self, cookie_value):
            self.headers = {"cookie": cookie_value}

        def get_headers(self):
            return self.headers

    secret_key = "your_secret_key"
    mock_request = MockRequest(f"session={session_id}")

    actual_result = get_or_create_session(mock_request, secret_key)

    decoded_session_data = decode_session_data(session_id)
    assert actual_result == decoded_session_data == expected_result
