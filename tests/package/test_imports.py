import pytest


def test_import_abc():
    try:
        import volsegtools.abc
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_converter():
    try:
        import volsegtools.converter
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_core():
    try:
        import volsegtools.core
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_downsapler():
    try:
        import volsegtools.downsampler
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_model():
    try:
        import volsegtools.model
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_preprocessor():
    try:
        import volsegtools.preprocessor
    except Exception:
        pytest.fail("No exception should be fired")


def test_import_serialization():
    try:
        import volsegtools.serialization
    except Exception:
        pytest.fail("No exception should be fired")
