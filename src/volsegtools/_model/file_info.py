from pathlib import Path
from typing import Annotated

import numpy as np
import pydantic

from volsegtools._core import AxisValues, AxisValuesAsInt, Bytes, Unit
from volsegtools._core.data_kind import SerializableDataKind

SerializablePath = Annotated[
    Path,
    pydantic.PlainSerializer(
        lambda path: str(path.resolve()),
        return_type=str,
    ),
]

SerializableDType = Annotated[
    np.dtype,
    pydantic.PlainSerializer(
        lambda dtype: dtype.name,
        return_type=str,
    ),
]

BytesAsMegaBytes = Annotated[
    Bytes,
    pydantic.PlainSerializer(
        lambda bytes: bytes / 1_000_000,
        return_type=float,
    ),
]


@pydantic.dataclasses.dataclass(
    frozen=True, slots=True, config=pydantic.ConfigDict(arbitrary_types_allowed=True)
)
class ChannelInfo:
    size_in_mb: BytesAsMegaBytes
    dimensions: AxisValuesAsInt
    origin: AxisValues
    cell_size: AxisValues
    units: Unit
    dtype: SerializableDType


@pydantic.dataclasses.dataclass(frozen=True, slots=True)
class MeshInfo:
    size_in_mb: BytesAsMegaBytes
    triangles: int


@pydantic.dataclasses.dataclass
class FileInfo:
    filepath: SerializablePath
    size_in_mb: BytesAsMegaBytes
    possible_kind: list[SerializableDataKind]
    frames: int
    data: list[ChannelInfo | MeshInfo]
