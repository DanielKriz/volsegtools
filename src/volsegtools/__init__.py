"""
The highest level interface of the `volsegtools` library.

The user should always include this modules instead of importing other
internal (private) modules.
"""

from ._converter import (
    ConverterMap,
    MRCConverter,
)
from ._core import (
    LatticeKind,
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
    ChannelMetadata,
    DescriptiveStatistics,
    Metadata,
    OriginalTimeFrameMetadata,
    TimeFrameMetadata,
    ChannelInfo,
    FlatChannelIterator,
    OpaqueDataHandle,
    StoringParameters,
    WorkingStore,
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
    "ConverterMap",
    "MRCConverter",
    "LatticeKind",
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
