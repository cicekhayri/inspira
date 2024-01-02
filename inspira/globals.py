global_app_instance = None


def set_global_app(app, secret_key):
    global global_app_instance
    global_app_instance = app
    global_app_instance.secret_key = secret_key


def get_global_app():
    return global_app_instance
