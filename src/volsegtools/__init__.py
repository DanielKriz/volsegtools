"""
The highest level interface of the `volsegtools` library.

The user should always include this modules instead of importing other
internal (private) modules.
"""

from ._converter import MapConverter
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
from ._preprocessor import (
    Preprocessor,
    PreprocessorBuilder,
)
from ._serialization import BCIFSerializer


__version__ = "0.0.0"


__all__ = [
    "MapConverter",
    "LatticeKind",
    "Vector3",
    "Bounds",
    "Gaussian3DKernel",
    "DownsamplingParameters",
    "to_bytes",
    "BaseDownsampler",
    "HierarchyDownsampler",
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
    "Preprocessor",
    "PreprocessorBuilder",
    "BCIFSerializer",
    "__version__",
]
