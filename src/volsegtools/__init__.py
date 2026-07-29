"""
The highest level interface of the `volsegtools` library.

The user should always include this modules instead of importing other
internal (private) modules.
"""

# this makes it possible to use abbreviation for `volsegtools` and then using `abc`.
from . import abc
from ._bundling import (
    MVSXBundler,
    ResolutionZipBundler,
    ZipBundler,
)
from ._conversion import (
    CIFConverter,
    ConverterMap,
    ImarisConverter,
    MeshConverter,
    MRCConverter,
    NGFFConverter,
    NiiConverter,
    SFFConverter,
    TIFFConverter,
    UnsupportedCompressionError,
    VRMLConverter,
)
from ._core import (
    AxisValues,
    Bounds,
    Bytes,
    ChunkingMode,
    DataKind,
    Gaussian3DKernel,
    JSONTimerReporter,
    Timer,
    TimerReporter,
    UnitKind,
    WorkingStore,
    to_angstrom,
    to_bytes,
    to_micrometer,
    unit_from_str,
)
from ._downsampling import (
    AveragePooling,
    InterpolationBased,
    MaxPooling,
    MinPooling,
    NearestNeighbor,
    Null,
    PoolingDownsamplingStrategy,
    SeparatedSmoothing,
    Smoothing,
    StridedSmoothing,
    TricubicInterpolation,
    TrilinearInterpolation,
    TriquinticInterpolation,
)
from ._model import (
    ChannelInfo,
    DataSetInfo,
    DescriptiveStatistics,
    MeshInfo,
    StoringParameters,
    TimeFrameInfo,
)
from ._processing import (
    ErrorEvaluationMultiStep,
    ErrorEvaluationStep,
    JSONSizeReporter,
    ProcessingPipeline,
    ProcessingPipelineBuilder,
    SizeEvaluationStep,
    SmoothingStep,
    StdoutSizeReporter,
    create_builder,
)
from ._serialization import (
    BCIFSerializer,
    MeshSerializer,
    MRCSerializer,
    OBJSerializer,
    PLYSerializer,
    STLSerializer,
)
from ._storage import (
    Channel,
    DataHandle,
    DataSet,
    Mesh,
    TimeFrame,
    create_file_name,
    info_from_file_path,
)

__version__ = "0.2.2"

import logging

logger = logging.getLogger(__name__)

__all__ = [
    "AveragePooling",
    "AxisValues",
    "BCIFSerializer",
    "Bounds",
    "Bytes",
    "CIFConverter",
    "Channel",
    "ChannelInfo",
    "ChunkingMode",
    "ConverterMap",
    "DataHandle",
    "DataKind",
    "DataSet",
    "DataSetInfo",
    "DescriptiveStatistics",
    "ErrorEvaluationMultiStep",
    "ErrorEvaluationStep",
    "Gaussian3DKernel",
    "ImarisConverter",
    "InterpolationBased",
    "JSONSizeReporter",
    "JSONTimerReporter",
    "MRCConverter",
    "MRCSerializer",
    # From subpackages
    "MVSXBundler",
    "MaxPooling",
    "Mesh",
    "MeshConverter",
    "MeshInfo",
    "MeshSerializer",
    "MinPooling",
    "NGFFConverter",
    "NearestNeighbor",
    "NiiConverter",
    "Null",
    "OBJSerializer",
    "PLYSerializer",
    "PoolingDownsamplingStrategy",
    "ProcessingPipeline",
    "ProcessingPipelineBuilder",
    "ResolutionZipBundler",
    "SFFConverter",
    "STLSerializer",
    "SeparatedSmoothing",
    "SizeEvaluationStep",
    "Smoothing",
    "SmoothingStep",
    "StdoutSizeReporter",
    "StoringParameters",
    "StridedSmoothing",
    "TIFFConverter",
    "TimeFrame",
    "TimeFrameInfo",
    "Timer",
    "TimerReporter",
    "TricubicInterpolation",
    "TrilinearInterpolation",
    "TriquinticInterpolation",
    "UnitKind",
    "UnsupportedCompressionError",
    "VRMLConverter",
    "WorkingStore",
    "ZipBundler",
    # Built-in
    "__version__",
    # Namespace Shortcuts
    "abc",
    "create_builder",
    "create_file_name",
    "info_from_file_path",
    "logger",
    "to_angstrom",
    "to_bytes",
    "to_micrometer",
    "unit_from_str",
]
