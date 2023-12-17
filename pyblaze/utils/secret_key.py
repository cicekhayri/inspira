import secrets


def get_random_secret_key(length=50):
    return secrets.token_urlsafe(length)[:length]
