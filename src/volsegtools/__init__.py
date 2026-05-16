"""
The highest level interface of the `volsegtools` library.

The user should always include this modules instead of importing other
internal (private) modules.
"""

from._bundling import (
    MVSXBundler,
)
from ._converter import (
    ConverterMap,
    MRCConverter,
)
from ._core import (
    LatticeKind,
    DataKind,
    Vector3,
    Bounds,
    Gaussian3DKernel,
    DownsamplingParameters,
    to_bytes,
)
from ._downsampler import (
    BaseDownsampler,
    HierarchyDownsampler,
    HierarchyDownsamplingStrategy,
    NullDownsamplingStrategy,
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
)
from ._serialization import BCIFSerializer, MRCSerializer

# this makes it possible to use abbreviation for `volsegtools` and then using `abc`.
from . import abc

__version__ = "0.0.0"


__all__ = [
    # From subpackages
    "MVSXBundler",
    "ConverterMap",
    "MRCConverter",
    "LatticeKind",
    "DataKind",
    "Vector3",
    "Bounds",
    "Gaussian3DKernel",
    "DownsamplingParameters",
    "to_bytes",
    "BaseDownsampler",
    "HierarchyDownsampler",
    "HierarchyDownsamplingStrategy",
    "NullDownsamplingStrategy",
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
    "BCIFSerializer",
    "MRCSerializer",
    # Built-in
    "__version__",
    # Namespace Shortcuts
    "abc",
]
