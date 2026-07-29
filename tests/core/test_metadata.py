from volsegtools._model import DescriptiveStatistics


def test_descriptive_statistics_construction():
    stats = DescriptiveStatistics(0.0, 0.0, 0.0, 0.0)
    assert hasattr(stats, "mean")
    assert hasattr(stats, "std")
    assert hasattr(stats, "max")
    assert hasattr(stats, "min")
