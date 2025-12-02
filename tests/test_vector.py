import volsegtools.core as vst

def test_vector():
    vec = vst.Vector3()
    assert hasattr(vec, 'x')
    assert hasattr(vec, 'y')
    assert hasattr(vec, 'z')
