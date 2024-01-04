import bcrypt

from inspira.constants import UTF8


class UserMixin:
    def __init__(self):
        self.password = None

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def set_password(self, password):
        hashed_password = bcrypt.hashpw(password.encode(UTF8), bcrypt.gensalt())
        self.password = hashed_password.decode(UTF8)

    def check_password_hash(self, password):
        return bcrypt.checkpw(password.encode(UTF8), self.password.encode(UTF8))


class AnonymousUserMixin:
    @property
    def is_authenticated(self):
        return False

    @property
    def is_active(self):
        return False

    @property
    def is_anonymous(self):
        return True
