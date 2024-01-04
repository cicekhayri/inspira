import datetime
import json
from http.cookies import SimpleCookie

from itsdangerous import URLSafeSerializer

from inspira.globals import get_global_app


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


def encode_session_data(session_data, secret_key):
    serializer = URLSafeSerializer(secret_key)
    json_session_data = json.dumps(session_data, cls=DateTimeEncoder)
    session_token = serializer.dumps(json_session_data)
    return session_token


def decode_session_data(session_token, secret_key):
    try:
        serializer = URLSafeSerializer(secret_key)
        json_session_data = serializer.loads(session_token)
        decoded_payload = json.loads(json_session_data)
        return decoded_payload
    except Exception as e:
        print(f"Error decoding session: {e}")
        raise ValueError("Invalid signature") from e


def get_or_create_session(request, secret_key):
    session_cookie = get_session_token_from_request(
        request, get_global_app().config["SESSION_COOKIE_NAME"]
    )
    session_data = {}

    if session_cookie:
        try:
            session_data = decode_session_data(session_cookie, secret_key)
            return session_data
        except ValueError:
            print("Invalid signature when decoding session")
            raise ValueError("Invalid signature")
    else:
        print("No session in cookies")

    if request.session:
        encoded_payload = encode_session_data(session_data, secret_key)
        return encoded_payload


def get_session_token_from_request(request, session_cookie_name):
    cookies = SimpleCookie(request.get_headers().get("cookie", ""))
    token_cookie = cookies.get(session_cookie_name)

    return token_cookie.value if token_cookie else None
