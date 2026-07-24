"""
Contains downsampling related classes and functions.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .null import Null
from .nearest_neighbor import (
    NearestNeighbor,
)
from .pooling import (
    PoolingDownsamplingStrategy,
    AveragePooling,
    MinPooling,
    MaxPooling,
)
from .smoothing import (
    Smoothing,
    SeparatedSmoothing,
    StridedSmoothing,
)
from .continuous_interpolation import (
    InterpolationBased,
    TrilinearInterpolation,
    TricubicInterpolation,
    TriquinticInterpolation,
)

__all__ = [
    "Null",
    "NearestNeighbor",
    "PoolingDownsamplingStrategy",
    "AveragePooling",
    "MinPooling",
    "MaxPooling",
    "Smoothing",
    "SeparatedSmoothing",
    "StridedSmoothing",
    "InterpolationBased",
    "TrilinearInterpolation",
    "TricubicInterpolation",
    "TriquinticInterpolation",
]
