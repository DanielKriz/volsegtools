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
from .pipeline_state import (
    PipelineStageKind,
    PipelineState,
    PipelineStateManager,
    PipelineContext,
)

__all__ = [
    "StoringParameters",
    "DataSetInfo",
    "DescriptiveStatistics",
    "TimeFrameInfo",
    "ChannelInfo",
    "MeshInfo",
    "PipelineStageKind",
    "PipelineState",
    "PipelineStateManager",
    "PipelineContext",
]
