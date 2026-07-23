"""
Contains downsampling related classes and functions.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .hierarchy_downsampling_strategy import (
    HierarchyDownsamplingStrategy,
)
from .null_downsampling_strategy import NullDownsamplingStrategy
from .nearest_neighbor_downsampling_strategy import (
    NearestNeighborDownsamplingStrategy,
)
from .pooling_downsampling_strategy import (
    PoolingDownsamplingStrategy,
    AveragePoolingStrategy,
    MinPoolingStrategy,
    MaxPoolingStrategy,
)
from .separated_smoothing import (
    SeparableSmoothing,
)
from .strided_smoothing import (
    StridedSmoothing,
)
from .continuous_interpolation import (
    InterpolationBased,
    TrilinearInterpolation,
    TricubicInterpolation,
    TriquinticInterpolation,
)
from .wavelet_transform import (
    WaveletTransform
)

__all__ = [
    "HierarchyDownsamplingStrategy",
    "NullDownsamplingStrategy",
    "NearestNeighborDownsamplingStrategy",
    "PoolingDownsamplingStrategy",
    "AveragePoolingStrategy",
    "MinPoolingStrategy",
    "MaxPoolingStrategy",
    "SeparableSmoothing",
    "StridedSmoothing",
    "InterpolationBased",
    "TrilinearInterpolation",
    "TricubicInterpolation",
    "TriquinticInterpolation",
    "WaveletTransform",
]
