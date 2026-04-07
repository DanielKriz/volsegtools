import pytest


def test_import_high_level():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_abc():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")


# All other modules are private, we still want to import them here so that
# we are sure, that there are not cyclic dependencies.


def test_import_converter():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_core():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_downsapler():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_model():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_preprocessor():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_serialization():
    try:
        pass
    except Exception:
        pytest.fail("No exception should be fired")
