global_app_instance = None


def set_global_app(app):
    global global_app_instance
    global_app_instance = app


def get_global_app():
    return global_app_instance
