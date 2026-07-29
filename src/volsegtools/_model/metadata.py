from pydantic import Field

import pydantic

from volsegtools._core import AxisValues, DataKind


class DataSetInfo(pydantic.BaseModel):
    filename: str = "Unknown File"
    resolution: int = -1
    axis_order: AxisValues = Field(default_factory=AxisValues)
    voxel_size: AxisValues = Field(default_factory=AxisValues)
    origin: AxisValues = Field(default_factory=AxisValues)
    id: str = "Unknown"
    kind: DataKind = DataKind.VOLUME
    lattice_shape: AxisValues = Field(default_factory=AxisValues)


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
