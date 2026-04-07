"""
Contains downsampling related classes and functions.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .base_downsampler import BaseDownsampler
from .hierarchy_downsampler import HierarchyDownsampler

__all__ = [
    "BaseDownsampler",
    "HierarchyDownsampler",
]
