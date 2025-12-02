import volsegtools.model
import pytest


def test_descriptive_statistics_construction():
    stats = volsegtools.model.DescriptiveStatistics(0.0, 0.0, 0.0, 0.0)
    assert hasattr(stats, 'mean')
    assert hasattr(stats, 'std')
    assert hasattr(stats, 'max')
    assert hasattr(stats, 'min')


@pytest.mark.parametrize("params", [(0), (0, 0), (0, 0, 0)])
def test_descriptive_statistics_incorrect_construction(params):
    with pytest.raises(TypeError):
        volsegtools.model.DescriptiveStatistics(*params)
