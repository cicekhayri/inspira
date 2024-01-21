from inspira.decorators.path import path


@path("/example/path")
class ExampleController:
    pass


def test_path_decorator():
    assert hasattr(ExampleController, "__path__")
    assert ExampleController.__path__ == "/example/path"
    assert hasattr(ExampleController, "__is_controller__")
    assert ExampleController.__is_controller__ is True
