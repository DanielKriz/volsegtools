from typing import Optional

import pydantic
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from volsegtools.abc.kernel import ConvolutionKernel
from volsegtools._core import Bounds, Gaussian3DKernel


def _minimal_size_bounds_factory():
    return Bounds(5.0, None)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class DownsamplingParameters:
    downsampling_level_bounds: Optional[Bounds] = None
    should_remove_original_resolution: bool = False
    is_mask: bool = False
    acceptance_threshold: Optional[pydantic.PositiveFloat] = None
    kernel: ConvolutionKernel = Gaussian3DKernel(5, 1.0)
    size_per_level_bounds_in_mb: Bounds = pydantic.Field(
        default_factory=_minimal_size_bounds_factory
    )


def to_bytes(megabytes: int):
    return megabytes * 10**6
