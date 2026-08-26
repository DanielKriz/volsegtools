import volsegtools as vst
import pytest

class HandleStub:
    def __init__(self, nbytes):
        self.nbytes = nbytes

class ChannelStub:
    def __init__(self, nbytes):
        self.handle = HandleStub(nbytes)


def test_calculate_approx_downsampled_sizes():
    assert vst.calculate_approx_downsampled_sizes(
            ChannelStub(64_000),
            10,
            2
        ) == [8_000, 1_000, 125, 15.625]


def test_calculate_steps():
    assert vst.calculate_steps(ChannelStub(64_000), 10, 2) == 4


@pytest.mark.parametrize(
    "threshold, expected_levels",
    [
        (10, [8000, 1000, 125, 15.625]),
        (100, [8000, 1000, 125]),
        (1_000, [8000, 1000]),
        (10_000, []),
    ],
)
def test_effect_of_threshold_on_sizes(threshold, expected_levels):
    assert vst.calculate_approx_downsampled_sizes(
            ChannelStub(64_000),
            threshold,
            2
        ) == expected_levels


@pytest.mark.parametrize(
    "threshold, expected_levels",
    [
        (10, 4),
        (100, 3),
        (1_000, 2),
        (10_000, 0),
    ],
)
def test_effect_of_threshold_on_steps(threshold, expected_levels):
    assert vst.calculate_steps(
            ChannelStub(64_000),
            threshold,
            2
        ) == expected_levels


@pytest.mark.parametrize("factor", [0, 1, -1])
def test_invalid_factor_in_sizes(factor):
    with pytest.raises(RuntimeError):
        vst.calculate_approx_downsampled_sizes(ChannelStub(0), 1024, factor)


@pytest.mark.parametrize("factor", [0, 1, -1])
def test_invalid_factor_in_steps(factor):
    with pytest.raises(RuntimeError):
        vst.calculate_steps(ChannelStub(0), 1024, factor)


@pytest.mark.parametrize("threshold", [0, -1])
def test_invalid_threshold_in_sizes(threshold):
    with pytest.raises(RuntimeError):
        vst.calculate_approx_downsampled_sizes(ChannelStub(0), threshold, 2)


@pytest.mark.parametrize("threshold", [0, -1])
def test_invalid_threshold_in_steps(threshold):
    with pytest.raises(RuntimeError):
        vst.calculate_steps(ChannelStub(0), threshold, 2)
