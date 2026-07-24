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
from .timer import Timer, TimerReporter, JSONTimerReporter
from .unit_kind import UnitKind, unit_from_str, to_micrometer, to_angstrom
from .chunking_mode import ChunkingMode
from .working_store import WorkingStore

__all__ = [
    "DataKind",
    "Vector3",
    "Bounds",
    "Gaussian3DKernel",
    "DownsamplingParameters",
    "to_bytes",
    "Timer",
    "TimerReporter",
    "JSONTimerReporter",
    "UnitKind",
    "unit_from_str",
    "to_micrometer",
    "to_angstrom",
    "ChunkingMode",
    "WorkingStore",
]
