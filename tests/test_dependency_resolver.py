from inspira.utils import resolve_dependencies_automatic, resolve_dependency


def test_resolve_dependencies_automatic_with_dependencies():
    class TestClass:
        def __init__(self, dep1, dep2):
            pass

    dependencies = resolve_dependencies_automatic(TestClass)
    assert len(dependencies) == 2


def test_resolve_dependencies_automatic_without_dependencies():
    class TestClass:
        def __init__(self):
            pass

    dependencies = resolve_dependencies_automatic(TestClass)
    assert dependencies is None


def test_resolve_dependencies():
    class TestClass:
        pass

    dependency_instance = resolve_dependency(TestClass)
    assert isinstance(dependency_instance, TestClass)


def test_resolve_dependency_with_invalid_dependency():
    invalid_dependency_instance = resolve_dependency(None)
    assert invalid_dependency_instance is None
