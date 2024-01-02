from inspira import Inspira


def test_set_global_app():
    from inspira.globals import get_global_app, set_global_app

    app_instance = Inspira()
    set_global_app(app_instance, secret_key="dummy")

    assert get_global_app() == app_instance
