"""
The highest level interface of the `volsegtools` library.

The user should always include this modules instead of importing other
internal (private) modules.
"""

from ._bundling import (
    MVSXBundler,
)
from ._converter import (
    ConverterMap,
    MRCConverter,
    TIFFConverter,
    MeshConverter,
)
from ._core import (
    DataKind,
    Vector3,
    Bounds,
    Gaussian3DKernel,
    DownsamplingParameters,
    to_bytes,
    Timer,
    TimerReporter,
    JSONTimerReporter,
)
from ._downsampler import (
    HierarchyDownsamplingStrategy,
    NullDownsamplingStrategy,
    NearestNeighborDownsamplingStrategy,
    PoolingDownsamplingStrategy,
    AveragePoolingStrategy,
    MinPoolingStrategy,
    MaxPoolingStrategy,
    SeparableSmoothing,
    StridedSmoothing,
    InterpolationBased,
    TrilinearInterpolation,
    TricubicInterpolation,
    TriquinticInterpolation,
)
from ._model import (
    ChunkingMode,
    ComputationBackend,
    StoringParameters,
    WorkingStore,
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
from ._processing import (
    ProcessingPipeline,
    ProcessingPipelineBuilder,
    create_builder,
    SmoothingStep,
    ErrorEvaluationStep,
    ErrorEvaluationMultiStep,
    SizeEvaluationStep,
    JSONSizeReporter,
    StdoutSizeReporter,
)
from ._serialization import (
    BCIFSerializer,
    MRCSerializer,
    MeshSerializer,
    OBJSerializer,
    PLYSerializer,
    STLSerializer,
)

# this makes it possible to use abbreviation for `volsegtools` and then using `abc`.
from . import abc

__version__ = "0.0.0"

import logging

logger = logging.getLogger(__name__)

__all__ = [
    # From subpackages
    "MVSXBundler",
    "ConverterMap",
    "MRCConverter",
    "TIFFConverter",
    "MeshConverter",
    "MeshSerializer",
    "OBJSerializer",
    "PLYSerializer",
    "STLSerializer",
    "DataKind",
    "Vector3",
    "Bounds",
    "Gaussian3DKernel",
    "DownsamplingParameters",
    "to_bytes",
    "Timer",
    "TimerReporter",
    "JSONTimerReporter",
    "HierarchyDownsamplingStrategy",
    "NullDownsamplingStrategy",
    "NearestNeighborDownsamplingStrategy",
    "PoolingDownsamplingStrategy",
    "AveragePoolingStrategy",
    "MinPoolingStrategy",
    "MaxPoolingStrategy",
    "SeparableSmoothing",
    "StridedSmoothing",
    "InterpolationBased",
    "TrilinearInterpolation",
    "TricubicInterpolation",
    "TriquinticInterpolation",
    "ChunkingMode",
    "StoringParameters",
    "ComputationBackend",
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
    "ProcessingPipeline",
    "ProcessingPipelineBuilder",
    "create_builder",
    "SmoothingStep",
    "ErrorEvaluationStep",
    "ErrorEvaluationMultiStep",
    "SizeEvaluationStep",
    "JSONSizeReporter",
    "StdoutSizeReporter",
    "BCIFSerializer",
    "MRCSerializer",
    # Built-in
    "__version__",
    "logger",
    # Namespace Shortcuts
    "abc",
]
