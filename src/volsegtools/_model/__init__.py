"""
Contains classes, functions and models related to the data that are used
through this project.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .storing_parameters import StoringParameters
from .metadata import (
    DataSetInfo,
    DescriptiveStatistics,
    ChannelInfo,
    MeshInfo,
    TimeFrameInfo,
)
from .data_set import (
    DataSet,
    Channel,
    Mesh,
    TimeFrame,
    create_file_name,
    info_from_file_path,
)
from .pipeline_state import (
    PipelineStageKind,
    PipelineState,
    PipelineStateManager,
)

__all__ = [
    "StoringParameters",
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
    "PipelineStageKind",
    "PipelineState",
    "PipelineStateManager",
]
