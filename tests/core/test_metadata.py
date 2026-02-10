import pytest

import volsegtools.model
from volsegtools.model import (
    DescriptiveStatistics
)


def test_descriptive_statistics_construction():
    stats = DescriptiveStatistics(0.0, 0.0, 0.0, 0.0)
    assert hasattr(stats, 'mean')
    assert hasattr(stats, 'std')
    assert hasattr(stats, 'max')
    assert hasattr(stats, 'min')


@pytest.mark.parametrize("params", [(0), (0, 0), (0, 0, 0)])
def test_descriptive_statistics_incorrect_construction(params):
    with pytest.raises(TypeError):
        DescriptiveStatistics(*params)
