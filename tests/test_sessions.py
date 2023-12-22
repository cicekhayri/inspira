import base64
import datetime
import hashlib
import json

from inspira.sessions import (
    decode_session_data,
    encode_session_data,
    get_or_create_session,
    DateTimeEncoder,
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


def test_encode_session_data():
    session_data = {"email": "hayri@inspiraframework.com"}
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
    print(expected_result)
    assert parts[1] == expected_signature


def test_encode_session_data_empty():
    secret_key = "you_secret_key"

    empty_session_data = {}
    empty_result = encode_session_data(empty_session_data, secret_key)

    assert empty_result is not None
    assert isinstance(empty_result, str)
    assert "." in empty_result


def test_decode_session_data():
    session_id = "eyJlbWFpbCI6ICJoYXlyaUBtb2R1bGFmcmFtZXdvcmsuY29tIn0=.178fb652833e4944b7cd5ef8339cdd020b13d28f628410f4894d0e27ad23deb0"

    actual_result = decode_session_data(session_id)
    expected_result = {"email": "hayri@inspiraframework.com"}

    assert actual_result == expected_result


def test_get_or_create_session():
    session_id = "eyJlbWFpbCI6ICJoYXlyaUBtb2R1bGFmcmFtZXdvcmsuY29tIn0=.178fb652833e4944b7cd5ef8339cdd020b13d28f628410f4894d0e27ad23deb0"
    expected_result = {"email": "hayri@inspiraframework.com"}

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
