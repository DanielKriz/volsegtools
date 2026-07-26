"""
Contains the base functions and classes that are used in other modules.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .bounds import Bounds
from .chunking_mode import ChunkingMode
from .computation_backend import ComputationBackend
from .data_kind import DataKind
from .gaussian_kernel import Gaussian3DKernel
from .kernel import ConvolutionKernel
from .timer import JSONTimerReporter, Timer, TimerReporter
from .unit_kind import UnitKind, to_angstrom, to_bytes, to_micrometer, unit_from_str
from .vector import Vector3
from .working_store import WorkingStore

__all__ = [
    "Bounds",
    "ChunkingMode",
    "ComputationBackend",
    "ConvolutionKernel",
    "DataKind",
    "Gaussian3DKernel",
    "JSONTimerReporter",
    "Timer",
    "TimerReporter",
    "UnitKind",
    "Vector3",
    "WorkingStore",
    "to_angstrom",
    "to_bytes",
    "to_micrometer",
    "unit_from_str",
]
