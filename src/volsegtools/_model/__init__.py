"""
Contains classes, functions and models related to the data that are used
through this project.

Please note that this module is private. Everything should be possible to
import from the `volsegtools` namespace.
"""

from .file_info import (
    ChannelInfo,
    FileInfo,
    MeshInfo,
)
from .metadata import (
    ChannelMetadata,
    DatasetMetadata,
    DescriptiveStatistics,
    MeshMetadata,
    TimeFrameMetadata,
)
from .pipeline_state import (
    PipelineContext,
    PipelineStageKind,
    PipelineState,
    PipelineStateManager,
)
from .storing_parameters import StoringParameters

__all__ = [
    "ChannelInfo",
    "ChannelMetadata",
    "DatasetMetadata",
    "DescriptiveStatistics",
    "FileInfo",
    "MeshInfo",
    "MeshMetadata",
    "PipelineContext",
    "PipelineStageKind",
    "PipelineState",
    "PipelineStateManager",
    "StoringParameters",
    "TimeFrameMetadata",
]
