import datetime
import json

from http.cookies import SimpleCookie

from itsdangerous import URLSafeTimedSerializer

from inspira.globals import get_global_app
from inspira.logging import log


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        return super().default(obj)


def encode_session_data(session_data, secret_key):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(
        seconds=get_global_app().config["SESSION_MAX_AGE"]
    )

    serializer = URLSafeTimedSerializer(secret_key)

    payload = {**session_data, "expiration_time": expiration_time}

    json_session_data = json.dumps(payload, cls=DateTimeEncoder)

    session_token = serializer.dumps(json_session_data)

    return session_token


def decode_session_data(session_token, secret_key):
    try:
        serializer = URLSafeTimedSerializer(secret_key)
        json_session_data = serializer.loads(session_token)
        decoded_payload = json.loads(json_session_data)
        return decoded_payload
    except Exception as e:
        log.error(f"Error decoding session: {e}")
        return None


def get_or_create_session(request):
    session_cookie = get_session_token_from_request(
        request, get_global_app().config["SESSION_COOKIE_NAME"]
    )
    secret_key = get_global_app().secret_key

    if session_cookie:
        try:
            session_data = decode_session_data(session_cookie, secret_key)
            return session_data
        except ValueError:
            log.error("Invalid signature when decoding session")
            raise ValueError("Invalid signature")
    else:
        log.error("No session in cookies")


def get_session_token_from_request(request, session_cookie_name):
    cookies = SimpleCookie(request.get_headers().get("cookie", ""))
    token_cookie = cookies.get(session_cookie_name)
    return token_cookie.value if token_cookie else None
