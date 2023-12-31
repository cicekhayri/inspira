import base64
import datetime
import hashlib
import hmac
import json
from http.cookies import SimpleCookie


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


def encode_session_data(session_data, secret_key):
    # Convert the session data to JSON and base64 encode it
    payload = base64.urlsafe_b64encode(
        json.dumps(session_data, cls=DateTimeEncoder).encode()
    ).decode()

    # Create a more secure signature using SHA-256 with the secret_key
    signature = hashlib.sha256(f"{payload}{secret_key}".encode()).hexdigest()

    # Combine the payload and signature
    session_id = f"{payload}.{signature}"

    return session_id


def decode_session_data(session_id, secret_key):
    # Check if session_id has the expected format
    if "." not in session_id:
        raise ValueError("Invalid session ID format")

    # Split the session ID into payload and signature
    payload, signature = session_id.split(".", 1)

    # Decode the payload and return the session data
    decoded_payload = base64.urlsafe_b64decode(
        payload + "=" * (-len(payload) % 4)
    ).decode()

    # Verify the signature using the secret key
    expected_signature = hashlib.sha256(f"{payload}{secret_key}".encode()).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        raise ValueError("Invalid signature")

    return json.loads(decoded_payload)


def get_or_create_session(request, secret_key):
    cookies = SimpleCookie(request.get_headers().get("cookie", ""))
    session_id = cookies.get("session")
    session_data = {}

    if session_id:
        try:
            session_data = decode_session_data(session_id.value, secret_key)
            return session_data
        except ValueError:
            print("Invalid session")
    else:
        print("No session in cookies")

    if request.session:
        encoded_payload = encode_session_data(session_data, secret_key)
        return encoded_payload
