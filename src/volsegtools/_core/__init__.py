"""
Contains the base functions and classes that are used in other modules.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .data_kind import DataKind
from .vector import Vector3
from .bounds import Bounds
from .gaussian_kernel_3D import Gaussian3DKernel
from .downsampling_parameters import DownsamplingParameters, to_bytes

__all__ = [
    "DataKind",
    "Vector3",
    "Bounds",
    "Gaussian3DKernel",
    "DownsamplingParameters",
    "to_bytes",
]
