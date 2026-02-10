from volsegtools.core import Vector3

def test_vector():
    vec = Vector3()
    assert hasattr(vec, 'x')
    assert hasattr(vec, 'y')
    assert hasattr(vec, 'z')
