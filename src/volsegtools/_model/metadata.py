from pydantic import Field

import pydantic

from volsegtools._core import DataKind, Vector3


class DataSetInfo(pydantic.BaseModel):
    filename: str = "Unknown File"
    resolution: int = -1
    axis_order: Vector3 = Field(default_factory=Vector3)
    voxel_size: Vector3 = Field(default_factory=Vector3)
    origin: Vector3 = Field(default_factory=Vector3)
    id: str = "Unknown"
    kind: DataKind = DataKind.VOLUME
    lattice_shape: Vector3 = Field(default_factory=Vector3)


class TimeFrameInfo(pydantic.BaseModel):
    id: int = -1


@pydantic.dataclasses.dataclass
class DescriptiveStatistics:
    """Represents statistics that should be collected for some data set for
    it to be representable in CIF.
    """

    mean: float = 0.0
    std: float = 0.0
    max: float = 0.0
    min: float = 0.0


class ChannelInfo(pydantic.BaseModel):
    id: int = -1
    statistics: DescriptiveStatistics = Field(default_factory=DescriptiveStatistics)


class MeshInfo(pydantic.BaseModel):
    id: int
