def test_set_global_app():
    from inspira.globals import get_global_app, set_global_app

    app_instance = "example_app"
    set_global_app(app_instance)

    assert get_global_app() == app_instance