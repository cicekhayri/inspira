import secrets


def get_random_secret_key(length: int = 50) -> str:
    return secrets.token_urlsafe(length)[:length]
