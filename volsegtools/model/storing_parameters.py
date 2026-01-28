import numpy as np
import numpy.typing
import pydantic
from zarr.abc.codec import BytesBytesCodec
from zarr.codecs import BloscCodec

from volsegtools.core import LatticeKind
from volsegtools.model.chunking_mode import ChunkingMode


class StoringParameters(pydantic.BaseModel):
    """Parameters used for storing a volume or a segmentation.

    Attributes
    ----------
    is_compression_enabled: bool, default: False
        Whether the compression is enabled.
    chunking_mode: ChunkingMode, default: ChunkingMode.AUTO
        Which chunking mode is used for this particular entry.
    storage_dtype: numpy.typing.DTypeLike, default: np.float64
        What is the type of data stored in this entry.
    resolution_level: pydantic.NonNegativeInt, default: 0
        Of which resolution level is this entry.
    time_frame: pydantic.NonNegativeInt, default: 0
        Which time frame is this entry.
    channel: pydantic.NonNegativeInt, default: 0
        Which channel is this entry.
    compressor: Codec, default: Blosc()
        Which compression codec is going to be used.
    """

    is_compression_enabled: bool = False
    chunking_mode: ChunkingMode = ChunkingMode.AUTO
    storage_dtype: numpy.typing.DTypeLike = np.float64
    resolution_level: pydantic.NonNegativeInt = 0
    time_frame: pydantic.NonNegativeInt = 0
    channel: pydantic.NonNegativeInt = 0
    compressor: BytesBytesCodec = BloscCodec()
    lattice_kind: LatticeKind = LatticeKind.VOLUME

    def __str__(self) -> str:
        return f"""Storing Paramaters:
        is_compression_enabled {self.is_compression_enabled}
        chunking_mode {self.chunking_mode}
        storage_dtype {self.storage_dtype}
        resolution_level {self.resolution_level}
        time_frame {self.time_frame}
        channel {self.channel}
        compressor {self.compressor}"""

    class Config:
        arbitrary_types_allowed = True
