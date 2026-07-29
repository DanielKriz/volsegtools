from volsegtools import AxisValues


def test_vector():
    vals = AxisValues
    assert hasattr(vals, "x")
    assert hasattr(vals, "y")
    assert hasattr(vals, "z")
