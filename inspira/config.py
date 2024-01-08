def default_max_age():
    return 24 * 60 * 60 * 31


class Config:
    def __init__(self):
        self.config_data = {
            "SESSION_COOKIE_NAME": "session",
            "SESSION_MAX_AGE": default_max_age(),
            "SESSION_COOKIE_DOMAIN": None,
            "SESSION_COOKIE_PATH": None,
            "SESSION_COOKIE_HTTPONLY": True,
            "SESSION_COOKIE_SECURE": True,
            "SESSION_COOKIE_SAMESITE": None,
            "TOKEN_EXPIRATION_TIME": 3600,
            "SECRET_KEY": "change_me"
        }

    def __getitem__(self, key):
        return self.config_data.get(key, None)

    def __setitem__(self, key, value):
        self.config_data[key] = value
