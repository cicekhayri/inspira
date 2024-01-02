from datetime import datetime, timedelta

import jwt

from inspira.requests import RequestContext
from inspira.globals import get_global_app


app = get_global_app()

if app:
    SECRET_KEY = app.secret_key
    TOKEN_EXPIRATION_TIME = app.config["TOKEN_EXPIRATION_TIME"]
else:
    SECRET_KEY = "dummy"
    TOKEN_EXPIRATION_TIME = 3600


def login_user(user_id):
    token = generate_token(user_id)
    request = RequestContext.get_request()
    request.set_session("token", token)


def logout_user():
    request = RequestContext.get_request()
    session = request.session

    if session and "token" in session:
        request.remove_session("token")


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=TOKEN_EXPIRATION_TIME),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
