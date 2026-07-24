"""
Contains classes, functions and models related to the data that are used
through this project.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .chunking_mode import ChunkingMode
from .storing_parameters import StoringParameters
from .working_store import WorkingStore
from .data_set import (
    DataSet,
    DataSetInfo,
    DescriptiveStatistics,
    Channel,
    ChannelInfo,
    Mesh,
    MeshInfo,
    TimeFrame,
    TimeFrameInfo,
    create_file_name,
    info_from_file_path,
)

__all__ = [
    "ChunkingMode",
    "StoringParameters",
    "WorkingStore",
    "DataSet",
    "DataSetInfo",
    "DescriptiveStatistics",
    "TimeFrame",
    "TimeFrameInfo",
    "Channel",
    "ChannelInfo",
    "Mesh",
    "MeshInfo",
    "create_file_name",
    "info_from_file_path",
]
