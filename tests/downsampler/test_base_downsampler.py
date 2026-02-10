import pytest

from volsegtools.core import DownsamplingParameters
from volsegtools.downsampler import BaseDownsampler


def test_base_downsampler_init():
    try:
        BaseDownsampler(DownsamplingParameters())
    except:
        pytest.fail()


def test_base_parameters_property():
    original_params = DownsamplingParameters()
    downsampler = BaseDownsampler(original_params)
    params = downsampler.parameters
    assert type(params) is DownsamplingParameters
    assert params.downsampling_level_bounds \
            == original_params.downsampling_level_bounds
    assert params.should_remove_original_resolution \
            == original_params.should_remove_original_resolution
    assert params.is_mask == original_params.is_mask
    assert params.acceptance_threshold == original_params.acceptance_threshold
    assert params.kernel == original_params.kernel
    assert params.size_per_level_bounds_in_mb \
            == original_params.size_per_level_bounds_in_mb


def test_base_parameters_reflect_input():
    original_params = DownsamplingParameters(
        should_remove_original_resolution=True
    )
    downsampler = BaseDownsampler(original_params)
    params = downsampler.parameters
    assert type(params) is DownsamplingParameters
    assert params.downsampling_level_bounds \
            == original_params.downsampling_level_bounds
