"""
Contains downsampling related classes and functions.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .hierarchy_downsampling_strategy import (
    HierarchyDownsamplingStrategy,
)

__all__ = [
    "HierarchyDownsamplingStrategy",
    "NullDownsamplingStrategy",
]
