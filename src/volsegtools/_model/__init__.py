"""
Contains classes, functions and models related to the data that are used
through this project.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .chunking_mode import ChunkingMode
from .metadata import (
    ChannelMetadata,
    DescriptiveStatistics,
    Metadata,
    OriginalTimeFrameMetadata,
    TimeFrameMetadata,
)
from .opaque_data_handle import ChannelInfo, FlatChannelIterator, OpaqueDataHandle
from .storing_parameters import StoringParameters
from .working_store import WorkingStore

__all__ = [
    "ChunkingMode",
    "ChannelMetadata",
    "DescriptiveStatistics",
    "Metadata",
    "OriginalTimeFrameMetadata",
    "TimeFrameMetadata",
    "ChannelInfo",
    "FlatChannelIterator",
    "OpaqueDataHandle",
    "StoringParameters",
    "WorkingStore",
]
