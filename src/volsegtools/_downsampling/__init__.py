"""
Contains downsampling related classes and functions.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .common import (
    calculate_approx_downsampled_sizes,
    calculate_steps,
)
from .continuous_interpolation import (
    InterpolationBased,
    TricubicInterpolation,
    TrilinearInterpolation,
    TriquinticInterpolation,
)
from .nearest_neighbor import (
    NearestNeighbor,
)
from .null import Null
from .pooling import (
    AveragePooling,
    MaxPooling,
    MinPooling,
    PoolingDownsamplingStrategy,
)
from .smoothing import (
    SeparatedSmoothing,
    Smoothing,
    StridedSmoothing,
)

__all__ = [
    "AveragePooling",
    "InterpolationBased",
    "MaxPooling",
    "MinPooling",
    "NearestNeighbor",
    "Null",
    "PoolingDownsamplingStrategy",
    "SeparatedSmoothing",
    "Smoothing",
    "StridedSmoothing",
    "TricubicInterpolation",
    "TrilinearInterpolation",
    "TriquinticInterpolation",
    "calculate_approx_downsampled_sizes",
    "calculate_steps",
]
